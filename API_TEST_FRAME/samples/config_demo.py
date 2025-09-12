import os
import configparser

config_path = os.path.join(os.path.dirname(__file__), '..','conf/config.ini')

cfg = configparser.ConfigParser()
cfg.read(config_path,encoding='utf-8')
print(cfg.get('path', 'CASE_DATA_PATH'))