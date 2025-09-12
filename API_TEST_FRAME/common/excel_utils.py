import xlrd
import os


class ExcelUtils():
    def __init__(self, file_path, sheet_name):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.sheet = self.get_sheets()
        # 缓存合并单元格信息，避免重复计算
        self.merged_cells = self.get_merged_info()

    def get_sheets(self):
        """获取指定的工作表对象"""
        try:
            wb = xlrd.open_workbook(self.file_path)
            sheet = wb.sheet_by_name(self.sheet_name)
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


if __name__ == '__main__':
    try:
        current_path = os.path.dirname(os.path.realpath(__file__))
        excel_path = os.path.join(current_path, '..', 'samples/data/test_demo.xlsx')
        # 确保路径正确解析
        excel_path = os.path.abspath(excel_path)

        excel_utils = ExcelUtils(excel_path, 'Sheet1')
        print("工作表数据:")
        for row in excel_utils.get_sheet_data_by_dict():
            print(row)

        # 示例：获取第3行第4列的值（索引从0开始）
        print("\n指定单元格的值:")
        print(excel_utils.get_merged_cell_value_from_cell(2, 3))
    except Exception as e:
        print(f"发生错误: {str(e)}")
