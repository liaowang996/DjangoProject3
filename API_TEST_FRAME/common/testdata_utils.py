import os.path
from common.excel_utils import ExcelUtils
from common import config
from common.sql_utils import SqlUtils

current_path = os.path.dirname(__file__)
test_data_path = os.path.join(current_path, '..', config.CASE_DATA_PATH)

class TestdataUtils():
    def __init__(self,test_data_path=test_data_path):
        self.test_data_path = test_data_path
        self.test_data = ExcelUtils(test_data_path, 'Sheet1').get_sheet_data_by_dict()
        self.test_data_by_mysql = SqlUtils().get_mysql_test_case_info()

#对excel数据进行处理
    def __get_testcase_data_dict(self):
        testcase_dict = {}
        for row_data in self.test_data:
            testcase_dict.setdefault(row_data['测试用例编号'],[]).append(row_data)
        return  testcase_dict

    def def_testcase_data_list(self):
        testcase_list = []
        for k, v in self.__get_testcase_data_dict().items():
            one_case_dict = {}
            one_case_dict['case_id'] = k
            one_case_dict['case_info'] = v
            testcase_list.append(one_case_dict)
        return tuple(testcase_list)


    # 对数据库数据进行处理
    def __get_testcase_data_dict_by_mysql(self):
        testcase_dict = {}
        for row_data in self.test_data_by_mysql:
            testcase_dict.setdefault(row_data['测试用例编号'],[]).append(row_data)
        return  testcase_dict

    def def_testcase_data_list_by_mysql(self):
        testcase_list = []
        for k, v in self.__get_testcase_data_dict_by_mysql().items():
            one_case_dict = {}
            one_case_dict['case_id'] = k
            one_case_dict['case_info'] = v
            testcase_list.append(one_case_dict)
        return tuple(testcase_list)

if __name__ == '__main__':
    testdata = TestdataUtils()
    for i in testdata.def_testcase_data_list_by_mysql():
        print(i)