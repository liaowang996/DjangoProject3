import json
from datetime import datetime
from typing import Dict, List


class TestReportGenerator:
    """测试报告生成器，根据测试结果生成HTML邮件正文"""

    def __init__(self):
        # 初始化HTML模板
        self.html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API自动化测试报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.8/dist/chart.umd.min.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#165DFF',
                        success: '#00B42A',
                        warning: '#FF7D00',
                        danger: '#F53F3F',
                        gray: {
                            100: '#F2F3F5',
                            200: '#E5E6EB',
                            300: '#C9CDD4',
                            400: '#86909C',
                            500: '#4E5969',
                            600: '#272E3B',
                            700: '#1D2129',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        .shadow-soft { box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); }
        .hover-row:hover { background-color: #F2F3F5; }
    </style>
</head>
<body class="bg-gray-100 font-sans text-gray-700">
    <div class="max-w-5xl mx-auto bg-white shadow-soft rounded-lg overflow-hidden">
        <!-- 报告头部 -->
        <header class="bg-primary text-white p-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center">
                <div>
                    <h1 class="text-2xl font-bold mb-2">API自动化测试报告</h1>
                    <p class="opacity-90">测试执行结果详情</p>
                </div>
                <div class="mt-4 md:mt-0 bg-white/10 px-4 py-2 rounded text-sm">
                    <p>生成时间: {{generate_time}}</p>
                </div>
            </div>
        </header>

        <!-- 测试摘要 -->
        <section class="p-6 border-b border-gray-200">
            <h2 class="text-xl font-bold mb-6 text-gray-700 flex items-center">
                <i class="fa fa-bar-chart mr-2 text-primary"></i>测试摘要
            </h2>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
                    <p class="text-gray-500 text-sm mb-1">总用例数</p>
                    <p class="text-3xl font-bold text-gray-700">{{total_cases}}</p>
                </div>
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
                    <p class="text-gray-500 text-sm mb-1">通过用例</p>
                    <p class="text-3xl font-bold text-success">{{passed_cases}}</p>
                </div>
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
                    <p class="text-gray-500 text-sm mb-1">失败用例</p>
                    <p class="text-3xl font-bold text-danger">{{failed_cases}}</p>
                </div>
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
                    <p class="text-gray-500 text-sm mb-1">通过率</p>
                    <p class="text-3xl font-bold text-primary">{{pass_rate}}%</p>
                </div>
            </div>

            <div class="mt-6">
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
                    <h3 class="text-base font-semibold mb-3 text-gray-700">测试结果分布</h3>
                    <div class="h-64">
                        <canvas id="resultChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- 测试详情 -->
        <section class="p-6 border-b border-gray-200">
            <h2 class="text-xl font-bold mb-6 text-gray-700 flex items-center">
                <i class="fa fa-list-alt mr-2 text-primary"></i>测试用例详情
            </h2>

            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead>
                        <tr>
                            <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用例ID</th>
                            <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">模块</th>
                            <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">接口名称</th>
                            <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">请求方式</th>
                            <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                            <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">耗时(秒)</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {{test_cases_table}}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- 失败用例详情 -->
        <section class="p-6 border-b border-gray-200">
            <h2 class="text-xl font-bold mb-6 text-gray-700 flex items-center">
                <i class="fa fa-exclamation-circle mr-2 text-danger"></i>失败用例详情
            </h2>

            <div class="space-y-4">
                {{failed_cases_details}}
            </div>
        </section>

        <!-- 环境信息 -->
        <section class="p-6 bg-gray-50">
            <h2 class="text-xl font-bold mb-6 text-gray-700 flex items-center">
                <i class="fa fa-cogs mr-2 text-primary"></i>测试环境信息
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="text-base font-semibold mb-3 text-gray-700">执行信息</h3>
                    <ul class="space-y-2 text-sm">
                        <li class="flex"><span class="w-24 text-gray-500">开始时间:</span> <span>{{start_time}}</span></li>
                        <li class="flex"><span class="w-24 text-gray-500">结束时间:</span> <span>{{end_time}}</span></li>
                        <li class="flex"><span class="w-24 text-gray-500">总耗时:</span> <span>{{total_duration}}秒</span></li>
                    </ul>
                </div>
                <div>
                    <h3 class="text-base font-semibold mb-3 text-gray-700">环境配置</h3>
                    <ul class="space-y-2 text-sm">
                        <li class="flex"><span class="w-24 text-gray-500">API地址:</span> <span>{{api_base_url}}</span></li>
                        <li class="flex"><span class="w-24 text-gray-500">测试环境:</span> <span>{{test_environment}}</span></li>
                    </ul>
                </div>
            </div>
        </section>
    </div>

    <script>
        // 初始化图表
        window.onload = function() {
            const ctx = document.getElementById('resultChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: {{module_labels}},
                    datasets: [
                        {
                            label: '通过',
                            data: {{passed_data}},
                            backgroundColor: '#00B42A',
                            stack: 'Stack 0'
                        },
                        {
                            label: '失败',
                            data: {{failed_data}},
                            backgroundColor: '#F53F3F',
                            stack: 'Stack 0'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        x: {
                            stacked: true
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        };
    </script>
</body>
</html>"""

    def generate(self, test_results: Dict) -> str:
        """
        生成HTML测试报告
        :param test_results: 测试结果数据字典
        :return: HTML格式的报告内容
        """
        # 计算通过率
        pass_rate = 0
        if test_results['total_cases'] > 0:
            pass_rate = round((test_results['passed_cases'] / test_results['total_cases']) * 100, 2)

        # 生成测试用例表格
        test_cases_table = ""
        for case in test_results['test_cases']:
            # 设置状态样式
            if case['result'] == 'passed':
                status_class = 'bg-green-100 text-success'
                status_text = '通过'
            else:
                status_class = 'bg-red-100 text-danger'
                status_text = '失败'

            test_cases_table += f"""
            <tr class="hover-row transition-colors">
                <td class="px-4 py-3 whitespace-nowrap text-sm">{case['case_id']}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm">{case['module']}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm">{case['api_name']}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm">{case['method']}</td>
                <td class="px-4 py-3 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {status_class}">
                        {status_text}
                    </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm">{case['duration']:.4f}</td>
            </tr>"""

        # 生成失败用例详情
        failed_cases_details = ""
        if test_results['failed_cases']:
            for case in test_results['failed_cases']:
                failed_cases_details += f"""
                <div class="border border-danger/30 bg-danger/5 p-4 rounded-lg">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-semibold text-danger">{case['case_id']}: {case['case_name']}</h3>
                            <p class="text-sm text-gray-600 mt-1">
                                模块: {case['module']} | 接口: {case['api_name']} ({case['method']})
                            </p>
                        </div>
                    </div>
                    <div class="mt-3 bg-white p-3 rounded border border-gray-200 text-sm">
                        <p class="text-gray-600 mb-2"><span class="font-medium">错误信息:</span> {case['error_msg']}</p>
                        <p class="text-gray-600"><span class="font-medium">耗时:</span> {case['duration']:.4f}秒</p>
                    </div>
                </div>"""
        else:
            failed_cases_details = """
            <div class="text-center py-6 text-gray-600">
                <i class="fa fa-check-circle text-success text-3xl mb-2"></i>
                <p>所有测试用例均通过验证</p>
            </div>"""

        # 准备图表数据
        module_labels = json.dumps(list(test_results['module_stats'].keys()))
        passed_data = json.dumps([v['passed'] for v in test_results['module_stats'].values()])
        failed_data = json.dumps([v['failed'] for v in test_results['module_stats'].values()])

        # 替换模板中的占位符
        html_content = self.html_template \
            .replace('{{generate_time}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S')) \
            .replace('{{total_cases}}', str(test_results['total_cases'])) \
            .replace('{{passed_cases}}', str(test_results['passed_cases'])) \
            .replace('{{failed_cases}}', str(test_results['failed_cases'])) \
            .replace('{{pass_rate}}', str(pass_rate)) \
            .replace('{{start_time}}', test_results['start_time']) \
            .replace('{{end_time}}', test_results['end_time']) \
            .replace('{{total_duration}}', str(round(test_results['total_duration'], 2))) \
            .replace('{{api_base_url}}', test_results['environment']['api_base_url']) \
            .replace('{{test_environment}}', test_results['environment']['test_environment']) \
            .replace('{{test_cases_table}}', test_cases_table) \
            .replace('{{failed_cases_details}}', failed_cases_details) \
            .replace('{{module_labels}}', module_labels) \
            .replace('{{passed_data}}', passed_data) \
            .replace('{{failed_data}}', failed_data)

        return html_content


# 在测试框架中集成的方式
def integrate_with_test_framework():
    # 1. 在测试基类中添加结果收集
    """
    在APITestBase类中添加:
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_results = {
            'total_cases': 0,
            'passed_cases': 0,
            'failed_cases': 0,
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': '',
            'total_duration': 0,
            'test_cases': [],
            'failed_cases': [],
            'module_stats': {},
            'environment': {
                'api_base_url': config.URL,  # 从配置获取
                'test_environment': '测试环境'  # 可从配置获取
            }
        }
    """

    # 2. 在测试方法中记录结果
    """
    在test_api_request方法中添加:
    # 记录用例结果
    case_result = {
        'case_id': self.case_id,
        'case_name': self._testMethodDoc,
        'module': self.case_info[0].get('模块名称', '未知'),
        'api_name': self.case_info[0].get('接口名称', ''),
        'method': self.case_info[0].get('请求方式', ''),
        'duration': duration,
        'result': 'passed'  # 或 'failed'
    }

    # 更新统计信息
    self.__class__.test_results['total_cases'] += 1
    if case_result['result'] == 'passed':
        self.__class__.test_results['passed_cases'] += 1
    else:
        self.__class__.test_results['failed_cases'] += 1
        case_result['error_msg'] = str(ae)  # 错误信息
        self.__class__.test_results['failed_cases'].append(case_result)

    self.__class__.test_results['test_cases'].append(case_result)
    """

    # 3. 在测试结束时生成报告
    """
    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.test_results['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cls.test_results['total_duration'] = time.time() - cls.start_time

        # 生成HTML报告
        generator = TestReportGenerator()
        html_content = generator.generate(cls.test_results)

        # 这里调用你自己的邮件发送功能
        # send_email(html_content)
    """


# 使用示例
if __name__ == "__main__":
    # 示例测试结果数据
    sample_results = {
        "total_cases": 15,
        "passed_cases": 12,
        "failed_cases": 3,
        "start_time": "2023-06-18 09:30:00",
        "end_time": "2023-06-18 09:45:30",
        "total_duration": 930,
        "test_cases": [
            {
                "case_id": "case_001",
                "module": "用户管理",
                "api_name": "用户登录",
                "method": "POST",
                "duration": 0.42,
                "result": "passed"
            },
            {
                "case_id": "case_002",
                "module": "商品管理",
                "api_name": "商品列表查询",
                "method": "GET",
                "duration": 0.78,
                "result": "failed"
            }
            # 更多测试用例...
        ],
        "failed_cases": [
            {
                "case_id": "case_002",
                "case_name": "商品列表查询接口测试",
                "module": "商品管理",
                "api_name": "商品列表查询",
                "method": "GET",
                "duration": 0.78,
                "error_msg": "响应结果与预期不符，预期状态码200，实际得到500"
            }
            # 更多失败用例...
        ],
        "module_stats": {
            "用户管理": {"passed": 5, "failed": 1},
            "商品管理": {"passed": 4, "failed": 2},
            "订单管理": {"passed": 3, "failed": 0}
        },
        "environment": {
            "api_base_url": "https://api-test.example.com",
            "test_environment": "测试环境"
        }
    }

    # 生成HTML报告
    generator = TestReportGenerator()
    html_content = generator.generate(sample_results)

    # 保存到文件查看效果
    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("测试报告已生成: test_report.html")
