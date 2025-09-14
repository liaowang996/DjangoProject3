
import re
import ast
import requests

# temp_variables = {"token": "123123123"}
#
# params = '{"access_token": ${token}}'
#
# value = re.findall('\\${\\w+}',params)[0]
# print(value)
# params = params.replace(value,temp_variables.get(value[2:-1]))
# print( params)
# requests.get(url='',
#              params = ast.literal_eval(params))


temp_variables = {"token": "123123123","number":"123","age":"66"}

str1= '{"access_token": ${token},${age}===>${number}}'

for v in re.findall('\\${\\w+}',str1):
    str1 = str1.replace(v,temp_variables.get(v[2:-1]))

print(str1)

