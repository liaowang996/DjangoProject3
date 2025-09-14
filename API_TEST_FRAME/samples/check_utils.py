import ast
import re



class CheckUtils():
    def __init__(self,check_response=None):
        self.ck_response = check_response
        self.ck_rules = {
            '无':self.no_check,
            'json键是否存在':self.check_key,
            'json键值对':self.check_key_value,
            '正则匹配':self.check_rerexp,
        }
        self.pass_result = {
            'code':0 ,#请求是否成功的标志位
            'response_reason':self.check_response.reason,
            'response_code':self.check_response.status_code,
            'response_headers':self.check_response.headers,
            'reponse_body':self.check_response.text,
            'check_result':True,
            'message':''#扩展座位日志输出等
        }
        self.fail_result ={
            'code':2 ,#请求是否成功的标志位
            'response_reason':self.check_response.reason,
            'response_code':self.check_response.status_code,
            'response_headers':self.check_response.headers,
            'reponse_body':self.check_response.text,
            'check_result': False,
            'message': ''
        }

    def no_check(self):
        return self.pass_result

    #检查key
    def check_key(self,check_data=None):
        check_data_List = check_data.split(',')
        reslist = []    #存放每次比较的结果
        wrongkey = []   #存放比较失败的key

        for check_data in check_data_List:
            if check_data in self.ck_response.keys():
                reslist.append(self.pass_result)
            else:
                reslist.append(self.fail_result)
                wrongkey.append(check_data)
        # print(reslist)
        # print(wrongkey)
        if self.fail_result in reslist:
            # print("缺少key：", wrongkey)
            return self.fail_result
        else:
            # print("检查key成功")
            return self.pass_result

    #检查key和value
    def check_key_value(self,check_data=None):
        res_list = []    #存放每次比较的结果
        wrong_item = []   #存放比较失败的 item
        for check_item in ast.literal_eval(check_data).items():
            if check_item in self.ck_response.items():
                res_list.append(self.pass_result)
            else:
                res_list.append(self.fail_result)
                wrong_item.append(check_item)
        if self.fail_result in res_list:
            print("缺少key：", wrong_item)
            return self.fail_result
        else:
            print("检查key成功")
            return self.pass_result

    #正则匹配
    def check_rerexp(self,check_data=None):
        pattern = re.compile(check_data)
        if re.findall(pattern= pattern,string = self.ck_response):
            print("正则匹配成功")
            return self.pass_result
        else:
            print("正则匹配失败")
            return self.fail_result

    def run_check(self,check_type=None,check_data=None):
        code = self.ck_response.status_code
        if code == 200:
            if check_type in self.ck_rules.keys():
                results = self.ck_rules[check_type](check_data)
                return results
            else:
                self.fail_result['message'] = '不支持%s判断方式'%check_type
                return self.fail_result
        else:
            self.fail_result['message'] = '请求失败'
            return self.fail_result




if __name__=='__main__':
    #     #实际结果
    str1 = '{"token":"ssasdasd","number":123,"age":66}'
    str3 = '{"token":"ssasdasd","number":123}'
    # #期望结果
    # str3 = '{"token":"(.+?)","number":(.+?),"age":(.+?)}'
    str2 = 'token,number,ages'
    str4  = '"token":"(.+?)","number":(.+?),"age":(.+?)'
    # CheckUtils(str1).check_key(str2)
    # CheckUtils(str1).check_key_value(str3)
    CheckUtils(str1).run_check(str4)