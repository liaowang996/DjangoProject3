import os
from common.config_utils import ConfigUtils
# from common.log_utils import logger

def load_config(env='test_env'):
    """
    加载配置（支持多环境切换，敏感配置从环境变量读取）
    :param env: 环境名称（对应config.ini中的section）
    :return: 配置字典
    """
    # 1. 处理配置文件路径（绝对路径）
    current_dir = os.path.dirname(__file__)
    # 原代码路径是common/config.py，对应config.ini在../config/config.ini
    config_abs_path = os.path.abspath(os.path.join(current_dir, '..', 'conf', 'config.ini'))

    # 2. 检查配置文件是否存在
    if not os.path.exists(config_abs_path):
        raise FileNotFoundError(f"配置文件不存在：{config_abs_path}")

    # 3. 初始化配置读取工具
    config_utils = ConfigUtils(config_abs_path)
    config_dict = {}

    # ------------------------------ 基础URL配置（支持多环境）------------------------------
    # 优先从环境变量读取，其次从配置文件读取，最后用默认值
    config_dict['URL'] = os.getenv('URL',
                                   config_utils.read_value(env, 'URL', default='http://192.168.1.4:3000')
                                   )
    config_dict['URL1'] = os.getenv('URL1',
                                    config_utils.read_value(env, 'URL1', default='https://api.weixin.qq.com')
                                    )
    # 添加请求超时配置
    config_dict['REQUEST_TIMEOUT'] = config_utils.read_int(env, 'REQUEST_TIMEOUT', default=10)

    # ------------------------------ 文件路径配置 ------------------------------
    def get_abs_path(section, key, default):
        """获取绝对路径"""
        rel_path = config_utils.read_value(section, key, default=default)
        return os.path.abspath(os.path.join(current_dir, '..', rel_path))

    config_dict['CASE_DATA_PATH'] = get_abs_path('path', 'CASE_DATA_PATH', 'test_data/test_demo.xls')
    config_dict['TEST_DATA'] = get_abs_path('path', 'TEST_DATA', 'test_data/')
    config_dict['LOG_PATH'] = get_abs_path('path', 'LOG_PATH', 'log/')
    config_dict['REPORT_PATH'] = get_abs_path('path', 'REPORT_PATH', 'tests_report/')
    config_dict['CASE_PATH'] = get_abs_path('path', 'CASE_PATH', 'api_testcase/')

    # ------------------------------ 日志配置 ------------------------------
    log_level_str = os.getenv('LOG_LEVEL', config_utils.read_value('log', 'LOG_LEVEL', default='20'))
    log_level_map = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
    if log_level_str.upper() in log_level_map:
        config_dict['LOG_LEVEL'] = log_level_map[log_level_str.upper()]
    else:
        try:
            config_dict['LOG_LEVEL'] = int(log_level_str)
        except ValueError:
            config_dict['LOG_LEVEL'] = 20
            # logger.warning(f"日志级别配置无效（{log_level_str}），默认设为INFO（20）")

    # ------------------------------ 邮件配置（敏感信息从环境变量读取）------------------------------
    config_dict['SMTP_SERVER'] = os.getenv('SMTP_SERVER',
                                           config_utils.read_value('email', 'SMTP_SERVER', default='smtp.qq.com')
                                           )
    config_dict['SMTP_PORT'] = config_utils.read_int('email', 'SMTP_PORT', default=465)
    config_dict['SMTP_SENDER'] = os.getenv('SMTP_SENDER',
                                           config_utils.read_value('email', 'SMTP_SENDER', default='sender@example.com')
                                           )
    # 邮件密码/授权码：优先从环境变量读取，避免明文存储
    config_dict['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD',
                                             config_utils.read_value('email', 'SMTP_PASSWORD', default='')
                                             )
    config_dict['SMTP_RECEIVER'] = os.getenv('SMTP_RECEIVER',
                                             config_utils.read_value('email', 'SMTP_RECEIVER',
                                                                     default='receiver@example.com')
                                             )
    config_dict['SMTP_SUBJECT'] = config_utils.read_value('email', 'SMTP_SUBJECT', default='接口测试报告')
    config_dict['SMTP_CC'] = config_utils.read_value('email', 'SMTP_CC', default='')

    # ------------------------------ MySQL配置（敏感信息从环境变量读取）------------------------------
    config_dict['MYSQL_DB_HOST'] = os.getenv('MYSQL_HOST',
                                             config_utils.read_value('mysql', 'MYSQL_DB_HOST', default='host.docker.internal')
                                             )
    config_dict['MYSQL_DB_PORT'] = config_utils.read_int('mysql', 'MYSQL_DB_PORT', default=3306)
    config_dict['MYSQL_DB_USER'] = os.getenv('MYSQL_USER',
                                             config_utils.read_value('mysql', 'MYSQL_DB_USER', default='root')
                                             )
    config_dict['MYSQL_DB_PASSWORD'] = os.getenv('MYSQL_PASSWORD',
                                                 config_utils.read_value('mysql', 'MYSQL_DB_PASSWORD', default='123456')
                                                 )
    config_dict['MYSQL_DB_DATABASE'] = os.getenv('MYSQL_DB',
                                                 config_utils.read_value('mysql', 'MYSQL_DB_DATABASE',
                                                                         default='api_test')
                                                 )
    config_dict['MYSQL_DB_CHARSET'] = config_utils.read_value('mysql', 'MYSQL_DB_CHARSET', default='utf8mb4')

    # 4. 确保目录存在
    for path_key in ['LOG_PATH', 'REPORT_PATH', 'CASE_PATH', 'TEST_DATA']:
        path = config_dict[path_key]
        if not os.path.exists(path):
            os.makedirs(path)
            # logger.info(f"目录不存在，已自动创建：{path}")

    return config_dict


