from datetime import datetime
import time
import random
import re
import traceback
import sys
import os
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import MoveTargetOutOfBoundsException

def has_file(fpath):
    try:
        return os.path.exists(fpath)
    except:
        return False

# n = How many elements each list should have 
def divide_chunks(l, n=10): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def print_error(e):
    error_class = e.__class__.__name__ #取得錯誤類型
    detail = e.args[0] #取得詳細內容
    cl, exc, tb = sys.exc_info() #取得Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
    fileName = lastCallStack[0] #取得發生的檔案名稱
    lineNum = lastCallStack[1] #取得發生的行號
    funcName = lastCallStack[2] #取得發生的函數名稱
    exceptionType = type(e)
    errMsg = "Exception of type {} occurred in file \"{}\", line {}, in {}: [{}] {}".format(exceptionType, fileName, lineNum, funcName, error_class, detail)
    sys.stderr.write(errMsg)
    return errMsg

def get_clean_url(url):
    host_url = 'https://www.facebook.com/'
    url_chunks = url.replace(host_url, '').split('?')
    if url_chunks[0] == 'profile.php':
        url.split('&')[0]
    else:
        return url.split('?')[0]

def click_without_move(selector, driver):
    try:
        ele = wait_element(selector, driver)
        ele.click()
    except Exception as e:
        print_error(e)    

def click(node, driver):
    try:
        ActionChains(driver).move_to_element(node).click(node).perform()
        return True
    except MoveTargetOutOfBoundsException as e:
        print_error(e)
        node.click()
        return True
    except Exception as e:
        print_error(e)
        return False

def now():
    return int(datetime.now().timestamp())


def wait(seconds=None):
    if not seconds:
        seconds = random.uniform(2, 3)
    time.sleep(seconds)


def data_testidify(selector):
    return '[data-testid="{}"]'.format(selector)


def get_count(text):
    try:
        return int(re.findall('\d+', text)[0])
    except:
        return 0


def get_text(node):
    try:
        return node.get_attribute('innerText')
    except:
        return ''


def get_html(node):
    try:
        return node.get_attribute('outerHTML')
    except:
        return ''


def get_element(node, selector):
    try:
        return node.find_element_by_css_selector(selector)
    except:
        return None


def wait_element(selector, driver, timeout=10):
    wait = WebDriverWait(driver, timeout=timeout)
    presence = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    return wait.until(presence)

def keyin_by_selector(selector, value, driver, timeout=10):
    ele = wait_element(selector, driver, timeout)
    ele.clear()
    ele.send_keys(value)
    driver.implicitly_wait(1)

def strip(string):
    """Helping function to remove all non alphanumeric characters"""
    words = string.split()
    words = [word for word in words if "#" not in word]
    string = " ".join(words)
    clean = ""
    for c in string:
        if str.isalnum(c) or (c in [" ", ".", ","]):
            clean += c
    return clean

