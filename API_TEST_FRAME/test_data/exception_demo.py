import requests
from requests.exceptions import RequestException

#
# res = requests.get(url = 'http://google.com.hk')
#
# print(res.status_code)
try:
    num_list = [1,2,3,4,5]
    print(num_list[6])
except IndexError as e:
    print('hellow')
except Exception as e:
    print(e)