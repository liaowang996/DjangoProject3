import xlrd
import os
import psutil
from xlutils.copy import copy
from common import config
from common.log_utils import logger
import glob


current_path = os.path.dirname(__file__)
test_data = os.path.join(current_path, '..', config.TEST_DATA)


class ExcelUtils():
    def __init__(self, file_path, sheet_name):
        """
        初始化Excel工具类
        :param file_path: Excel文件路径
        :param sheet_name: 工作表名称
        """
        self.test_data = test_data
        self.file_path = self._validate_file_path(file_path)
        self.sheet_name = sheet_name
        self.wb = self._open_workbook()
        self.sheet = self.get_sheets()
        # 缓存合并单元格信息，避免重复计算
        self.merged_cells = self.get_merged_info()
        logger.info(f"Excel工具初始化完成: {self.file_path} - {self.sheet_name}")

    def _validate_file_path(self, file_path):
        """验证文件路径有效性"""
        normalized_path = os.path.abspath(file_path)

        if not os.path.exists(normalized_path):
            error_msg = f"Excel文件不存在: {normalized_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        if not os.path.isfile(normalized_path):
            error_msg = f"路径不是文件: {normalized_path}"
            logger.error(error_msg)
            raise IsADirectoryError(error_msg)

        if not normalized_path.endswith(('.xls', '.xlsx')):
            logger.warning(f"文件可能不是Excel格式: {normalized_path}")

        return normalized_path

    def _open_workbook(self):
        """打开工作簿并处理可能的错误"""
        try:
            # 对于.xlsx文件，需要使用xlrd的新版本或切换到openpyxl
            # 这里保持原有的formatting_info=True以保留格式
            return xlrd.open_workbook(self.file_path, formatting_info=True)
        except xlrd.XLRDError as e:
            error_msg = f"打开Excel文件失败: {str(e)}"
            logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"处理Excel文件时出错: {str(e)}"
            logger.error(error_msg)
            raise

    def get_sheets(self):
        """获取指定的工作表对象"""
        try:
            return self.wb.sheet_by_name(self.sheet_name)
        except xlrd.XLRDError as e:
            error_msg = f"工作表 '{self.sheet_name}' 不存在: {str(e)}"
            logger.error(error_msg)
            raise

    def get_row_counts(self):
        """获取行数"""
        count = self.sheet.nrows
        # logger.debug(f"工作表 '{self.sheet_name}' 包含 {count} 行")
        return count

    def get_col_counts(self):
        """获取列数"""
        count = self.sheet.ncols
        # logger.debug(f"工作表 '{self.sheet_name}' 包含 {count} 列")
        return count

    def __get_cell_value(self, row_index, col_index):
        """获取指定单元格的值（私有方法）"""
        # 检查索引是否越界
        if row_index < 0 or row_index >= self.get_row_counts():
            raise IndexError(f"行索引 {row_index} 超出范围（最大行索引: {self.get_row_counts() - 1}）")
        if col_index < 0 or col_index >= self.get_col_counts():
            raise IndexError(f"列索引 {col_index} 超出范围（最大列索引: {self.get_col_counts() - 1}）")

        return self.sheet.cell_value(row_index, col_index)

    def get_merged_info(self):
        """获取合并单元格信息"""
        merged_info = self.sheet.merged_cells
        logger.debug(f"工作表 '{self.sheet_name}' 包含 {len(merged_info)} 个合并单元格区域")
        return merged_info

    def get_merged_cell_value_from_cell(self, row_index, col_index):
        """
        获取指定单元格的值，处理合并单元格情况
        如果是合并单元格，返回合并区域左上角的值
        """
        try:
            # 先假设不是合并单元格，直接获取值
            cell_value = self.__get_cell_value(row_index, col_index)

            # 如果有合并单元格信息，检查当前单元格是否在合并区域内
            if self.merged_cells:
                for (rlow, rhigh, clow, chigh) in self.merged_cells:
                    if rlow <= row_index < rhigh and clow <= col_index < chigh:
                        # 如果是合并单元格，取合并区域左上角的值
                        cell_value = self.__get_cell_value(rlow, clow)
                        logger.debug(f"单元格({row_index},{col_index})属于合并区域，取值({rlow},{clow})")
                        break

            return cell_value
        except IndexError as e:
            logger.error(f"获取单元格值失败: {str(e)}")
            raise

    def get_sheet_data_by_dict(self):
        """将工作表数据转换为字典列表，使用首行作为键"""
        try:
            alldata_list = []
            row_count = self.get_row_counts()

            if row_count < 1:
                logger.warning(f"工作表 '{self.sheet_name}' 为空")
                return alldata_list  # 空表返回空列表

            # 获取首行作为字典的键
            first_row = [self.get_merged_cell_value_from_cell(0, col)
                         for col in range(self.get_col_counts())]

            # 从第二行开始读取数据
            for row in range(1, row_count):
                row_dict = {}
                for col in range(self.get_col_counts()):
                    # 使用首行的值作为键，当前单元格的值作为值
                    key = first_row[col] if first_row[col] is not None else f"col_{col}"
                    row_dict[key] = self.get_merged_cell_value_from_cell(row, col)
                alldata_list.append(row_dict)

            logger.info(f"从工作表 '{self.sheet_name}' 读取了 {len(alldata_list)} 条数据")
            return alldata_list
        except Exception as e:
            logger.error(f"转换工作表数据为字典列表失败: {str(e)}", exc_info=True)
            raise

    # def update_excel_data(self, row_id, col_id, content):
    #     """更新Excel单元格数据"""
    #     try:
    #         # 检查文件是否被占用
    #         if self._is_file_locked():
    #             logger.warning(f"文件 {self.file_path} 可能被占用，尝试关闭占用进程")
    #             self.force_close_file()
    #
    #         new_workbook = copy(self.wb)
    #         sheet_index = self.wb.sheet_names().index(self.sheet_name)
    #         sheet = new_workbook.get_sheet(sheet_index)
    #         sheet.write(row_id, col_id, content)
    #
    #         # 保存前再次检查
    #         if self._is_file_locked():
    #             raise IOError(f"文件 {self.file_path} 被锁定，无法写入")
    #
    #         new_workbook.save(self.file_path)
    #         logger.info(f"已更新单元格({row_id},{col_id})为: {content}")
    #         return True
    #     except Exception as e:
    #         logger.error(f"更新Excel数据失败: {str(e)}", exc_info=True)
    #         return False

    # def clear_excel_column(self, start_id, end_id, col_id):
    #     """清空Excel列中指定范围的单元格"""
    #     try:
    #         # 检查文件是否被占用
    #         if self._is_file_locked():
    #             logger.warning(f"文件 {self.file_path} 可能被占用，尝试关闭占用进程")
    #             self.force_close_file()
    #
    #         new_workbook = copy(self.wb)
    #         sheet_index = self.wb.sheet_names().index(self.sheet_name)
    #         sheet = new_workbook.get_sheet(sheet_index)
    #
    #         for row_id in range(start_id, end_id):
    #             sheet.write(row_id, col_id, '')
    #
    #         # 保存前再次检查
    #         if self._is_file_locked():
    #             raise IOError(f"文件 {self.file_path} 被锁定，无法写入")
    #
    #         new_workbook.save(self.file_path)
    #         logger.info(f"已清空列 {col_id} 中从行 {start_id} 到 {end_id - 1} 的数据")
    #         return True
    #     except Exception as e:
    #         logger.error(f"清空Excel列数据失败: {str(e)}", exc_info=True)
    #         return False

    def _is_file_locked(self):
        """检查文件是否被锁定"""
        try:
            with open(self.file_path, 'a'):
                return False
        except IOError:
            return True

    def force_close_file(self):
        """强制关闭占用文件的进程"""
        file_path = os.path.abspath(self.file_path)
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                for file in proc.info['open_files'] or []:
                    if file_path == file.path:
                        logger.warning(f"发现占用进程：{proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()  # 终止进程
                        logger.info(f"已关闭进程 {proc.info['pid']}")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.warning(f"处理进程时出错: {str(e)}")
        return False

    # def find_column_index(self, column_name):
    #     """根据列名查找列索引"""
    #     try:
    #         for col in range(self.get_col_counts()):
    #             if self.get_merged_cell_value_from_cell(0, col) == column_name:
    #                 logger.debug(f"找到列 '{column_name}'，索引为 {col}")
    #                 return col
    #         logger.warning(f"未找到列 '{column_name}'")
    #         return -1
    #     except Exception as e:
    #         logger.error(f"查找列索引失败: {str(e)}")
    #         return -1

    def read_multiple_excel_cases(self, sheet_name='Sheet1'):
        """
        读取指定目录下的所有Excel文件中的测试用例
        :param excel_dir_path: 存放Excel文件的目录路径
        :param sheet_name: 要读取的工作表名称，默认为'Sheet1'
        :return: 整合后的测试用例字典列表，格式为[{用例1}, {用例2}, ...]
        """
        all_cases = []
        excel_dir_path = self.test_data

        try:
            # 验证目录是否存在
            if not os.path.exists(excel_dir_path):
                logger.error(f"目录不存在: {excel_dir_path}")
                return all_cases

            if not os.path.isdir(excel_dir_path):
                logger.error(f"路径不是目录: {excel_dir_path}")
                return all_cases

            # 查找目录下所有Excel文件（.xls和.xlsx）
            excel_files = glob.glob(os.path.join(excel_dir_path, '*.xls')) + \
                          glob.glob(os.path.join(excel_dir_path, '*.xlsx'))

            if not excel_files:
                logger.warning(f"在目录 {excel_dir_path} 中未找到Excel文件")
                return all_cases

            logger.info(f"发现 {len(excel_files)} 个Excel文件，开始读取测试用例...")

            # 逐个读取Excel文件
            for file_path in excel_files:
                file_name = os.path.basename(file_path)
                logger.info(f"开始处理文件: {file_name}")

                try:
                    # 使用已有的ExcelUtils读取单个文件
                    excel_utils = ExcelUtils(file_path, sheet_name)
                    cases = excel_utils.get_sheet_data_by_dict()

                    if cases:
                        # 可以为每个用例添加来源文件信息，便于追溯
                        for case in cases:
                            case['来源文件'] = file_name

                        all_cases.extend(cases)
                        logger.info(f"从 {file_name} 中读取到 {len(cases)} 条用例")
                    else:
                        logger.warning(f"{file_name} 中未包含测试用例数据")

                except Exception as e:
                    logger.error(f"处理文件 {file_name} 时出错: {str(e)}", exc_info=True)
                    # 继续处理下一个文件，不中断整体流程
                    continue

            logger.info(f"所有文件处理完成，共读取到 {len(all_cases)} 条测试用例")
            logger.info(f"已整合的用例列表: {all_cases}")
            return all_cases

        except Exception as e:
            logger.error(f"批量读取Excel用例失败: {str(e)}", exc_info=True)
            return all_cases

if __name__ == '__main__':
    try:
        current_path = os.path.dirname(os.path.realpath(__file__))
        excel_path = os.path.join(current_path, '..', 'samples/data/test_demo.xls')
        excel = ExcelUtils(excel_path, 'Sheet1')

        # 示例：获取指定单元格值
        cell_value = excel.get_sheet_data_by_dict()
        logger.info(f"单元格(0,13)的值: {cell_value}")

    except Exception as e:
        logger.error(f"执行Excel操作时出错: {str(e)}", exc_info=True)
