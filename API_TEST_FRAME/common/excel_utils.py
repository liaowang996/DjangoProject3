import xlrd
import os
import psutil
from xlutils.copy import copy
from common import config

class ExcelUtils():
    def __init__(self, file_path, sheet_name):
        self.file_path = file_path
        self.wb = xlrd.open_workbook(self.file_path, formatting_info=True)
        self.sheet_name = sheet_name
        self.sheet = self.get_sheets()
        # 缓存合并单元格信息，避免重复计算
        self.merged_cells = self.get_merged_info()


    def get_sheets(self):
        """获取指定的工作表对象"""
        try:
            sheet = self.wb.sheet_by_name(self.sheet_name)
            return sheet
        except FileNotFoundError:
            raise Exception(f"文件不存在: {self.file_path}")
        except xlrd.XLRDError as e:
            raise Exception(f"读取工作表失败: {str(e)}")

    def get_row_counts(self):
        """获取行数"""
        return self.sheet.nrows

    def get_col_counts(self):
        """获取列数"""
        return self.sheet.ncols

    def __get_cell_value(self, row_index, col_index):
        """获取指定单元格的值（私有方法）"""
        # 检查索引是否越界
        if row_index < 0 or row_index >= self.get_row_counts():
            raise IndexError(f"行索引 {row_index} 超出范围")
        if col_index < 0 or col_index >= self.get_col_counts():
            raise IndexError(f"列索引 {col_index} 超出范围")

        return self.sheet.cell_value(row_index, col_index)

    def get_merged_info(self):
        """获取合并单元格信息"""
        return self.sheet.merged_cells

    def get_merged_cell_value_from_cell(self, row_index, col_index):
        """
        获取指定单元格的值，处理合并单元格情况
        如果是合并单元格，返回合并区域左上角的值
        """
        # 先假设不是合并单元格，直接获取值
        cell_value = self.__get_cell_value(row_index, col_index)

        # 如果有合并单元格信息，检查当前单元格是否在合并区域内
        if self.merged_cells:
            for (rlow, rhigh, clow, chigh) in self.merged_cells:
                if rlow <= row_index < rhigh and clow <= col_index < chigh:
                    # 如果是合并单元格，取合并区域左上角的值
                    cell_value = self.__get_cell_value(rlow, clow)
                    break

        return cell_value

    def get_sheet_data_by_dict(self):
        """将工作表数据转换为字典列表，使用首行作为键"""
        alldata_list = []
        if self.get_row_counts() < 1:
            return alldata_list  # 空表返回空列表

        # 获取首行作为字典的键
        first_row = [self.get_merged_cell_value_from_cell(0, col)
                     for col in range(self.get_col_counts())]

        # 从第二行开始读取数据
        for row in range(1, self.get_row_counts()):
            row_dict = {}
            for col in range(self.get_col_counts()):
                # 使用首行的值作为键，当前单元格的值作为值
                row_dict[first_row[col]] = self.get_merged_cell_value_from_cell(row, col)
            alldata_list.append(row_dict)
        return alldata_list

    def update_excel_data(self,row_id,col_id,content):
        new_workbook = copy(self.wb)
        sheet = new_workbook.get_sheet(self.wb.sheet_names().index(self.sheet_name))
        sheet.write(row_id, col_id, content)
        new_workbook.save(self.file_path)

    def clear_excel_colum(self,start_id,end_id,col_id):
        new_workbook = copy(self.wb)
        sheet = new_workbook.get_sheet(self.wb.sheet_names().index(self.sheet_name))
        for row_id in range(start_id,end_id):
            sheet.write(row_id, col_id, '')
        new_workbook.save(self.file_path)

    #结束文件打开没关闭的操作
    def force_close_file(file_path):
        file_path = os.path.abspath(file_path)
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                for file in proc.info['open_files'] or []:
                    if file_path in file.path:
                        print(f"发现占用进程：{proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()  # 终止进程
                        print(f"已关闭进程 {proc.info['pid']}")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
if __name__ == '__main__':

    current_path = os.path.dirname(os.path.realpath(__file__))
    excel_path = os.path.join(current_path, '..', 'samples/data/test_demo.xls')
    excel = ExcelUtils(excel_path, 'Sheet1')
    # e.update_excel_data(1,14,'111')
    print(excel.sheet.row(0)[13].value)
    for i in range(len(excel.sheet.row(0))):
        if excel.sheet.row(0)[i] == '测试结果':
            break
    print(i)


    #     # 确保路径正确解析
    #     excel_path = os.path.abspath(excel_path)
    #
    #     excel_utils = ExcelUtils(excel_path, 'Sheet1')
    #     print("工作表数据:")
    #     for row in excel_utils.get_sheet_data_by_dict():
    #         print(row)
    #
    #     # 示例：获取第3行第4列的值（索引从0开始）
    #     print("\n指定单元格的值:")
    #     print(excel_utils.get_merged_cell_value_from_cell(2, 3))
    # except Exception as e:
    #     print(f"发生错误: {str(e)}")
#