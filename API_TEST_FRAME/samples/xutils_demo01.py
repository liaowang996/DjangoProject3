#
#
# import os
# import xlrd
# from xlutils.copy import copy
# from common.excel_utils import ExcelUtils
# from common import config
# from samples.xlutils_demo import excel_path
#
# # excel_path = os.path.join(os.path.dirname(__file__), 'data', 'test_data.xlsx')
# #
# #
# # wb = xlrd.open_workbook(excel_path, formatting_info=True) #创建工作簿对象,formatting_info=True防止格式丢失
# # new_workbook = copy(wb) #new_workbook.copy()创建新的工作簿对象
# # sheet = new_workbook.get_sheet(wb.sheet_name.index('Sheet1'))
# # sheet.write(1, 3, 'new_value333')
# # new_workbook.save(excel_path)
#
# # excel_path = os.path.join(os.path.dirname(__file__), 'data', 'test_demo.xlsx')
# # excel_utils = ExcelUtils(excel_path, 'Sheet1')
# # i = 1;
# # for row in excel_utils.get_sheet_data_by_dict():
# #     if row['测试用例编号']=='case_02' and row['测试用例步骤'] == 'step_01':
# #         break
# #     else:
# #         i = i + 1
# # print( i )
# # test_data = excel_utils.get_sheet_data_by_dict()  # 获取行号
# # for j in range(len(test_data)):
# #     if test_data[j]['测试用例编号']=='case_01' and test_data[j]['测试用例步骤'] == 'step_01':
# #         break
# # print(j+1)
# excel_path = os.path.join(os.path.dirname(__file__), '..',config.CASE_DATA_PATH)
# wb = xlrd.open_workbook(excel_path, formatting_info=True)
#
# new_workbook = copy(wb)
# sheet = new_workbook.get_sheet(wb.sheet_names().index('Sheet1'))
# sheet.write(1, 14, '通过')
# sheet.write(2, 14, '失败')
# new_workbook.save(excel_path)