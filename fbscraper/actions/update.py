import time
import random
import logging

logger = logging.getLogger(__name__)
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException
from bs4 import BeautifulSoup
import re
from fbscraper.settings import (
    DEFAULT_IS_LOGINED,
    DEFAULT_MAX_TRY_TIMES,
    DEFAULT_SHOULD_LOAD_COMMENT,
    DEFAULT_SHOULD_TURN_OFF_COMMENT_FILTER,
    DEFAULT_NEXT_SNAPSHOT_AT_INTERVAL,
    STATUS_SUCCESS,
)
import fbscraper.facebook as fb


class UpdateCrawler:
    def __init__(
        self,
        article_url,
        article_id,
        db,
        browser,
        limit_sec,
        max_try_times=DEFAULT_MAX_TRY_TIMES,
        is_logined=DEFAULT_IS_LOGINED,
    ):
        self.article_url = article_url
        self.article_id = article_id
        self.db = db
        self.browser = browser
        self.post_selector = ".permalinkPost" if is_logined else ".userContentWrapper"
        self.post_node = None
        self.max_try_times = max_try_times
        self.is_logined = is_logined
        self.start_at = None
        self.limit_sec = limit_sec
        self.should_load_comment = DEFAULT_SHOULD_LOAD_COMMENT
        self.should_turn_off_comment_filter = DEFAULT_SHOULD_TURN_OFF_COMMENT_FILTER

    @staticmethod
    def log_crawler(depth, comment_loaders_total, clicked_count, empty_count):
        message = f"crawler: expanding comments at level #{depth}, found comment loader total is {comment_loaders_total}, has clicked loader count is {clicked_count}, empty response count #{empty_count} \n"
        logger.debug(message)

    def crawl_and_save(self):
        self.start_at = int(time.time())
        self.enter_site()

        is_located = self.locate_target_post()

        if is_located:
            try:
                self.expand_comment()
                should_relocate_for_loaded_comment = True

            except TimeoutException:
                # encountered LIVE video post: https://www.facebook.com/hsiweiC/posts/160025454961889
                # with this kind of message: [TimeoutException] , note: .userContentWrapper [data-testid="UFI2CommentsCount/root"]
                # normal video post is fine: https://www.facebook.com/hsiweiC/posts/173291537422199
                logger.warning(
                    "[post_crawler] maybe NO COMMENTS or failed to expand comment for LIVE VIDEO"
                )
                should_relocate_for_loaded_comment = False
                pass

            except Exception:
                # continue to save() without comment
                # sometimes failed to expand comment due to random slow browser condition
                logger.error(
                    "[post_crawler] failed to expand comment for unknown reason"
                )
                should_relocate_for_loaded_comment = False
                pass
        else:
            should_relocate_for_loaded_comment = False
            logger.debug(
                f"[post_crawler] Cannot locate target post with selector={self.post_selector}"
            )

        if should_relocate_for_loaded_comment:
            self.locate_target_post()

        # save html with relocated post node
        raw_html = (
            self.post_node and self.post_node.get_attribute("outerHTML")
            if self.post_node
            else self.get_post_raw_html(self.browser.page_source)
        )
        self.save(raw_html)

    def save(self, raw_html):
        now = int(time.time())
        self.snapshot_article(now, raw_html)
        self.log_pipeline(table="snapshot")
        self.refresh_article_snapshot_history(now, self.article_id)
        self.log_pipeline(table="article")

    def enter_site(self):
        self.browser.get(self.article_url)
        fb.raise_if_security_check(self.browser)

        success_status = (
            f'crawler: successful to enter site with url "{self.article_url}"'
        )
        logger.debug(success_status)

        if not self.is_logined:
            block_selector = "#headerArea"
            self.browser.execute_script(
                f"document.querySelector('{block_selector}') && document.querySelector('{block_selector}').remove()"
            )
            removed_block_text = f'crawler: removed block element for non-logined browsing with selector="{block_selector}" \n'
            logger.debug(removed_block_text)

    def locate_target_post(self):
        self.post_node = (
            self.browser.find_elements_by_css_selector(self.post_selector)[0]
            if len(self.browser.find_elements_by_css_selector(self.post_selector)) > 0
            else None
        )

        if not self.post_node:
            post_not_found = f'crawler: failed and article not found with selector "{self.post_selector}", article url is {self.article_url} \n'
            logger.debug(post_not_found)
            result = False
        else:
            post_is_found = f'crawler: success and article is located with selector "{self.post_selector}", article url is {self.article_url} \n'
            logger.debug(post_is_found)
            result = True

        return result

    def is_robot_check(self):
        # is_robot_url
        if re.match(".*/checkpoint.*", self.browser.current_url):
            result = True
        # is_forced_robot_verify
        elif len(self.browser.find_elements_by_css_selector("#captcha")) > 0:
            result = True
        else:
            result = False

        return result

    def is_login_check(self):
        # is_login_url
        if re.match(".*/login.*", self.browser.current_url):
            result = True
        # id of button with text: "忘記帳號？" but not the id for page of "稍後再說"
        # is_forced_login_verify
        elif len(self.browser.find_elements_by_css_selector("#login_link")) > 0:
            result = True
        else:
            result = False

        return result

    def expand_comment(self):
        if not self.post_node:
            return

        self.show_comment()

        if self.should_turn_off_comment_filter:
            self.turn_off_comment_filter()

        if self.should_load_comment:
            self.load_comment(0)
            self.load_comment(1)

    def show_comment(self):
        if not self.is_logined:
            display_comment_selector = (
                '.userContentWrapper [data-testid="UFI2CommentsCount/root"]'
            )
            fb.click_by_selector(driver=self.browser, selector=display_comment_selector)
            time.sleep(random.uniform(2, 3))

    def turn_off_comment_filter(self):
        filter_menu_link_selector = '[data-testid="UFI2ViewOptionsSelector/root"] [data-testid="UFI2ViewOptionsSelector/link"]'
        filter_menu_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"]'
        unfiltered_option_selector = '[data-testid="UFI2ViewOptionsSelector/menuRoot"] [data-ordering="RANKED_UNFILTERED"]'

        fb.click_by_selector(driver=self.browser, selector=filter_menu_link_selector)
        logger.debug(
            f'crawler: clicked comment filter button with selector="{filter_menu_link_selector}" \n'
        )
        fb.move_to_element_by_selector(
            driver=self.browser, selector=filter_menu_selector
        )
        logger.debug(
            f'crawler: comment filter menu is shown with selector="{filter_menu_selector}" \n'
        )
        fb.click_by_selector(driver=self.browser, selector=unfiltered_option_selector)
        logger.debug(
            f'crawler: clicked comment filter "RANKED_UNFILTERED" with selector="{unfiltered_option_selector}" \n'
        )

    def load_comment(self, depth):
        comment_expander_selector = '[data-testid="UFI2CommentsPagerRenderer/pager_depth_{}"]'.format(
            depth
        )
        clicked_count = 0
        empty_count = 0
        comment_loaders_total = 0
        self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)

        while (int(time.time()) - self.start_at) < self.limit_sec:
            comment_loaders = self.post_node.find_elements_by_css_selector(
                comment_expander_selector
            )
            comment_loaders_total = len(comment_loaders)
            is_clicked = False
            if comment_loaders_total > 0:
                try:
                    is_clicked = fb.click_by_selector(
                        driver=self.browser, selector=comment_expander_selector
                    )

                except MoveTargetOutOfBoundsException as e:
                    # https://www.facebook.com/photo.php?fbid=3321929767823884&set=p.3321929767823884&type=3&theater
                    dialog_close_button = self.browser.find_element_by_link_text("關閉")
                    dialog_close_button and dialog_close_button.click()

            if not is_clicked:
                empty_count += 1
            else:
                clicked_count += 1

            self.log_crawler(depth, comment_loaders_total, clicked_count, empty_count)
            time.sleep(random.uniform(2, 3))

        crawled_time = int(time.time()) - self.start_at
        time_status = f"[update.py - load_comment] LimitSec: {self.limit_sec}, Crawled: {crawled_time}. is_over_limit_sec={self.limit_sec < crawled_time}"
        logger.debug(time_status)

    @staticmethod
    def get_post_raw_html(page_source):
        soup = BeautifulSoup(page_source, "html.parser")

        if len(soup.select(".permalinkPost")) > 0:
            result = str(soup.select(".permalinkPost")[0])
        elif len(soup.select(".userContentWrapper")) > 0:
            result = str(soup.select(".userContentWrapper")[0])
        else:
            # return whole page's html if cannot locate post node
            # ex. failed for non-existing article: https://www.facebook.com/fuqidao168/posts/2466415456951685
            # ex. failed for some video post: https://www.facebook.com/znk168/posts/412649276099554
            result = page_source

        return result

    def snapshot_article(self, snapshot_at, raw_data):
        snapshot = dict()
        snapshot["snapshot_at"] = snapshot_at
        snapshot["raw_data"] = raw_data
        snapshot["article_id"] = self.article_id
        self.db.insert_article_snapshot(snapshot)

    def refresh_article_snapshot_history(self, snapshot_at, article_id):
        article = dict()
        original_article = self.db.get_article_by_id(article_id=article_id)

        article["article_id"] = article_id
        article["last_snapshot_at"] = snapshot_at
        article["next_snapshot_at"] = snapshot_at + DEFAULT_NEXT_SNAPSHOT_AT_INTERVAL
        article["snapshot_count"] = original_article["snapshot_count"] + 1
        if original_article["first_snapshot_at"] == 0:
            article["first_snapshot_at"] = snapshot_at
        else:
            article["first_snapshot_at"] = original_article["first_snapshot_at"]
        self.db.update_article(**article)

    def log_pipeline(self, table):
        result = None
        if table == "snapshot":
            result = f"[{STATUS_SUCCESS}] insert ArticleSnapshot #{self.article_id}"
        elif table == "article":
            result = f"[{STATUS_SUCCESS}] update Article #{self.article_id} after ArticleSnapshot inserted"
        timestamp = f"pipeline: {result} \n"
        logger.info(timestamp)
