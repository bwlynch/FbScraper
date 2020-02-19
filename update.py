from tqdm import tqdm
import argparse
import os
import sys
import multiprocessing
multiprocessing.set_start_method('spawn', True)
from selenium.common.exceptions import NoSuchElementException
import threading
import random

# self-defined
from post_spider import PostSpider
from page_spider import PageSpider
from logger import Logger
from helper import helper, SelfDefinedError
import db_manager

DISCOVER_ACTION = 'discover'
UPDATE_ACTION = 'update'
GROUP_SITE_TYPE = 'fb_public_group'
PAGE_SITE_TYPE = 'fb_page'
DISCOVER_TIMEOUT = 60*60
UPDATE_TIMEOUT = 60*10

class Handler:
    def __init__(self, action, site_type, is_logined=False, timeout=60*60, is_headless=True, max_amount_of_items=1, n_amount_in_a_chunk=1):
        self.action = action
        self.site_type = site_type
        self.is_logined = is_logined
        self.timeout = timeout
        self.is_headless = is_headless
        self.max_amount_of_items = max_amount_of_items
        self.n_amount_in_a_chunk = n_amount_in_a_chunk
        

    def log_handler(self, logfile, description, parameters, result=None):
        timestamp = None
        if result is not None:
            timestamp = 'handler_timestamp_{}: {}, {}, result is {} \n'.format(helper.now(), description, parameters, result)
        else:
            timestamp = 'handler_timestamp_{}: {}, {} \n'.format(helper.now(), description, parameters)
        logfile.write(timestamp)

    def update_one(self, article, browser, logfile, is_group_site_type):
        article_id = article['article_id']
        article_url = article['url']
        ps = PostSpider(article_url, article_id, browser, logfile)
        ps.work()

    def discover_one(self, site, browser, logfile, is_group_site_type, max_try_times=None):
        site_url = site['url']
        site_id = site['site_id']
        existing_article_urls = db_manager.get_articles_by_site_id(site_id)
        should_use_original_url = is_group_site_type
        ps = PageSpider(site_url, site_id, browser, existing_article_urls, logfile, max_try_times, should_use_original_url)
        ps.work()

    def process_one(self, item, browser, logfile):
        is_group_site_type = True if self.site_type == GROUP_SITE_TYPE else False

        if self.action == DISCOVER_ACTION:
            self.discover_one(item, browser, logfile, is_group_site_type)
        elif self.action == UPDATE_ACTION:
            self.update_one(item, browser, logfile, is_group_site_type)

    def process_item(self, item, should_show_progress=True):
        errors = []
        pid = os.getpid()
        start_at = helper.now()

        fpath = '{}-{}_pid_{}_timestamp_{}.log'.format(self.action, self.site_type, pid, start_at)
        print(fpath)
        print(item)
        logfile = open(fpath, 'a', buffering=1)
        sys.stdout = logfile
        if not should_show_progress:
            sys.stderr = logfile
        logfile.write('[{}] -------- LAUNCH --------, {}-{} for item: {} \n'.format(start_at, self.action, self.site_type, item))

        from facebook import Facebook
        from settings import FB_EMAIL, FB_PASSWORD, CHROMEDRIVER_BIN

        fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, self.is_headless)
        fb.start(self.is_logined)
        browser = fb.driver

        error_note = 'file_path = {}, item = {}'.format(fpath, item)
        is_security_check = False
        try:
            self.process_one(item, browser, logfile)
        except SelfDefinedError as e:
            # encountered security check for robot or login
            is_security_check = True
            error_msg = '[{}] Encountered security check and failed to {}-{} for item, error: {} \n'.format(helper.now(), self.action, self.site_type, helper.print_error(e, error_note))
            errors.append(error_msg)
            logfile.write(error_msg)
        except Exception as e:
            error_msg = '[{}] Failed to {}-{} for item, error: {} \n'.format(helper.now(), self.action, self.site_type, helper.print_error(e, error_note))
            errors.append(error_msg)
            logfile.write(error_msg)
        
        try:
            browser.quit()
            logfile.write('[{}] Quit Browser, result is SUCCESS \n'.format(helper.now()))
        except Exception as e:
            error_msg = '[{}] Failed to Quit Browser, {} \n'.format(helper.now(), helper.print_error(e, browser.current_url))
            errors.append(error_msg)
            logfile.write(error_msg)

        end_at = helper.now()
        spent = end_at - start_at
        logfile.write('[{}] -------- FINISH --------, spent: {}, {}-{} for item: {} \n'.format(end_at, spent, self.action, self.site_type, item))
        logfile.close()
        
        response = {}
        response['errors'] = errors
        response['is_security_check'] = is_security_check
        response['url'] = item['url']
        return response

    def countdown(self, period, desc='Item Process Countdown'):
        with tqdm(desc=desc, total=period) as pbar:
            for i in range(period):
                helper.wait(1)
                pbar.update(1)

    def handle(self):
        items = []
        if self.action == UPDATE_ACTION and self.site_type == PAGE_SITE_TYPE:
            items = db_manager.get_articles_never_update()
        elif self.action == DISCOVER_ACTION:
            items = db_manager.get_sites_need_to_crawl(self.site_type)

        random.shuffle(items)
        items = items[:self.max_amount_of_items]
        item_tuples = helper.to_tuples(items)
        item_chunks = helper.divide_chunks(item_tuples, self.n_amount_in_a_chunk)

        desc = '{} {}'.format(self.action, self.site_type)
        with tqdm(desc=desc, total=len(items)) as pbar:
            for n_item in item_chunks:
                n_item_result = None
                
                countdown_process = multiprocessing.Process(target=self.countdown,args=(self.timeout,))
                countdown_process.start()

                with multiprocessing.Pool(processes=self.n_amount_in_a_chunk) as pool:
                    pool_result = pool.starmap_async(self.process_item, n_item)
                    try:
                        n_item_result = pool_result.get(timeout=self.timeout)
                        print(n_item_result)
                    except Exception as e:
                        helper.print_error(e)
                try:
                    countdown_process.terminate()
                except Exception as e:
                    helper.print_error(e)
                
                # facebook block the user for a while, so take a break
                try:
                    for a_item_result in n_item_result:
                        if a_item_result['is_security_check']:
                            msg = '[{}] Encountered security check in details: {}. \n'.format(helper.now(), a_item_result)
                            print(msg)
                            return
                except Exception as e:
                    helper.print_error(e)            

                pbar.update(self.n_amount_in_a_chunk)

