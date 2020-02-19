from facebook import *
from settings import *

## 初始化爬蟲
fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, True)

DISCOVER_ACTION = 'discover'
UPDATE_ACTION = 'update'
GROUP_SITE_TYPE = 'fb_public_group'
PAGE_SITE_TYPE = 'fb_page'
DISCOVER_TIMEOUT = 60*60
UPDATE_TIMEOUT = 60*10
DEFAULT_IS_LOGINED = False
DEFAULT_IS_HEADLESS = True
DEFAULT_MAX_AMOUNT_OF_ITEMS = 1
DEFAULT_N_AMOUNT_IN_A_CHUNK = 1
