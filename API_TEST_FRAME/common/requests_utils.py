import requests
import re
import ast
import jsonpath
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from common import config
from common.check_utils import CheckUtils


class RequestsUtils():

    def __init__(self):
        self.host1 = config.URL1
        self.host  = config.URL
        self.headers = {"Content-Type": "application/json;charset=UTF-8"}
        self.session = requests.session()
        self.temp_variables = {}  #临时变量，用于存储传值

    def __get(self,get_info):
        try:
            url = self.host1 +get_info['请求地址']
            response = self.session.get( url = url,
                                         params = ast.literal_eval(get_info['请求参数(get)'])
                                         )
            response.encoding = response.apparent_encoding
            '''使用jsonpath对返回取值
                接下来考虑如何使用传值变量呢？===思路：在请求类中增加一个字典，字典的key作为变量名、字典的value
                作为取值代码和取值方式配合使用取到的值  self.temp_variables = {}
            '''
            if get_info['取值方式'] == 'json取值':
                value = jsonpath.jsonpath(response.json(),get_info['取值代码'])[0]
                self.temp_variables[get_info['传值变量']] = value
            elif get_info['取值方式'] == '正则匹配':
                value = re.findall(get_info['取值代码'],response.text)[0]
                self.temp_variables[get_info['传值变量']] = value
            result = CheckUtils(response).run_check(check_type = get_info['期望结果类型'],
                                                     check_data = get_info['期望结果'])
        except ConnectionError as e:
            result = {'code':4,'result':'[%s]请求执行连接超时'%(get_info['接口名称'])}
        except RequestException as e:
            result = {'code':4,'result':'[%s]请求执行报Request异常，原因是%s'%(get_info['接口名称'],e.__str__())}
        except Exception as e:
            result = {'code':4,'result':'[%s]请求执行报系统错误，原因是%s'%(get_info['接口名称'],e.__str__())}
        return result


    def __post(self,post_info):
        try:
            url = self.host +post_info['请求地址']
            response = self.session.get( url = url,
                                         headers = self.headers,
                                         # params = ast.literal_eval(post_info['请求参数(get)']),
                                         # data = ast.literal_eval(post_info['提交数据(post)'])
                                         params = ast.literal_eval(post_info['请求参数(get)']),
                                         json = None #  ast.literal_eval(post_info['提交数据(post)'])
                                         )

            response.encoding = response.apparent_encoding


            if post_info['取值方式'] == 'json取值':
                value = jsonpath.jsonpath(response.json(),post_info['取值代码'])[0]
                self.temp_variables[post_info['传值变量']] = value
            elif post_info['取值方式'] == '正则匹配':
                value = re.findall(post_info['取值代码'],response.text)[0]
                self.temp_variables[post_info['传值变量']] = value
            result = CheckUtils(response).run_check(check_type=post_info['期望结果类型'],
                                                    check_data=post_info['期望结果'])
        except ConnectionError as e:
            result = {'code':4,'result':'[%s]请求执行连接超时'%(post_info['接口名称'])}
        except RequestException as e:
            result = {'code':4,'result':'[%s]请求执行报Request异常，原因是%s'%(post_info['接口名称'],e.__str__())}
        except Exception as e:
            result = {'code':4,'result':'[%s]请求执行报系统错误，原因是%s'%(post_info['接口名称'],e.__str__())}
        return result

    def request(self,step_info):
        try:
            request_type = step_info['请求方式']
            param_variable_list = re.findall('\\${\\w+}', step_info['请求参数(get)'])
            if param_variable_list:
                for param_variable in param_variable_list:
                    step_info['请求参数(get)'] = step_info['请求参数(get)'].replace(param_variable,
                                                                                  self.temp_variables[param_variable[2:-1]])

            if request_type == 'GET':
                result=self.__get(step_info)
            elif request_type == 'POST':
                param_variable_list = re.findall('\\${\\w+}', step_info['提交数据(post)'])
                if param_variable_list:
                    for param_variable in param_variable_list:
                        step_info['提交数据(post)'] = step_info['提交数据(post)'].replace(param_variable,
                                                                                        self.temp_variables[
                                                                                            param_variable[2:-1]])
                result=self.__post(step_info)
            else:
                result = {'code':1,'result':'请求方式不支持'}
        except  Exception as e:
            result = {'code':4,'result':'用例编号[%s]的[%s]步骤出现系统异常，原因%s'%(step_info['测试用例编号'],step_info['测试用例步骤'],e)}
        return result

    def request_by_step(self,step_infos):
        self.temp_variables = {}
        for step_info in step_infos:
            temp_result = self.request(step_info)
            if temp_result['code'] != 0:
                break
        return temp_result

if __name__ == "__main__":

    """
    取值方式：json取值、正则匹配
    请求方式:POST、GET
    """
    # get_info={'测试用例编号': 'case_01', '测试用例名称': '测试能否正确获取access_token接口', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '获取access_token接口', '请求方式': 'GET', '请求地址': '/cgi-bin/token', '请求参数(get)': '{"grant_type": "client_credential","appid": "wx91b4a00dbb9f828d","secret": "f5d2dc18178fac284c135c9e3df0ec5b"} ', '提交数据(post)': '提交数据(post)1', '取值方式': '正则匹配', '传值变量': 'errmsg', '取值代码': '"errmsg":"(.+?)"', '期望结果类型': '期望结果类型1', '期望结果': '期望结果1'}
    # RequestsUtils().request(get_info)

    # post_info={'测试用例编号': 'case_01', '测试用例名称': '/api/users', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '/api/users', '请求方式': 'POST', '请求地址': '/api/users', '请求参数(get)': '', '提交数据(post)': '{"name": "morpheus","job": "leader"}', '取值方式': '取值方式1', '传值变量': '传值变量1', '取值代码': '取值代码1', '期望结果类型': '期望结果类型1', '期望结果': '期望结果1'}
    # print(RequestsUtils().request(post_info))

    test_data = [{'测试用例编号': 'case_01', '测试用例名称': '注册接口', '用例执行': '是', '测试用例步骤': 'step1',
                  '接口名称': '注册接口', '请求方式': 'POST', '请求地址': '/api/register',
                  '请求参数(get)': '{"email": "sydney@fife","password": "pistol"}', '提交数据(post)': '',
                  '取值方式': '正则匹配', '传值变量': 'total_pages', '取值代码': '"total_pages":(.+?)',
                  '期望结果类型': 'json键是否存在', '期望结果': 'total_pages'},
                 {'测试用例编号': 'case_01', '测试用例名称': '登录失败接口', '用例执行': '是', '测试用例步骤': 'step1',
                  '接口名称': '登录失败接口', '请求方式': 'POST', '请求地址': '/api/login',
                  '请求参数(get)': '{"email": "${total_pages}"}', '提交数据(post)': '', '取值方式': '', '传值变量': '',
                  '取值代码': '', '期望结果类型': 'json键是否存在', '期望结果': 'error'}
                 ]

    RequestsUtils().request_by_step(test_data)