def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-d', '--discover', action='store_true', help='save article urls for sites')
    argument_parser.add_argument('-u', '--update', action='store_true', help='save html for articles')    
    argument_parser.add_argument('-g', '--group', action='store_true', help='facebook group')
    argument_parser.add_argument('-p', '--page', action='store_true', help='facebook page')    
    argument_parser.add_argument('-t', '--timeout', action='store', help='timeout for a site discover or an article update')
    args = argument_parser.parse_args()

    action = None
    site_type = None
    timeout = None

    if args.discover:
        action = DISCOVER_ACTION
        timeout = DISCOVER_TIMEOUT
    elif args.update:
        action = UPDATE_ACTION
        timeout = UPDATE_TIMEOUT

    if args.group:
        site_type = GROUP_SITE_TYPE
    elif args.page:
        site_type = PAGE_SITE_TYPE

    if args.timeout:
        timeout = int(args.timeout)

    max_amount_of_items = 1000
    n_amount_in_a_chunk = 4
    is_headless = True
    is_logined = False
    main_handler = Handler(action, site_type, is_logined=is_logined, timeout=timeout, max_amount_of_items=max_amount_of_items, n_amount_in_a_chunk=n_amount_in_a_chunk, is_headless=is_headless)
    main_handler.handle()
    

if __name__ == '__main__':
    main()
