import os
from nb_log import LogManager
from common import config

current_path = os.path.dirname(__file__)
log_out_path = os.path.join(current_path, '..',config.LOG_PATH)
print(log_out_path)


logger = LogManager('ApiTestLog').get_logger_and_add_handlers(log_level_int= 0,
                                                             log_path=log_out_path,
                                                               log_filename='log_demo_nb.log')

#
# logger.info('this is info')
# logger.debug('this is debug')
# print('123123213')
# logger.warning('this is warning')
# logger.error('this is error')
# logger.critical('this is critical')
# logger.exception('this is exception')
# logger.log(10,'this is log')