def get_facebook_url_info(url):
    def get_post_id_and_type(_url):
        # post
        # https://www.facebook.com/gushi.tw/posts/2497783880459937?__xts__%5B0%5D=68.ARDbW5UsQAib2f6AhUSWlUd14puN0S3wDD0lu_HWiKphufxnWorDIS6auvPx2XP5IF4WYa6E9Io1Xh54QKrzasCfyz-YIhfjbsvn2fgKtdTj9pueZWA2rwcqP3lfojWzsbP3L7UIdF6QPwSunxcFXgfqDBWXGZGi0USmENBzljNwiAhXokTqCegr1c43ybrmHgTokEiEbeWCvQuG1TnR2HBfodeOKXhqO_v4N5jr9VFUq3X4xl2goQ90NesQloptFubcudH3XmdWEnvggbff8TjEEpEtFBqE7tEAqfYAjBs5vqekgZKFrrrU9ZYWo33LZqLi6d0&__tn__=-R0.g
        try:
            return { 'id': re.findall('\/posts\/(\w+)', _url)[0], 'type': 'post' }
        except Exception as e:
            pass

        # video
        # https://www.facebook.com/Wackyboys.Fans/videos/2452717014996864/?__xts__%5B0%5D=68.ARAvj4VDiok00FyWYH8Z6-CfMUuiKKlRIBfwnU6PmNEgcdDgBwP064gXAvQrk749Lk-G-eKK5cMLvuTvQtC3o3Q49y3btN7JDOb8CrsjxJB5FMNk7RPpmukw4N4HMmw94t3hH8_jmELHgcvd5YiHXFQcnvJ6OEqECZq_iL6ObarfUDnoUVAfo1SfVJzGg_ucWX5XzXFIkoCEjcEVs-zNOh4Vm4wtjngaKFyCvEvdh4C44l9DU5PHbHY0Z1WbGmoPvMA-zc5g8KqxfVXFMCNoab5FJ5zT9pWETZb9OVfe9wkWYBDXdsIVyhgMTiSdlfnIv_7ntDuyyepTzK7M&__tn__=-R
        try:
            return { 'id': re.findall('\/videos\/(\w+)', _url)[0], 'type': 'video' }
        except Exception as e:
            pass        

        # photo
        # https://www.facebook.com/121570255108696/photos/a.123441864921535/539538693311848/?type=3&__xts__%5B0%5D=68.ARA6rYVIdTFoURfgtAk7MYP31YGVtprQD3XebhVwZrQJsFLn9p8IrndnWNqM20mN8uI4qJMJIlccHtAaPX3RfJWq73MaykNjGwTTuSEl48j8SDJ-sQtDzwhC7z5LRrWvtN4tdS1_4hZRXaRUxjgP7u6Vs-N8C7eRkwKBzZJ6jS16M1bru4QiXc3NlBHnx1QgrDMpsb7xVr5eZuZoaqVRisFkDMRymGkkmoZ_xbSUZXXTz-jhJQ2SSGeHHyMFl5eQqpVZYexFkylhdwSL4LBXZyQC1vCc6b7MGZ3dXz08OsSebylqdxNUFlTZgg4hpiktqCWc8UAkqXl7YzVxndTX2E8&__tn__=-R
        try:
            return { 'id': re.findall('\/photos\/.*\/(\w+)', _url)[0], 'type': 'photo' }
        except Exception as e:
            pass

        # story_fbid
        # https://www.facebook.com/permalink.php?story_fbid=636096237164329&id=185537762220181&__xts__%5B0%5D=68.ARDXxSWoo2rCRDwjx5S1lYqEcEfvBMn1UTxm5NhakAusCUlvWei7dO7PwFhzAiit3Whq7RrG5MT7R2dgrTVfZ1fZSK3bOF5VzuM5SzsV5c0O1QKfCEVEcnnH7_auDpVO6vAhUQqyWl1tpc87-S2r18n0tY3hHFgKo5jt3Bt-stjPxqUYnpgrvj_Olu0bhuoE7Lfu28jonlluTpEmqjmoI2l5RXDsdHiyCpgarTpO-VosE6UiYHQYlkWlCpjVrSk5EL1cddjfs_suqFtKzhI4zd607DOsUCEbnJqxrjN5JWU_g-tWE2O0bTUh4tTeQTIt3OrvuM1IFzUNNaX6UsLuZImCiPJ7pvO4XACaF8o7h1w9xzpT-NYlc2ux9Klk-JDjAaZJyfUBYGGkMxXnZouXovKMgbk_vqt1tm0Hh_kVSKKjfI6HXkB_osuy26i3gW85HTifiFZCd2vIk-pNIk7JL59b6LI0DjvRztbMNUhhQDnlf3IGrIY&__tn__=-R
        # https://www.facebook.com/permalink.php?story_fbid=539530269979357&id=121570255108696
        try:
            return { 'id': re.findall('story_fbid\=(\d+?)\D', _url)[0], 'type': 'story_fbid' }
        except Exception as e:
            print_error(e)
            return None
    def parse_common_type(_url, _type):
        # for normal post, video, photo
        try:
            u = _url if _url.endswith('/') else _url+'/'
            r = 'facebook.com\/(.*?)\/'
            m = re.findall(r, u)

            if len(m) == 0:
                if u.startswith('/'):
                    r = '\/(.+?)\/{}s'.format(_type)
                else:
                    r = '(.+?)\/{}s'.format(_type)
                m = re.findall(r, u)

            return m[0]
        except Exception as e:
            print_error(e)
            return None
    def parse_story_fbid(_url, _type):
        # for story_fbid (aka. https://www.facebook.com/permalink.php?story_fbid=636095870497699&id=185537762220181&__xts__%5B0%5D=68.ARCf_eRqNCjMHCrF1FpzArZumj35pO8phq9MYa8nTLqK9QsoboTD-EOTPFn_mFHto8H7O5ZJbcpGOek-9fi3s_TmxAuuai9GL1vBvNFnYp9niSdU3oDKRrt-HoYoogWDMbUcSt07miwVMcKiscOErEhQxNw4C8bN_pTJB-F_dRQwT1vjOApIZdAgUtlvJ_PxKcLrQa6ZuYCr_MVMdr2j2tlHXXe1bYOdYy-PlxJFdkwS4xyeJbZI6s16EuQ7Ityyz8j7rHoFgj028kQi0ckU77ioWVqbvbqrMRzfEVRmWUGepvI-Wj0sMcFo2XvuZjhUSH7C666eyLP3LetXW1wRQmYqBP2RNGnpawPtt8IgSc8dTmn64XNZw3Q91Rb9kC-9ZabNRTuzUuB4Mec9ANoOVoafbQVC5Yj-ATIac0BJ4dsSFO2KAzHNuVirEpkNb2UmaTxBX4noPXN2Yw3pjF4X-hiWlJrkwQRhI9uFmDHKGzP1ncHeuy_dDQ&__tn__=-R)
        try:
            return re.findall('\Wid\=(\d+)', _url)[0]
        except Exception as e:
            print_error(e)
            return None
    def get_permalink(_url_info):
        # all types of post can accessed by https://www.facebook.com/{page_id}/posts/{post_id}
        return 'https://www.facebook.com/{page_id}/posts/{post_id}'.format(**_url_info)

    switcher = {
        'post': parse_common_type,
        'video': parse_common_type,
        'photo': parse_common_type,
        'story_fbid': parse_story_fbid,
    }

    post_info = get_post_id_and_type(url)
    url_type = post_info['type']
    parse_url_root_id_func = switcher.get(url_type, lambda : None)

    url_info = {}
    url_info['page_id'] = parse_url_root_id_func(url, url_type)
    url_info['post_id'] = post_info['id']
    url_info['permalink'] = get_permalink(url_info)
    url_info['type'] = post_info['type']
    url_info['original_url'] = url
    
    return url_info
    
