
import ast
import re

#实际结果
str1 = '{"token":"ssasdasd","number":123,"age":66}'

#期望结果
str3 = '{"token":"(.+?)","number":(.+?),"age":(.+?)}'
#正则检测测试

if re.findall(str2,str1):
    print(True)
else:
    print(False)

#是否包含json keys,键值对是否存在

jsondata1 = ast.literal_eval(str1)
str2 = 'token,number,age'
check_key_list = str2.split(',')
for check_key in check_key_list:
    result = True
    if check_key in jsondata1.keys():
        result = True
    else:
        result = False
    if not result:
        break
# print( result)

#键值对检测正确，键和值都正确
str2 = '{"token":"ssasdasd"}'
for v in ast.literal_eval(str2).items():
    result = True
    if v in jsondata1.items():
        result = True
    else:
        result = False
    if not result:
        break

jsondata1.items()