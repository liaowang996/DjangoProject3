import os
from common.config_utils import ConfigUtils  # 假设 ConfigUtils 支持基础的配置读取


def load_config():
    """
    加载配置文件，统一处理路径、容错和类型转换
    :return: 配置字典（含所有读取的配置项）
    """
    # 1. 处理配置文件路径（转为绝对路径，避免运行路径影响）
    current_dir = os.path.dirname(__file__)
    config_relative_path = os.path.join(current_dir, '..', 'conf', 'config.ini')
    config_abs_path = config_relative_path

    # 2. 检查配置文件是否存在（避免 FileNotFoundError）
    if not os.path.exists(config_abs_path):
        raise FileNotFoundError(f"配置文件不存在：{config_abs_path}")

    # 3. 初始化 ConfigUtils 并读取配置（使用局部变量，避免全局占用）
    config_utils = ConfigUtils(config_abs_path)
    config_dict = {}

    # ------------------------------ 基础URL配置 ------------------------------
    # 容错：若键不存在，可设置默认值（如测试环境URL）
    config_dict['URL'] = config_utils.read_value('default', 'URL', default='http://test-api.example.com')
    config_dict['URL1'] = config_utils.read_value('default', 'URL1', default='http://test-api1.example.com')  # 可选配置

    # ------------------------------ 文件路径配置 ------------------------------
    # 路径统一转为绝对路径（避免相对路径混乱）
    case_data_rel = config_utils.read_value('path', 'CASE_DATA_PATH', default='test_data/test_cases.xls')
    config_dict['CASE_DATA_PATH'] = os.path.join(current_dir, '..', case_data_rel)

    test_data_rel = config_utils.read_value('path', 'TEST_DATA', default='test_data/')
    config_dict['TEST_DATA'] = os.path.join(current_dir, '..', test_data_rel)

    log_rel = config_utils.read_value('path', 'LOG_PATH', default='logs')
    config_dict['LOG_PATH'] = os.path.join(current_dir, '..', log_rel)

    report_rel = config_utils.read_value('path', 'REPORT_PATH', default='reports')
    config_dict['REPORT_PATH'] = os.path.join(current_dir, '..', report_rel)

    case_rel = config_utils.read_value('path', 'CASE_PATH', default='test_cases')
    config_dict['CASE_PATH'] = os.path.join(current_dir, '..', case_rel)

    # ------------------------------ 日志配置 ------------------------------
    # 容错：日志级别默认设为 INFO（20），支持配置值为数字或字符串（如 "20" 或 "INFO"）
    log_level_str = config_utils.read_value('log', 'LOG_LEVEL', default='20')
    log_level_map = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
    if log_level_str.upper() in log_level_map:
        config_dict['LOG_LEVEL'] = log_level_map[log_level_str.upper()]
    else:
        try:
            config_dict['LOG_LEVEL'] = int(log_level_str)
        except ValueError:
            config_dict['LOG_LEVEL'] = 20  # 默认 INFO 级别
            print(f"日志级别配置无效（{log_level_str}），已默认设为 INFO（20）")

    # ------------------------------ 邮件配置 ------------------------------
    # 邮件配置允许部分可选（如 CC 可空），用默认值避免 None
    config_dict['SMTP_SERVER'] = config_utils.read_value('email', 'SMTP_SERVER', default='smtp.qq.com')
    config_dict['SMTP_PORT'] = config_utils.read_int('email', 'SMTP_PORT', default=465)  # 优先用 read_int，容错默认值
    config_dict['SMTP_SENDER'] = config_utils.read_value('email', 'SMTP_SENDER', default='sender@example.com')
    config_dict['SMTP_PASSWORD'] = config_utils.read_value('email', 'SMTP_PASSWORD', default='')  # 密码不可默认，为空需用户补充
    config_dict['SMTP_RECEIVER'] = config_utils.read_value('email', 'SMTP_RECEIVER', default='receiver@example.com')
    config_dict['SMTP_SUBJECT'] = config_utils.read_value('email', 'SMTP_SUBJECT', default='接口测试报告')
    config_dict['SMTP_CC'] = config_utils.read_value('email', 'SMTP_CC', default='')  # 抄送可选，默认空

    # ------------------------------ MySQL配置 ------------------------------
    # MySQL 端口、字符集等有明确默认值，容错处理
    config_dict['MYSQL_DB_HOST'] = config_utils.read_value('mysql', 'MYSQL_DB_HOST', default='localhost')
    config_dict['MYSQL_DB_PORT'] = config_utils.read_int('mysql', 'MYSQL_DB_PORT', default=3306)
    config_dict['MYSQL_DB_USER'] = config_utils.read_value('mysql', 'MYSQL_DB_USER', default='root')
    config_dict['MYSQL_DB_PASSWORD'] = config_utils.read_value('mysql', 'MYSQL_DB_PASSWORD', default='123456')
    config_dict['MYSQL_DB_DATABASE'] = config_utils.read_value('mysql', 'MYSQL_DB_DATABASE', default='test_db')
    config_dict['MYSQL_DB_CHARSET'] = config_utils.read_value('mysql', 'MYSQL_DB_CHARSET', default='utf8mb4')

    # 4. 确保路径目录存在（避免后续写日志/报告时抛目录不存在错误）
    for path_key in ['LOG_PATH', 'REPORT_PATH', 'CASE_PATH']:
        path = config_dict[path_key]
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"目录不存在，已自动创建：{path}")

    return config_dict


