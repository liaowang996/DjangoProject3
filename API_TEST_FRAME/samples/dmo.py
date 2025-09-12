
a = {'one':1, 'two':2, 'three':3}

a.setdefault('one',4)
print(a)
lista = [
    {'测试用例编号': 'case_01', '测试用例名称': 'name_01', '用例执行': '是', '测试用例步骤': '测试用例步骤1', '接口名称': '接口名称1'},
    {'测试用例编号': 'case_02', '测试用例名称': 'name_02', '用例执行': '是', '测试用例步骤': '测试用例步骤2', '接口名称': '接口名称2'},
    {'测试用例编号': 'case_02', '测试用例名称': 'name_03', '用例执行': '是', '测试用例步骤': '测试用例步骤3', '接口名称': '接口名称3'},
    {'测试用例编号': 'case_02', '测试用例名称': 'name_04', '用例执行': '是', '测试用例步骤': '测试用例步骤4', '接口名称': '接口名称4'},
    {'测试用例编号': 'case_05', '测试用例名称': 'name_05', '用例执行': '是', '测试用例步骤': '测试用例步骤5', '接口名称': '接口名称5'},
    {'测试用例编号': 'case_06', '测试用例名称': 'name_06', '用例执行': '是', '测试用例步骤': '测试用例步骤6', '接口名称': '接口名称6'}
]
case_dict={}

for i in lista:
    case_dict.setdefault(i['测试用例编号'],[]).append(i)
# print(case_dict)

case_list = []
for k,v in case_dict.items():
    case_dict={}
    case_dict['case_name'] = k
    case_dict['case_info'] = v
    case_list.append(case_dict)
for c in case_list:
    print(c)