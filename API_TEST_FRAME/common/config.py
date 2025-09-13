import os
from common.config_utils import ConfigUtils

config_path = os.path.join(os.path.dirname(__file__), '..','conf/config.ini')

configUtils = ConfigUtils(config_path)
URL = configUtils.read_value('default','URL')
CASE_DATA_PATH = configUtils.read_value('path','CASE_DATA_PATH')
URL1 = configUtils.read_value('default','URL1')
LOG_PATH = configUtils.read_value('path','LOG_PATH')
LOG_LEVEL = int(configUtils.read_value('log','LOG_LEVEL'))
REPORT_PATH = configUtils.read_value('path','REPORT_PATH')