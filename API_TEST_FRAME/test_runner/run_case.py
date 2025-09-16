

import os
import unittest
from common import config, HTMLTestReportCN
from common.email_utils import EmailUtils


current_path = os.path.dirname(__file__)
test_case_path = os.path.join(current_path, '..', config.CASE_PATH)
test_report_path = os.path.join(current_path, '..', config.REPORT_PATH)

# print(test_case_path,test_report_path)
class RunCase():
    def __init__(self):
        self.test_case_path = test_case_path
        self.test_report_path = test_report_path
        self.title = '接口自动化测试报告'
        self.description = '接口自动化测试报告'
        self.tester = '测试-Liaowang'

    def get_test_suite(self):
        discover = unittest.defaultTestLoader.discover(start_dir=self.test_case_path,
                                                       pattern = 'api_test.py',
                                                       top_level_dir=self.test_case_path)
        all_suite = unittest.TestSuite()
        all_suite.addTest(discover)
        return all_suite

    def run(self):
        report_dir = HTMLTestReportCN.ReportDirectory(self.test_report_path)
        report_dir.create_dir(self.title)
        report_file_path = HTMLTestReportCN.GlobalMsg.get_value('report_path')
        fp = open(report_file_path, 'wb')
        runner = HTMLTestReportCN.HTMLTestRunner(stream=fp,
                                                title=self.title,
                                                description=self.description,
                                                tester=self.tester)
        runner.run(self.get_test_suite())
        fp.close()
        return report_file_path


if __name__ == '__main__':
    html_path = RunCase().run()
    EmailUtils('接口自动化测试报告',html_path).send_email()
