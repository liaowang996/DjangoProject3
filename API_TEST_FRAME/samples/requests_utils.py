
import requests
import ast
from common import config



class RequestsUtils():

    def __init__(self):
        self.host1 = config.URL1
        self.host  = config.URL
        self.headers = {"Content-Type": "application/json;charset=UTF-8"}
        self.session = requests.session()


    def get(self,get_infos):
        url = self.host1 +get_infos['请求地址']
        response = self.session.get( url = url,
                                     params = ast.literal_eval(get_infos['请求参数(get)'])
                                     )

        response.encoding = response.apparent_encoding
        result = {
            'code':0 ,#请求是否成功的标志位
            'response_reason':response.reason,
            'response_code':response.status_code,
            'response_headers':response.headers,
            'reponse_body':response.text
        }
        return result


    def post(self,post_infos):
        url = self.host +post_infos['请求地址']
        response = self.session.get( url = url,
                                     # params = ast.literal_eval(post_infos['请求参数(get)']),
                                     data = ast.literal_eval(post_infos['提交数据(post)'])
                                     )

        response.encoding = response.apparent_encoding

        result = {
            'code':0 ,#请求是否成功的标志位
            'response_reason':response.reason,
            'response_code':response.status_code,
            'response_headers':response.headers,
            'reponse_body':response.text
        }
        return result

if __name__ == "__main__":
    get_info={'测试用例编号': 'case_01', '测试用例名称': '测试能否正确获取access_token接口', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '获取access_token接口', '请求方式': 'get', '请求地址': '/cgi-bin/token', '请求参数(get)': '{"grant_type": "client_credential","appid": "wx91b4a00dbb9f828d","secret": "f5d2dc18178fac284c135c9e3df0ec5b"} ', '提交数据(post)': '提交数据(post)1', '取值方式': '取值方式1', '传值变量': '传值变量1', '取值代码': '取值代码1', '期望结果类型': '期望结果类型1', '期望结果': '期望结果1'}
    # print(RequestsUtils().get(get_info))

    post_info={'测试用例编号': 'case_01', '测试用例名称': '/api/users', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '/api/users', '请求方式': 'POST', '请求地址': '/api/users', '请求参数(get)': '', '提交数据(post)': '{"name": "morpheus","job": "leader"}', '取值方式': '取值方式1', '传值变量': '传值变量1', '取值代码': '取值代码1', '期望结果类型': '期望结果类型1', '期望结果': '期望结果1'}
    print(RequestsUtils().post(post_info))