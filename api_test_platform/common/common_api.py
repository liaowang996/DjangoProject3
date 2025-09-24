import requests
from common import config
'''
    针对每个接口都把它做成函数处理，所有接口的入参都座位函数的形参，函数的返回值做为接口的响应对象
'''

def get_access_token_api(session,grant_type,appid,secret,tag_json):
    params = {
        'grant_type':grant_type,
        'appid':appid,
        'secret':secret
    }
    json_data = tag_json
    response = session.get(url = config.URL1 + "/cgi-bin/token",
                            params = params
                            )
    return response