import os
import sys
import unittest
from common.testdata_utils import TestdataUtils
from common import HTMLTestReportCN
from common.log_utils import logger

def init_logger():
    from common.log_utils import LogUtils
    return LogUtils(log_path=os.path.join(os.path.dirname(__file__), '../logs')).get_log()

class RunSingleCase:
    def __init__(self, case_step_id):
        global logger
        logger = init_logger()
        self.case_step_id = case_step_id
        self.test_report_root = os.path.join(os.path.dirname(__file__), '../test_reports')
        logger.debug(f"初始化RunSingleCase, case_step_id={case_step_id}")

    def get_test_suite(self):
        """获取单条用例测试套件"""
        logger.info(f"开始获取测试套件, case_step_id={self.case_step_id}")
        testdata_utils = TestdataUtils()
        case_info = testdata_utils.get_single_testcase(self.case_step_id)
        if not case_info:
            logger.error(f"未找到测试用例: {self.case_step_id}")
            raise ValueError(f"未找到测试用例: {self.case_step_id}")
        logger.debug(f"获取到用例信息: {case_info}")

        from api_testcase.api_test import generate_test_suite
        return generate_test_suite([case_info])

    def run(self):
        """执行单条用例并返回结果"""
        logger.info(f"开始执行单条用例, case_step_id={self.case_step_id}")
        try:
            test_suite = self.get_test_suite()
            runner = unittest.TextTestRunner()
            result = runner.run(test_suite)

            # 解析执行结果
            if result.wasSuccessful():
                return {
                    'status': 'success',
                    'case_id': self.case_step_id,
                    'passed': True,
                    'details': '测试用例执行通过'
                }
            else:
                return {
                    'status': 'fail',
                    'case_id': self.case_step_id,
                    'passed': False,
                    'details': result.failures[0][1] if result.failures else '未知错误'
                }
        except Exception as e:
            logger.error(f"单条用例执行失败: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'case_id': self.case_step_id,
                'passed': False,
                'details': str(e)
            }