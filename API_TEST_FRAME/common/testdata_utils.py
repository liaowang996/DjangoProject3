import os.path
import psutil
from common.log_utils import logger
from common.excel_utils import ExcelUtils
from common import config
from common.sql_utils import SqlUtils

# 1. 统一路径格式（绝对路径 + 斜杠统一）
current_path = os.path.dirname(__file__)
test_data_path = os.path.abspath(os.path.join(current_path, '..', config.CASE_DATA_PATH))

# 2. 强制关闭占用文件的进程（全局方法）
def force_close_file(file_path):
    file_path = os.path.abspath(file_path)
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            for file in proc.info['open_files'] or []:
                if os.path.abspath(file.path) == file_path:
                    print(f"强制关闭占用进程：{proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=2)
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

class TestdataUtils():
    def __init__(self, test_data_path=test_data_path):
        # 初始化前先释放文件占用
        force_close_file(test_data_path)
        self.test_data_path = test_data_path
        self.test_data_sheet = ExcelUtils(test_data_path, 'Sheet1')
        self.test_data = self.test_data_sheet.read_multiple_excel_cases()
        self.test_data_by_mysql = SqlUtils().get_mysql_test_case_info()

    # 处理 Excel 数据（只筛选“用例执行=是”的用例）
    def __get_testcase_data_dict(self):
        testcase_dict = {}
        for row_data in self.test_data:
            if row_data['用例执行'] == '是':
                testcase_dict.setdefault(row_data['模块名称']+'_'+row_data['测试用例编号'], []).append(row_data)

        logger.info(testcase_dict)
        return testcase_dict

    def def_testcase_data_list(self):
        testcase_list = []
        for case_id, case_info in self.__get_testcase_data_dict().items():
            testcase_list.append({'case_id': case_id, 'case_info': case_info})
        logger.info(testcase_list)
        return tuple(testcase_list)

    # 处理数据库数据
    def __get_testcase_data_dict_by_mysql(self):
        testcase_dict = {}
        for row_data in self.test_data_by_mysql:
            testcase_dict.setdefault(row_data['模块名称']+'_'+row_data['测试用例编号'], []).append(row_data)
        return testcase_dict

    def def_testcase_data_list_by_mysql(self):
        testcase_list = []
        for case_id, case_info in self.__get_testcase_data_dict_by_mysql().items():
            testcase_list.append({'case_id': case_id, 'case_info': case_info})
        return tuple(testcase_list)

    # 获取用例行号（带错误判断）
    # def get_row_num(self, case_id, case_step_name):
    #     for j in range(len(self.test_data)):
    #         if self.test_data[j]['测试用例编号'] == case_id and self.test_data[j]['测试用例步骤'] == case_step_name:
    #             return j + 1  # 假设 Excel 行号从 1 开始
    #     raise ValueError(f"未找到用例：case_id={case_id}, case_step_name={case_step_name}")

    # 获取“是否通过”列的列号
    # def get_result_id(self):
    #     for col_id in range(len(self.test_data_sheet.sheet.row(0))):
    #         if self.test_data_sheet.sheet.row(0)[col_id].value == '是否通过':
    #             return col_id  # 注意：列号是否从 0 开始，需与 ExcelUtils 保持一致
    #     raise ValueError("Excel 中未找到'是否通过'列")

    # 写入测试结果并关闭文件
    # def write_result_to_excel(self, case_id, case_step_name, content='通过'):
    #     row_id = self.get_row_num(case_id, case_step_name)
    #     col_id = self.get_result_id()
    #     self.test_data_sheet.update_excel_data(row_id, col_id, content)
    #     self.close_excel()  # 写入后立即关闭

    # 清空结果列
    # def clear_result_from_excel(self):
    #     row_count = self.test_data_sheet.get_row_counts()
    #     col_id = self.get_result_id()
    #     self.test_data_sheet.clear_excel_colum(1, row_count, col_id)
    #     self.close_excel()  # 清空后也需关闭

    # 关闭 Excel 文件
    def close_excel(self):
        if hasattr(self.test_data_sheet, 'close'):
            self.test_data_sheet.close()
        else:
            self.test_data_sheet = None
            print("ExcelUtils 未实现 close 方法，已释放引用")



# 测试主程序
if __name__ == '__main__':
    try:
        # 指定存放Excel用例的目录

        # 读取所有Excel文件中的用例
        testdata_utils = TestdataUtils()
        all_test_cases = testdata_utils.def_testcase_data_list_by_mysql()
        print(all_test_cases)

    except Exception as e:
        logger.error(f"执行出错: {str(e)}")