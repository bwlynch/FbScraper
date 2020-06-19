from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
import os

CHROMEDRIVER_BIN = os.getenv("CHROMEDRIVER_BIN")
DB_URL = os.getenv("DB_URL")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
FB_EMAIL = os.getenv("FB_EMAIL")
FB_PASSWORD = os.getenv("FB_PASSWORD")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOG_FORMAT = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOG_FILENAME = os.getenv(
    "LOG_FILENAME", datetime.now().strftime("%Y-%m-%dT%H:%M") + ".log"
)

SITE_DEFAULT_LIMIT_SEC = 60 * 30
POST_DEFAULT_LIMIT_SEC = 60 * 1

DEFAULT_BROWSER_TYPE = "Chrome"
DEFAULT_EXECUTABLE_PATH = CHROMEDRIVER_BIN
DISCOVER_ACTION = "discover"
UPDATE_ACTION = "update"
DISCOVER_DEFAULT_LIMIT_SEC = 60 * 60
UPDATE_DEFAULT_LIMIT_SEC = 60 * 10
GROUP_SITE_TYPE = "fb_public_group"
PAGE_SITE_TYPE = "fb_page"
DEFAULT_IS_LOGINED = False
DEFAULT_IS_HEADLESS = True
DEFAULT_MAX_AMOUNT_OF_ITEMS = 1
DEFAULT_CPU = 2
DEFAULT_N_AMOUNT_IN_A_CHUNK = 10
DEFAULT_BREAK_BETWEEN_PROCESS = 60 * 2
DEFAULT_MAX_AUTO_TIMES = 0
DEFAULT_MAX_TRY_TIMES = 10
STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"
DEFAULT_SHOULD_USE_ORIGINAL_URL = False
DEFAULT_NEXT_SNAPSHOT_AT_INTERVAL = 60 * 60 * 24 * 3
DEFAULT_SHOULD_LOAD_COMMENT = True
DEFAULT_SHOULD_TURN_OFF_COMMENT_FILTER = True
