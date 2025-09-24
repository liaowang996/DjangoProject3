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
        """执行单条用例并生成报告"""
        logger.info(f"开始执行单条用例, case_step_id={self.case_step_id}")
        try:
            test_suite = self.get_test_suite()
            report_file = os.path.join(self.test_report_root,
                                     f"单条用例报告_{self.case_step_id}.html")
            logger.debug(f"测试报告将保存至: {report_file}")

            with open(report_file, 'wb') as fp:
                runner = HTMLTestReportCN.HTMLTestRunner(
                    stream=fp,
                    title=f'单条用例测试报告 - {self.case_step_id}',
                    tester='自动化测试'
                )
                result = runner.run(test_suite)

            return {
                'status': 'success',
                'report_file': report_file,
                'case_count': result.testsRun
            }
        except Exception as e:
            logger.error(f"单条用例执行失败: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': str(e)}