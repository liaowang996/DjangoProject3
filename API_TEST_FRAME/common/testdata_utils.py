import os.path
import psutil
from pandas.io.sas.sas_constants import row_count_offset_multiplier

from common.excel_utils import ExcelUtils
from common import config
from common.sql_utils import SqlUtils
from samples.read_excel1 import excelUtils

current_path = os.path.dirname(__file__)
test_data_path = os.path.join(current_path, '..', config.CASE_DATA_PATH)




class TestdataUtils():
    def __init__(self,test_data_path=test_data_path):
        self.test_data_path = test_data_path
        self.test_data_sheet = ExcelUtils(test_data_path, 'Sheet1')
        self.test_data = self.test_data_sheet.get_sheet_data_by_dict()
        self.test_data_by_mysql = SqlUtils().get_mysql_test_case_info()

#对excel数据进行处理
    def __get_testcase_data_dict(self):
        testcase_dict = {}

        for row_data in self.test_data:
            if row_data['用例执行'] == '是':
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


    #case的行号，用于数据回写入excel，测试结果反写
    def get_row_num(self,case_id,case_step_name):
        for j in range(len(self.test_data)):
            if self.test_data[j]['测试用例编号'] == case_id and self.test_data[j]['测试用例步骤'] == case_step_name:
                break
        return j+1

    def get_result_id(self):
        for col_id in range(len(self.test_data_sheet.sheet.row(0))):
            if self.test_data_sheet.sheet.row(0)[col_id].value == '是否通过':
                break
        return col_id


    def write_result_to_excel(self,case_id,case_step_name,content='通过'):
        row_id = self.get_row_num(case_id, case_step_name)
        col_id = self.get_result_id()
        self.test_data_sheet.update_excel_data(row_id, col_id, content)
        # # 写入后关闭文件
        self.close_excel()

    # 新增关闭Excel文件的方法
    def close_excel(self):
        if hasattr(self.test_data_sheet, 'close'):
            self.test_data_sheet.close()
        else:
            # 如果ExcelUtils没有close方法，尝试其他释放资源的方式
            self.test_data_sheet = None

    def clear_result_from_excel(self):
        row_count = self.test_data_sheet.get_row_counts()
        col_id = self.get_result_id()
        self.test_data_sheet.clear_excel_colum(1,row_count,col_id)

if __name__ == '__main__':
    ExcelUtils.force_close_file(test_data_path)
    testdata = TestdataUtils()
    testdata.write_result_to_excel('case_01','step1','成功1111')
    # # print(testdata.get_row_num('case_01','step1'))
    # testdata.write_result_to_excel('case_01','step1','成功1111')