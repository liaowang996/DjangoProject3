import os.path
from common.excel_utils import ExcelUtils
from common import config


current_path = os.path.dirname(__file__)
test_data_path = os.path.join(current_path, '..', config.CASE_DATA_PATH)

class TestdataUtils():
    def __init__(self,test_data_path=test_data_path):
        self.test_data_path = test_data_path
        self.test_data = ExcelUtils(test_data_path, 'Sheet1').get_sheet_data_by_dict()

    def __get_testcase_data_dict(self):
        testcase_dict = {}
        for row_data in self.test_data:
            testcase_dict.setdefault(row_data['测试用例编号'],[]).append(row_data)
        return  testcase_dict

    def def_testcase_data_list(self):
        testcase_list = []
        for k, v in self.__get_testcase_data_dict().items():
            one_case_dict = {}
            one_case_dict['case_name'] = k
            one_case_dict['case_info'] = v
            testcase_list.append(one_case_dict)
        return testcase_list

if __name__ == '__main__':
    testdata = TestdataUtils()
    for i in testdata.def_testcase_data_list():
        print(i)