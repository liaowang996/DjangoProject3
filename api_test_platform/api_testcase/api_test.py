import warnings
import unittest
import logging
from common.testdata_utils import TestdataUtils
from common.requests_utils import RequestsUtils
from common.log_utils import logger

class APITestBase(unittest.TestCase):
    """API测试基类"""
    def setUp(self):
        warnings.simplefilter('ignore', ResourceWarning)
        logger.info(f"开始执行测试用例: {self._testMethodName}")

    def tearDown(self):
        logger.info(f"测试用例执行结束: {self._testMethodName}")

def generate_test_suite(case_infos):
    """生成测试套件"""
    test_suite = unittest.TestSuite()

    if not case_infos:
        logger.warning("未提供任何用例信息")
        return test_suite

    for case in case_infos:
        if not validate_case_data(case):
            logger.error(f"用例数据验证失败: {case.get('case_id', 'unknown')}")
            continue

        try:
            test_case = APITest(case_id=case['case_id'],
                              case_info=case['case_info'])
            if not hasattr(test_case, '_testMethodName'):
                logger.error(f"测试用例初始化失败: {case['case_id']}")
                continue

            test_suite.addTest(test_case)
        except Exception as e:
            logger.error(f"创建测试用例失败: {case['case_id']}, 错误: {str(e)}")
            continue

    if test_suite.countTestCases() == 0:
        logger.error("未生成任何有效测试用例")

    return test_suite

def validate_case_data(case):
    """验证用例数据格式"""
    required_fields = ['case_id', 'case_info']
    if not all(field in case for field in required_fields):
        logger.error(f"用例缺少必要字段: {case.keys()}")
        return False

    if not isinstance(case['case_info'], list):
        logger.error(f"case_info必须为列表: {type(case['case_info'])}")
        return False

    return True

class APITest(APITestBase):
    """动态生成的测试类"""
    def __init__(self, methodName='runTest', case_id=None, case_info=None):
        super().__init__(methodName)
        self.case_id = case_id
        self.case_info = case_info
        self._init_test_metadata()
        # 动态添加测试方法
        setattr(self.__class__, self._testMethodName, lambda x: x._execute_test_case())

    def _init_test_metadata(self):
        """初始化测试元数据"""
        try:
            first_step = self.case_info[0]
            self._testMethodName = f"test_{first_step.get('模块名称','unknown')}_{first_step.get('测试用例编号','0')}"
            self._testMethodDoc = first_step.get('测试用例名称', '未命名测试用例')
        except Exception as e:
            logger.error(f"初始化测试元数据失败: {str(e)}")
            self._testMethodName = f"test_case_{self.case_id}"
            self._testMethodDoc = f"测试用例 (ID: {self.case_id})"

    def runTest(self):
        """统一执行入口"""
        try:
            getattr(self, self._testMethodName)(self)
        except Exception as e:
            logger.error(f"测试执行异常: {str(e)}")
            raise

    def _execute_test_case(self):
        """实际执行测试用例"""
        result = RequestsUtils().request_by_step(self.case_info)
        self.assertTrue(
            result.get('check_result', False),
            result.get('message', '测试用例失败')
        )

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    unittest.main(verbosity=2)