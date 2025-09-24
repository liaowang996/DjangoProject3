import warnings
import unittest
import logging

import paramunittest

from common.testdata_utils import TestdataUtils
from common.requests_utils import RequestsUtils
from common.log_utils import logger

# 获取测试用例数据
#case_infos = TestdataUtils().def_testcase_data_list()


# 可选：从MySQL获取测试数据
case_infos = TestdataUtils().def_testcase_data_list_by_mysql()

class APITestBase(unittest.TestCase):
    """API测试基类，封装通用功能"""

    def setUp(self) -> None:
        # 忽略资源警告
        warnings.simplefilter('ignore', ResourceWarning)
        logger.info(f"开始执行测试用例: {self._testMethodName}")

    def tearDown(self) -> None:
        logger.info(f"测试用例执行结束: {self._testMethodName}")


def generate_test_class(case_infos):
    """动态生成参数化测试类"""

    @paramunittest.parametrized(*case_infos)
    class APITest(APITestBase):
        def setParameters(self, case_id, case_info):
            """设置测试用例参数"""
            self.case_id = case_id
            self.case_info = case_info
            # 设置测试用例ID和名称
            self._testMethodName = f"test_{case_info[0].get('模块名称')}"+"_"+f"test_{case_info[0].get('测试用例编号')}"
            self._testMethodDoc = case_info[0].get('测试用例名称', '未命名测试用例')

        def test_api_request(self):
            """执行API测试并验证结果"""
            try:
                # 记录测试用例信息
                logger.info(f"执行测试用例: {self._testMethodDoc} (ID: {self.case_id})")

                # 发送请求并获取结果
                actual_result = RequestsUtils().request_by_step(self.case_info)

                # 验证结果
                logger.warning(actual_result)
                self.assertTrue(
                    actual_result.get('check_result'),
                    f"测试用例失败: {actual_result.get('message')}"
                )

                logger.info(f"测试用例 {self._testMethodName} 执行成功")

            except AssertionError as ae:
                logger.error(f"测试用例断言失败: {str(ae)}", exc_info=True)
                raise  # 重新抛出断言错误，让测试框架捕获
            except Exception as e:
                logger.error(f"测试用例执行出错: {str(e)}", exc_info=True)
                raise  # 重新抛出异常，让测试框架捕获


    return APITest


# 生成测试类
APITest = generate_test_class(case_infos)

if __name__ == '__main__':
    # 配置日志级别，确保测试过程可追踪
    logger.setLevel(logging.INFO)

    # 执行测试
    unittest.main(verbosity=2)