import requests
import re
import ast
import jsonpath
from requests.exceptions import RequestException, ConnectionError
from common import config
from common.check_utils import CheckUtils
from common.log_utils import logger  # 新增日志引用


class RequestsUtils():
    def __init__(self):
        self.host1 = config.URL1
        self.host = config.URL
        self.headers = {"Content-Type": "application/json;charset=UTF-8;multipart/form-data"}
        self.session = requests.session()
        self.temp_variables = {}  # 临时变量，用于存储传值

        # 修复：直接读取config的全局变量，而非调用get方法
        # 优先使用config中定义的REQUEST_TIMEOUT，无则默认10秒
        self.timeout = getattr(config, 'REQUEST_TIMEOUT', 10)
        logger.debug(f"请求超时时间设置为: {self.timeout}秒")

    def __get(self, get_info):
        try:
            # 构建URL
            url = self.host1 + get_info['请求地址']
            logger.debug(f"发送GET请求: {url}, 参数: {get_info['请求参数(get)']}")

            # 发送请求（添加超时）
            response = self.session.get(
                url=url,
                params=ast.literal_eval(get_info['请求参数(get)']),
                timeout=self.timeout
            )
            response.encoding = response.apparent_encoding
            logger.debug(f"GET响应状态码: {response.status_code}, 响应内容: {response.text[:500]}")

            # 变量提取
            self._extract_variable(get_info, response)

            # 结果断言
            result = CheckUtils(response).run_check(
                check_type=get_info['期望结果类型'],
                check_data=get_info['期望结果']
            )
            # 新增：打印完整响应内容（关键！定位非JSON响应的具体内容）
            logger.debug(f"GET响应完整内容: {response.text}")  # 查看返回的到底是什么
            logger.debug(f"GET响应Content-Type: {response.headers.get('Content-Type')}")  # 查看响应类型
            return result

        except ConnectionError as e:
            err_msg = f"[{get_info['接口名称']}]请求连接超时"
            logger.error(err_msg, exc_info=True)
            return {'code': 4, 'result': err_msg, 'check_result': False, 'message': err_msg}
        except RequestException as e:
            err_msg = f"[{get_info['接口名称']}]Request异常: {str(e)}"
            logger.error(err_msg, exc_info=True)
            return {'code': 4, 'result': err_msg, 'check_result': False, 'message': err_msg}
        except Exception as e:
            err_msg = f"[{get_info['接口名称']}]系统错误: {str(e)}"
            logger.error(err_msg, exc_info=True)
            return {'code': 4, 'result': err_msg, 'check_result': False, 'message': err_msg}

    def __post(self, post_info):
        try:
            # 构建URL
            url = self.host + post_info['请求地址']
            logger.debug(
                f"发送POST请求: {url}, 参数: {post_info['请求参数(get)']}, 提交数据: {post_info['提交数据(post)']}")

            # 处理提交数据（修复原GET调用bug）
            post_data = ast.literal_eval(post_info['提交数据(post)']) if post_info['提交数据(post)'] else None

            # 发送POST请求（添加超时）

            logger.warning(post_info['请求参数(get)'] )
            response = self.session.post(
                url=url,
                headers=self.headers,
                params=ast.literal_eval(post_info['请求参数(get)']) if post_info['请求参数(get)'] else None,
                json=post_data,  # 修复：使用post_data而非None
                timeout=self.timeout
            )
            response.encoding = response.apparent_encoding
            logger.debug(f"POST响应状态码: {response.status_code}, 响应内容: {response.text[:500]}")

            # 变量提取
            self._extract_variable(post_info, response)

            # 结果断言
            result = CheckUtils(response).run_check(
                check_type=post_info['期望结果类型'],
                check_data=post_info['期望结果']
            )
            # 新增：打印完整响应内容
            logger.debug(f"POST响应完整内容: {response.text}")
            logger.debug(f"POST响应Content-Type: {response.headers.get('Content-Type')}")
            return result

        except ConnectionError as e:
            err_msg = f"[{post_info['接口名称']}]请求连接超时"
            logger.error(err_msg, exc_info=True)
            return {'code': 4, 'result': err_msg, 'check_result': False, 'message': err_msg}
        except RequestException as e:
            err_msg = f"[{post_info['接口名称']}]Request异常: {str(e)}"
            logger.error(err_msg, exc_info=True)
            return {'code': 4, 'result': err_msg, 'check_result': False, 'message': err_msg}
        except Exception as e:
            err_msg = f"[{post_info['接口名称']}]系统错误: {str(e)}"
            logger.error(err_msg, exc_info=True)
            return {'code': 4, 'result': err_msg, 'check_result': False, 'message': err_msg}

    def _extract_variable(self, step_info, response):
        """提取变量（重构为公共方法，减少重复代码）"""
        extract_type = step_info.get('取值方式')
        if not extract_type or extract_type == '无':
            return

        var_name = step_info.get('传值变量')
        extract_code = step_info.get('取值代码')
        if not var_name or not extract_code:
            logger.warning(f"取值变量或取值代码为空，跳过提取: {step_info['测试用例步骤']}")
            return

        try:
            if extract_type == 'json取值':
                values = jsonpath.jsonpath(response.json(), extract_code)
                if not values or len(values) == 0:
                    logger.error(f"JSON取值失败: 表达式{extract_code}未匹配到值")
                    return
                value = values[0]
            elif extract_type == '正则匹配':
                values = re.findall(extract_code, response.text)
                if not values or len(values) == 0:
                    logger.error(f"正则匹配失败: 表达式{extract_code}未匹配到值")
                    return
                value = values[0]
            else:
                logger.warning(f"不支持的取值方式: {extract_type}")
                return

            self.temp_variables[var_name] = value
            logger.debug(f"提取变量成功: {var_name} = {value}")
        except Exception as e:
            logger.error(f"变量提取失败: {str(e)}", exc_info=True)

    def request(self, step_info):
        try:
            request_type = step_info['请求方式'].upper()
            logger.info(f"开始处理请求步骤: {step_info['测试用例步骤']}, 方式: {request_type}")

            # 替换请求参数中的变量（容错处理）
            step_info['请求参数(get)'] = self._replace_variable(step_info['请求参数(get)'])

            if request_type == 'GET':
                result = self.__get(step_info)
            elif request_type == 'POST':
                # 替换提交数据中的变量
                step_info['提交数据(post)'] = self._replace_variable(step_info['提交数据(post)'])
                result = self.__post(step_info)
            else:
                err_msg = f"不支持的请求方式: {request_type}"
                logger.error(err_msg)
                return {'code': 1, 'result': err_msg, 'check_result': False, 'message': err_msg}

            logger.info(f"请求步骤处理完成: {step_info['测试用例步骤']}, 结果: {result.get('code')}")
            return result

        except Exception as e:
            err_msg = f"用例[{step_info['测试用例编号']}]步骤[{step_info['测试用例步骤']}]异常: {str(e)}"
            logger.error(err_msg, exc_info=True)
            return {'code': 4, 'result': err_msg, 'check_result': False, 'message': err_msg}

    def _replace_variable(self, content):
        """替换变量（容错：变量不存在时不替换，避免KeyError）"""
        if not content:
            return content

        var_list = re.findall('\\${\\w+}', content)
        if not var_list:
            return content

        for var in var_list:
            var_key = var[2:-1]  # 提取变量名（如${token} -> token）
            if var_key in self.temp_variables:
                content = content.replace(var, str(self.temp_variables[var_key]))
                logger.debug(f"替换变量: {var} -> {self.temp_variables[var_key]}")
            else:
                logger.warning(f"变量{var}未找到，跳过替换")

        return content

    def request_by_step(self, step_infos):
        self.temp_variables = {}
        final_result = {'code': 0, 'result': '所有步骤执行完成', 'check_result': True, 'message': ''}

        for step_info in step_infos:
            temp_result = self.request(step_info)
            if temp_result['code'] != 0:
                final_result = temp_result
                logger.error(f"步骤{step_info['测试用例步骤']}执行失败，终止后续步骤")
                break

        return final_result


if __name__ == "__main__":
    # 测试代码（保持原逻辑）
    test_data = [
        {'测试用例编号': 'case_01', '测试用例名称': '注册接口', '用例执行': '是', '测试用例步骤': 'step1',
         '接口名称': '注册接口', '请求方式': 'POST', '请求地址': '/api/register',
         '请求参数(get)': '{"email":"sydney@fife","password":"pistol"}', '提交数据(post)': '',
         '取值方式': '正则匹配', '传值变量': 'total_pages', '取值代码': '"total_pages":(.+?)',
         '期望结果类型': 'json键是否存在', '期望结果': 'total_pages'},
        {'测试用例编号': 'case_01', '测试用例名称': '登录失败接口', '用例执行': '是', '测试用例步骤': 'step1',
         '接口名称': '登录失败接口', '请求方式': 'POST', '请求地址': '/api/login',
         '请求参数(get)': '', '提交数据(post)': '{"email": "${total_pages}"}', '取值方式': '', '传值变量': '',
         '取值代码': '', '期望结果类型': 'json键是否存在', '期望结果': 'error'}
    ]
    result = RequestsUtils().request_by_step(test_data)
    logger.info(f"测试结果: {result}")