# 加载配置（仅在模块导入时执行一次，避免重复加载）
CONFIG = load_config()

# 将配置项映射为全局变量（保持原有使用习惯，兼容旧代码）
URL = CONFIG['URL']
URL1 = CONFIG['URL1']
CASE_DATA_PATH = CONFIG['CASE_DATA_PATH']
TEST_DATA = CONFIG['TEST_DATA']
LOG_PATH = CONFIG['LOG_PATH']
LOG_LEVEL = CONFIG['LOG_LEVEL']
REPORT_PATH = CONFIG['REPORT_PATH']
CASE_PATH = CONFIG['CASE_PATH']

# 邮件配置全局变量
SMTP_SERVER = CONFIG['SMTP_SERVER']
SMTP_PORT = CONFIG['SMTP_PORT']
SMTP_SENDER = CONFIG['SMTP_SENDER']
SMTP_PASSWORD = CONFIG['SMTP_PASSWORD']
SMTP_RECEIVER = CONFIG['SMTP_RECEIVER']
SMTP_SUBJECT = CONFIG['SMTP_SUBJECT']
SMTP_CC = CONFIG['SMTP_CC']

# MySQL配置全局变量
MYSQL_DB_HOST = CONFIG['MYSQL_DB_HOST']
MYSQL_DB_PORT = CONFIG['MYSQL_DB_PORT']
MYSQL_DB_USER = CONFIG['MYSQL_DB_USER']
MYSQL_DB_PASSWORD = CONFIG['MYSQL_DB_PASSWORD']
MYSQL_DB_DATABASE = CONFIG['MYSQL_DB_DATABASE']
MYSQL_DB_CHARSET = CONFIG['MYSQL_DB_CHARSET']

if __name__ == '__main__':
    # 测试：打印关键配置，验证加载结果
    print("=" * 50)
    print("配置加载结果（关键项）：")
    print(f"接口主URL：{URL}")
    print(f"测试数据路径：{CASE_DATA_PATH}")
    print(f"日志路径：{LOG_PATH}（级别：{LOG_LEVEL}）")
    print(f"报告路径：{REPORT_PATH}")
    print(f"MySQL地址：{MYSQL_DB_HOST}:{MYSQL_DB_PORT}（库：{MYSQL_DB_DATABASE}）")
    print("=" * 50)