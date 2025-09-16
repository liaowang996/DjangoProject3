from common.requests_utils import RequestsUtils


test_data=[{'测试用例编号': 'case_01', '测试用例名称': '注册接口', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '注册接口', '请求方式': 'POST', '请求地址': '/api/register', '请求参数(get)': '{"email": "sydney@fife","password": "pistol"}', '提交数据(post)': '', '取值方式': '正则匹配', '传值变量': 'total_pages', '取值代码': '"total_pages":(.+?)', '期望结果类型': 'json键是否存在', '期望结果': 'token'},{'测试用例编号': 'case_01', '测试用例名称': '登录失败接口', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '登录失败接口', '请求方式': 'POST', '请求地址': '/api/login', '请求参数(get)': '{"email": "${token}"}', '提交数据(post)': '', '取值方式': '', '传值变量': '', '取值代码': '', '期望结果类型': 'json键是否存在', '期望结果': 'error'}
         ]

RequestsUtils().request_by_step(test_data)

# test_data1=[{'测试用例编号': 'case_01', '测试用例名称': '注册接口', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '注册接口', '请求方式': 'POST', '请求地址': '/api/register', '请求参数(get)': '{"email": "sydney@fife","password": "pistol"}', '提交数据(post)': '', '取值方式': '正则匹配', '传值变量': 'total_pages', '取值代码': '"total_pages":(.+?)', '期望结果类型': 'json键是否存在', '期望结果': 'token'},
#             {'测试用例编号': 'case_02', '测试用例名称': '登录失败接口', '用例执行': '是', '测试用例步骤': 'step1', '接口名称': '登录失败接口', '请求方式': 'POST', '请求地址': '/api/login', '请求参数(get)': '{"email": "${total_pages}"}', '提交数据(post)': '', '取值方式': '', '传值变量': '', '取值代码': '', '期望结果类型': '无', '期望结果': 'error'}
#          ]

# RequestsUtils().request_by_step(test_data1)



