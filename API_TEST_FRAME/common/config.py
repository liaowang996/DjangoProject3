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
CASE_PATH = configUtils.read_value('path','CASE_PATH')


###################邮件配置##############
SMTP_SERVER = configUtils.read_value('email','SMTP_SERVER')
SMTP_PORT = configUtils.read_value('email','SMTP_PORT')
SMTP_SENDER = configUtils.read_value('email','SMTP_SENDER')
SMTP_PASSWORD = configUtils.read_value('email','SMTP_PASSWORD')
SMTP_RECEIVER = configUtils.read_value('email','SMTP_RECEIVER')
SMTP_SUBJECT = configUtils.read_value('email','SMTP_SUBJECT')
SMTP_CC = configUtils.read_value('email','SMTP_CC')
if __name__ == '__main__':
    print(REPORT_PATH)
