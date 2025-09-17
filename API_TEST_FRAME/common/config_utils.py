
import configparser

class ConfigUtils():
    def __init__(self,config_path):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(config_path,encoding='utf-8')


    def read_value(self, section, key, default=None):
        """读取配置值，支持默认值"""
        try:
            return self.cfg.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def read_int(self, section, key, default=None):
        """读取整数类型的配置值"""
        value = self.read_value(section, key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def read_bool(self, section, key, default=None):
        """读取布尔类型的配置值"""
        value = self.read_value(section, key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')

