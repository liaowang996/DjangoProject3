import xlrd
import os

excel_file_path = os.path.join(os.path.dirname(__file__), 'data/test_data.xlsx')
print(excel_file_path)


wb = xlrd.open_workbook(excel_file_path)
sheet = wb.sheet_by_name("Sheet1")
cell_value = sheet.cell_value(3, 0)
print(cell_value)
print(sheet.merged_cells)
merged=sheet.merged_cells
# row_index = 3;col_index =0
# for (rlow,rhigh,clow,chigh) in merged:
#     if(row_index >= rlow and row_index <rhigh):
#         if(col_index>=clow and col_index<chigh):
#             print("Merged cell")

def get_merged_cell_value(row_index,col_index):
    cell_value=None
    for (rlow,rhigh,clow,chigh) in merged:
        if(row_index >= rlow and row_index <rhigh):
            if(col_index>=clow and col_index<chigh):
                cell_value = sheet.cell_value(rlow,clow)
    return cell_value


def get_merged_cell_value_from_cell(row_index,col_index):
    cell_value=None
    for (rlow,rhigh,clow,chigh) in merged:
        if(row_index >= rlow and row_index <rhigh):
            if(col_index>=clow and col_index<chigh):
                cell_value = sheet.cell_value(rlow,clow)
                break;#防止多个合并单元格时，多次赋值查询错误
            else:
                cell_value = sheet.cell_value(row_index,col_index)
        else:
            cell_value = sheet.cell_value(row_index, col_index)
    return cell_value

print(r"1111"+str(get_merged_cell_value_from_cell(3,1)))