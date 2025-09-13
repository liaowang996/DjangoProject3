import unittest
import time,os
from common.HTMLTestRunner_PY3.HTMLTestRunner_PY3 import HTMLTestRunner
from common import config


def get_test_suite():
    discover = unittest.defaultTestLoader.discover(start_dir='./testcases',
                                                   pattern='*cases.py',
                                                   top_level_dir='./testcases'
                                                   )
    all_suite = unittest.TestSuite()
    all_suite.addTest(discover)
    return all_suite

now_time = time.strftime('%Y-%m-%d %H_%M_%S')
html_report = os.path.join(config.REPORT_PATH,now_time + 'report.html')
file = open(html_report, 'wb')
testsuite=get_test_suite()
html_runner=HTMLTestRunner(stream=file,
                           verbosity=2,
                           title='API_TEST_FRAME',
                           description='接口测试结果'
                           )
html_runner.run(testsuite)
file.close()

