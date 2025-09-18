import ast
import re
from common.log_utils import logger


class CheckUtils():
    def __init__(self, check_response=None):
        self.ck_response = check_response
        # 初始化结果模板（补充check_result和message字段，与请求工具兼容）
        self.base_result = {
            'code': 0 if check_response.status_code == 200 else 2,
            'response_reason': self.ck_response.reason,
            'response_code': self.ck_response.status_code,
            'response_headers': dict(self.ck_response.headers),  # 转为dict，避免对象序列化问题
            'reponse_body': self.ck_response.text,
            'check_result': False,
            'message': ''
        }
        # 断言规则映射
        self.ck_rules = {
            '无': self.no_check,
            'json键是否存在': self.check_key,
            'json键值对': self.check_key_value,
            '正则匹配': self.check_rerexp,
        }

    def no_check(self, check_data=None):
        """无断言：默认通过"""
        result = self.base_result.copy()
        result['check_result'] = True
        result['message'] = '无断言，默认通过'
        logger.debug("无断言规则，返回默认通过")
        return result

    def check_key(self, check_data=None):
        """检查JSON键是否存在"""
        result = self.base_result.copy()
        if not check_data:
            result['code'] = 4
            result['message'] = '断言数据为空，无法检查JSON键'
            logger.error(result['message'])
            return result

        try:
            # 解析响应JSON
            response_json = self.ck_response.json()
            check_keys = [key.strip() for key in check_data.split(',')]
            missing_keys = [key for key in check_keys if key not in response_json]

            if not missing_keys:
                result['check_result'] = True
                result['message'] = f"JSON键检查通过，所有键存在: {','.join(check_keys)}"
                logger.debug(result['message'])
            else:
                result['code'] = 4
                result['message'] = f"JSON键检查失败，缺失键: {','.join(missing_keys)}"
                logger.error(result['message'])

        except ValueError as e:
            # 响应不是JSON格式
            result['code'] = 4
            result['message'] = f"JSON键检查失败：响应不是JSON格式: {str(e)}"
            logger.error(result['message'])
        except Exception as e:
            result['code'] = 4
            result['message'] = f"JSON键检查异常: {str(e)}"
            logger.error(result['message'], exc_info=True)

        return result

    def check_key_value(self, check_data=None):
        """检查JSON键值对是否匹配"""
        result = self.base_result.copy()
        if not check_data:
            result['code'] = 4
            result['message'] = '断言数据为空，无法检查JSON键值对'
            logger.error(result['message'])
            return result

        try:
            # 解析断言数据和响应JSON
            expect_data = ast.literal_eval(check_data)
            response_json = self.ck_response.json()
            mismatch_items = []

            # 检查每个键值对
            for key, expect_val in expect_data.items():
                if key not in response_json:
                    mismatch_items.append(f"键{key}不存在")
                elif response_json[key] != expect_val:
                    mismatch_items.append(f"键{key}: 期望{expect_val}, 实际{response_json[key]}")

            if not mismatch_items:
                result['check_result'] = True
                result['message'] = f"JSON键值对检查通过，所有键值匹配"
                logger.debug(result['message'])
            else:
                result['code'] = 4
                result['message'] = f"JSON键值对检查失败: {';'.join(mismatch_items)}"
                logger.error(result['message'])

        except (ValueError, SyntaxError) as e:
            # 断言数据格式错误或响应不是JSON
            result['code'] = 4
            result['message'] = f"JSON键值对检查失败：{str(e)}"
            logger.error(result['message'])
        except Exception as e:
            result['code'] = 4
            result['message'] = f"JSON键值对检查异常: {str(e)}"
            logger.error(result['message'], exc_info=True)

        return result

    def check_rerexp(self, check_data=None):
        """正则匹配检查"""
        result = self.base_result.copy()
        if not check_data:
            result['code'] = 4
            result['message'] = '断言数据为空，无法执行正则匹配'
            logger.error(result['message'])
            return result

        try:
            pattern = re.compile(check_data)
            match_result = re.findall(pattern, self.ck_response.text)

            if match_result:
                result['check_result'] = True
                result['message'] = f"正则匹配通过，匹配结果: {match_result[:2]}"  # 只显示前2个结果，避免过长
                logger.debug(result['message'])
            else:
                result['code'] = 4
                result['message'] = f"正则匹配失败，表达式: {check_data}, 响应内容: {self.ck_response.text[:200]}"
                logger.error(result['message'])

        except re.error as e:
            # 正则表达式语法错误
            result['code'] = 4
            result['message'] = f"正则表达式错误: {str(e)}"
            logger.error(result['message'])
        except Exception as e:
            result['code'] = 4
            result['message'] = f"正则匹配异常: {str(e)}"
            logger.error(result['message'], exc_info=True)

        return result

    def run_check(self, check_type=None, check_data=None):
        """执行断言（移除200状态码限制，支持所有状态码断言）"""
        logger.info(f"开始执行断言: 类型={check_type}, 数据={check_data}")

        if not check_type:
            result = self.base_result.copy()
            result['code'] = 4
            result['message'] = '断言类型未指定'
            logger.error(result['message'])
            return result

        if check_type in self.ck_rules:
            return self.ck_rules[check_type](check_data)
        else:
            result = self.base_result.copy()
            result['code'] = 4
            result['message'] = f"不支持的断言类型: {check_type}，支持类型: {list(self.ck_rules.keys())}"
            logger.error(result['message'])
            return result


if __name__ == '__main__':
    # 测试代码（模拟响应）
    class MockResponse:
        def __init__(self, status_code, text, reason='OK'):
            self.status_code = status_code
            self.text = text
            self.reason = reason
            self.headers = {'Content-Type': 'application/json'}

        def json(self):
            import json
            return json.loads(self.text)


    # 测试JSON键检查
    mock_resp1 = MockResponse(200, '{"token":"123","age":20}')
    check1 = CheckUtils(mock_resp1)
    print(check1.run_check('json键是否存在', 'token,age'))  # 应该通过

    # 测试JSON键值对检查
    mock_resp2 = MockResponse(200, '{"token":"123","age":20}')
    check2 = CheckUtils(mock_resp2)
    print(check2.run_check('json键值对', '{"token":"123","age":21}'))  # 应该失败（age不匹配）

    # 测试正则匹配
    mock_resp3 = MockResponse(401, '{"error":"Unauthorized","msg":"token过期"}')
    check3 = CheckUtils(mock_resp3)
    print(check3.run_check('正则匹配', '"error":"(.+?)"'))  # 支持401状态码断言