# 初始化配置（默认测试环境，可通过环境变量指定ENV切换）
current_env = os.getenv('TEST_ENV', 'test_env')  # 环境变量TEST_ENV控制环境
CONFIG = load_config(current_env)

# 映射为全局变量（保持原有使用习惯）
URL = CONFIG['URL']
URL1 = CONFIG['URL1']
REQUEST_TIMEOUT = CONFIG['REQUEST_TIMEOUT']
CASE_DATA_PATH = CONFIG['CASE_DATA_PATH']
TEST_DATA = CONFIG['TEST_DATA']
LOG_PATH = CONFIG['LOG_PATH']
LOG_LEVEL = CONFIG['LOG_LEVEL']
REPORT_PATH = CONFIG['REPORT_PATH']
CASE_PATH = CONFIG['CASE_PATH']

# 邮件配置
SMTP_SERVER = CONFIG['SMTP_SERVER']
SMTP_PORT = CONFIG['SMTP_PORT']
SMTP_SENDER = CONFIG['SMTP_SENDER']
SMTP_PASSWORD = CONFIG['SMTP_PASSWORD']
SMTP_RECEIVER = CONFIG['SMTP_RECEIVER']
SMTP_SUBJECT = CONFIG['SMTP_SUBJECT']
SMTP_CC = CONFIG['SMTP_CC']

# MySQL配置
MYSQL_DB_HOST = CONFIG['MYSQL_DB_HOST']
MYSQL_DB_PORT = CONFIG['MYSQL_DB_PORT']
MYSQL_DB_USER = CONFIG['MYSQL_DB_USER']
MYSQL_DB_PASSWORD = CONFIG['MYSQL_DB_PASSWORD']
MYSQL_DB_DATABASE = CONFIG['MYSQL_DB_DATABASE']
MYSQL_DB_CHARSET = CONFIG['MYSQL_DB_CHARSET']

if __name__ == '__main__':
    # 测试配置加载
    print("=" * 50)
    print(f"当前环境: {current_env}")
    print(f"API主URL: {URL}")
    print(f"日志路径: {LOG_PATH}（级别: {LOG_LEVEL}）")
    print(f"MySQL地址: {MYSQL_DB_HOST}:{MYSQL_DB_PORT}（库: {MYSQL_DB_DATABASE}）")
    print("=" * 50)
