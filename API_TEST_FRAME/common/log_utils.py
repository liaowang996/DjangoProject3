
import os
from nb_log import LogManager
import config
import  time
current_path = os.path.dirname(__file__)
log_out_path = os.path.join(current_path, '..',config.LOG_PATH)


class LogUtils():
    def __init__(self,log_path=log_out_path):
        self.log_name = os.path.join(log_out_path, 'ApitTest_%s.log'%time.strftime('%Y_%m_%d') )
        self.logger = LogManager('ApitTest').get_logger_and_add_handlers(log_level_int=config.LOG_LEVEL,
                                                                     log_path=log_out_path,
                                                                     log_filename='ApitTest_%s.log'%time.strftime('%Y_%m_%d') )
        #控制台输出时间

    def get_log(self):
        return self.logger

logger= LogUtils().get_log()

if __name__ == '__main__':
    logger.info('中文')
    logger.info('this is info')
    logger.debug('this is debug')
    logger.warning('this is warning')
    logger.error('this is error')
    logger.critical('this is critical')
    logger.exception('this is exception')
