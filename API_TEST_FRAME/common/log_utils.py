
import os
import logging
import config
import  time
current_path = os.path.dirname(__file__)
log_out_path = os.path.join(current_path, '..',config.LOG_PATH)

class LogUtils():
    def __init__(self,log_path=log_out_path):
        self.log_name = os.path.join(log_out_path, 'ApitTest_%s.log'%time.strftime('%Y_%m_%d') )
        self.logger = logging.getLogger("ApiTestLog")
        self.logger.setLevel(config.LOG_LEVEL)
        #控制台输出时间
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(self.log_name,'a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        console_handler.close()
        file_handler.close()

    def get_log(self):
        return self.logger

logger= LogUtils().get_log()

if __name__ == '__main__':
    logger.info('中文')