def main():
    po_url = 'https://www.facebook.com/almondbrother/posts/3031431170223940?__xts__%5B0%5D=68.ARB4uuLJzs_P4-S_XrvvsCwnv36pUISC5a99w6mC7k12e9zkJeMXyES-_-w_18xFtfnRL5StvmxI_qcTpa8N0BTK96pbRVUegaTZNhkp1i7Hzxtb98kqQBAZEJ03hqzGVU2iSsi7Wy-oP2ir8OfviiaJikCxGNN1-n8q7mQU7c_swKNYtgDMf_qCQqFuVNoxiGiwmlWIzFdCqmaSXD8hGswf8faVGR9Kxw3tSmKLcjTFEm-lygXT1qdauuO5jfQKURS798h7YO3ONmvm3cWKhogsBVNCu1Dp3c01CraTiAMdBg1yMZbouncCy_XZQeRVJfKiWiX_NYEpHlk8WA6gBoLNaa40&__tn__=-R'
    v_url = 'https://www.facebook.com/185537762220181/videos/2426555417632575/?__xts__%5B0%5D=68.ARB-CsV3myg-YhVnQMISQUtWCb1OKkAj9ZOHixGX49YAwEs3RBMpLmuiTXW3Dp1eyEmaJM95SIkCnlM-9Pg5F1BGaroLycIeRK4T8CwJYgs5dGj2xxvZ9OcqrVl8AgziPPFFEzsjjHzgTClO28MNRgR_blqZI3N-G6S-QhZ2OhGZvQn65pgmK5rbRjb4nbm7721pUZDAqGXMOrxHf9tv5wWpQcKhidzpwodCFmL2AYatnBfyv56hZbZ6zNv5zdv03IXjoeTzW7ZqwP9CVL-hlMlcmVhpr99E4GYdz4d3tRqMxRLEZSVuG-aUtmV2G2ACUig9XSkaAWoe8zYzWFVPCnloXV1RVSicccA&__tn__=-R'
    ph_url = 'https://www.facebook.com/Wackyboys.Fans/photos/a.393130864073315/2608708485848864/?type=3&__xts__%5B0%5D=68.ARAfyz236qxprIn2nIBDPHiajithT7nfYrgArqW4IJ0iDzuuw6Pq0tn5vi16KQJjzjRXIA2QAe92bdAScQ7rvfIof1pwjA-zo_5mU9g8AJ56e3iGgJbJMUGTH3YOZlid41rSKXcqGM8O2NGtXexJY6RTR6z79no9b_0SDke6roAklrbQkUjFc_mMPLE3onZjWLV2mdVuXYgg3IeB06TJaO8hYomlzAJeO47FgWldqIHKHq39OFiSnip4QkI6A84HT-4hhQWksKmoez0UL-VxEXsivqxC8w2IB5wxMMLd8cssI6PQKFnXGC1PxM7VZxilaayr9FoLvN1ZH4AktqzrlE3KJg&__tn__=-R'
    s_url = 'https://www.facebook.com/permalink.php?story_fbid=636095870497699&id=185537762220181&__xts__%5B0%5D=68.ARCf_eRqNCjMHCrF1FpzArZumj35pO8phq9MYa8nTLqK9QsoboTD-EOTPFn_mFHto8H7O5ZJbcpGOek-9fi3s_TmxAuuai9GL1vBvNFnYp9niSdU3oDKRrt-HoYoogWDMbUcSt07miwVMcKiscOErEhQxNw4C8bN_pTJB-F_dRQwT1vjOApIZdAgUtlvJ_PxKcLrQa6ZuYCr_MVMdr2j2tlHXXe1bYOdYy-PlxJFdkwS4xyeJbZI6s16EuQ7Ityyz8j7rHoFgj028kQi0ckU77ioWVqbvbqrMRzfEVRmWUGepvI-Wj0sMcFo2XvuZjhUSH7C666eyLP3LetXW1wRQmYqBP2RNGnpawPtt8IgSc8dTmn64XNZw3Q91Rb9kC-9ZabNRTuzUuB4Mec9ANoOVoafbQVC5Yj-ATIac0BJ4dsSFO2KAzHNuVirEpkNb2UmaTxBX4noPXN2Yw3pjF4X-hiWlJrkwQRhI9uFmDHKGzP1ncHeuy_dDQ&__tn__=-R'
    ph_href = '/Wackyboys.Fans/photos/a.393130864073315/2608708485848864/?type=3&__xts__%5B0%5D=68.ARAfyz236qxprIn2nIBDPHiajithT7nfYrgArqW4IJ0iDzuuw6Pq0tn5vi16KQJjzjRXIA2QAe92bdAScQ7rvfIof1pwjA-zo_5mU9g8AJ56e3iGgJbJMUGTH3YOZlid41rSKXcqGM8O2NGtXexJY6RTR6z79no9b_0SDke6roAklrbQkUjFc_mMPLE3onZjWLV2mdVuXYgg3IeB06TJaO8hYomlzAJeO47FgWldqIHKHq39OFiSnip4QkI6A84HT-4hhQWksKmoez0UL-VxEXsivqxC8w2IB5wxMMLd8cssI6PQKFnXGC1PxM7VZxilaayr9FoLvN1ZH4AktqzrlE3KJg&__tn__=-R'
    s_href = 'permalink.php?story_fbid=636095870497699&id=185537762220181&__xts__%5B0%5D=68.ARCf_eRqNCjMHCrF1FpzArZumj35pO8phq9MYa8nTLqK9QsoboTD-EOTPFn_mFHto8H7O5ZJbcpGOek-9fi3s_TmxAuuai9GL1vBvNFnYp9niSdU3oDKRrt-HoYoogWDMbUcSt07miwVMcKiscOErEhQxNw4C8bN_pTJB-F_dRQwT1vjOApIZdAgUtlvJ_PxKcLrQa6ZuYCr_MVMdr2j2tlHXXe1bYOdYy-PlxJFdkwS4xyeJbZI6s16EuQ7Ityyz8j7rHoFgj028kQi0ckU77ioWVqbvbqrMRzfEVRmWUGepvI-Wj0sMcFo2XvuZjhUSH7C666eyLP3LetXW1wRQmYqBP2RNGnpawPtt8IgSc8dTmn64XNZw3Q91Rb9kC-9ZabNRTuzUuB4Mec9ANoOVoafbQVC5Yj-ATIac0BJ4dsSFO2KAzHNuVirEpkNb2UmaTxBX4noPXN2Yw3pjF4X-hiWlJrkwQRhI9uFmDHKGzP1ncHeuy_dDQ&__tn__=-R'
    s2_href = '/permalink.php?story_fbid=2617587964946262&id=1100522356652838'

    po_info = get_facebook_url_info(po_url)
    v_info = get_facebook_url_info(v_url)
    ph_info = get_facebook_url_info(ph_url)
    s_info = get_facebook_url_info(s_url)
    ph_href_info = get_facebook_url_info(ph_href)
    s_href_info = get_facebook_url_info(s_href)
    s2_href_info = get_facebook_url_info(s2_href)

    # site_url_1 = 'https://www.facebook.com/%E5%A4%A9%E5%8D%97%E5%9C%B0%E5%8C%97-1063653903655415/'
    # site_url_2 = 'https://www.facebook.com/jesusSavesF13/'
    # site_url_3 = 'https://www.facebook.com/%E5%BC%B7%E5%BC%B7%E6%BB%BE%E5%A4%A7%E5%93%A5-%E9%98%BF%E8%AA%8C-1088027454701943/?__tn__=%2Cd%2CP-R&eid=ARBiDxJohZf5_icvMw2BXVNG2nHG4VR9b_ArA_Tc6PfA98MtdnGw1xVKWvIdE-X1wfSteOnhr6PxVDUX'
    # site_url_4 = 'https://www.facebook.com/inability.dpp/'

    # site_url_1_info = get_facebook_url_info(site_url_1)
    # site_url_2_info = get_facebook_url_info(site_url_2)
    # site_url_3_info = get_facebook_url_info(site_url_3)
    # site_url_4_info = get_facebook_url_info(site_url_4)

    print('hold')

if __name__ == "__main__":
    main()