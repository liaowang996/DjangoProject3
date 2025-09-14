import re


str1 = 'summer hot ~'

pattern3 = re.compile(r'(\w+)(\w+)')
# str1 = re.sub(pattern3,r'hello',str1)
# print(str1)



# result = re.match(pattern3,str1)
# print(result.group(1).title())
def fun(m):
    return m.group(1).title()+''+m.group(2).title()


str1 = re.sub(pattern3,fun,str1)
print(str1)