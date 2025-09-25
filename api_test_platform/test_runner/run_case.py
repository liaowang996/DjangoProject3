import os
import sys

# 1. 获取框架根目录（common所在的目录，即test_runner的父目录）
# 路径说明：test_runner目录的父目录就是框架根目录（含common、api_testcase等）
FRAMEWORK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 2. 将框架根目录添加到sys.path（确保Python能找到common模块）
if FRAMEWORK_ROOT not in sys.path:
    sys.path.append(FRAMEWORK_ROOT)

import unittest
import datetime
from common import config
from common import HTMLTestReportCN
from common.email_utils import EmailUtils
from common.log_utils import logger

from django.shortcuts import redirect, reverse
from django.contrib import messages
import subprocess
from django.conf import settings
# from common.test_report_generator_utils import TestReportGenerator  # 假设你有报告生成工具


class RunCase():
    def __init__(self):
        # 1. 路径配置（从config读取，避免硬编码）
        self.test_case_path = config.CASE_PATH
        self.test_report_root = config.REPORT_PATH
        self.title = '接口自动化测试报告'
        self.description = f'接口自动化测试报告（环境：{os.getenv("TEST_ENV", "test_env")}）'
        self.tester = '测试-Liaowang'

        # 2. 验证必要目录
        self._validate_dirs()

    def _validate_dirs(self):
        """验证目录存在性"""
        if not os.path.exists(self.test_case_path):
            err_msg = f"测试用例目录不存在: {self.test_case_path}"
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
        if not os.path.isdir(self.test_case_path):
            err_msg = f"测试用例路径不是目录: {self.test_case_path}"
            logger.error(err_msg)
            raise IsADirectoryError(err_msg)

    def get_test_suite(self):
        """收集测试用例（支持按模块筛选，新增：支持指定用例ID）"""
        try:
            logger.info(f"开始收集测试用例，路径: {self.test_case_path}")
            # 1. 获取指定用例ID（优先从命令行参数获取）
            single_case_id = None
            if len(sys.argv) > 1 and sys.argv[1] == '--single-case':
                single_case_id = sys.argv[2] if len(sys.argv) > 2 else os.getenv('SINGLE_CASE_ID')
            selected_case_ids = os.getenv('SELECTED_CASE_IDS')  # 批量执行
            logger.info(f"指定用例ID: {selected_case_ids}")
            # 2. 加载测试用例数据（从MySQL）
            from common.testdata_utils import TestdataUtils
            testdata_utils = TestdataUtils()
            case_list = testdata_utils.def_testcase_data_list_by_mysql()
            logger.info(case_list)
            # 3. 筛选用例（如果指定了用例ID）
            filtered_cases = []
            logger.info(filtered_cases)
            if single_case_id:
                # 单条执行：筛选CaseStepInfo_id匹配的用例
                for case in case_list:
                    for step in case['case_info']:
                        if step.get('case_step_info_id') == single_case_id:
                            filtered_cases.append(case)
                            break
            elif selected_case_ids:
                # 批量执行：筛选CaseStepInfo_id在列表中的用例
                selected_ids = selected_case_ids.split(',')
                for case in case_list:
                    for step in case['case_info']:
                        if step.get('case_step_info_id') in selected_ids:
                            filtered_cases.append(case)
                            break
            else:
                # 全量执行
                filtered_cases = case_list

            if not filtered_cases:
                logger.warning("未找到指定的测试用例")
                return unittest.TestSuite()

            # 4. 动态生成测试套件
            from api_testcase.api_test import generate_test_suite
            if not filtered_cases:
                logger.warning("没有可执行的测试用例")
                return unittest.TestSuite()

            # 确保数据格式正确
            formatted_cases = []
            for case in filtered_cases:
                if isinstance(case, dict) and 'case_id' in case and 'case_info' in case:
                    formatted_cases.append(case)
                else:
                    formatted_cases.append({
                        'case_id': str(hash(str(case))),
                        'case_info': case
                    })

            test_suite = generate_test_suite(formatted_cases)
            case_count = test_suite.countTestCases()
            logger.info(f"用例收集完成，共 {case_count} 个用例")
            return test_suite
        except Exception as e:
            logger.error(f"用例收集失败: {str(e)}", exc_info=True)
            raise

    def _get_report_path(self):
        """生成报告路径（按时间戳命名，避免覆盖）"""
        # 报告目录：根目录/报告标题_时间戳
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        report_dir_name = f"{self.title}_{timestamp}"
        report_dir = os.path.join(self.test_report_root, report_dir_name)
        os.makedirs(report_dir, exist_ok=True)

        # 报告文件：目录/报告标题.html
        report_file = os.path.join(report_dir, f"{self.title}.html")
        logger.info(f"测试报告将保存至: {report_file}")
        return report_file

    def run(self):
        """执行测试并生成报告"""
        try:
            logger.info("=" * 60)
            logger.info("开始接口自动化测试流程")
            logger.info(f"测试环境: {os.getenv('TEST_ENV', 'test_env')}")
            logger.info("=" * 60)

            # 1. 获取测试套件
            test_suite = self.get_test_suite()
            if not test_suite.countTestCases():
                logger.warning("未收集到任何测试用例，终止测试")
                return None

            # 2. 生成报告路径
            report_file = self._get_report_path()

            # 3. 执行测试并生成报告
            with open(report_file, 'wb') as fp:
                runner = HTMLTestReportCN.HTMLTestRunner(
                    stream=fp,
                    title=self.title,
                    description=self.description,
                    tester=self.tester
                )
                result = runner.run(test_suite)

            # 4. 记录测试结果
            logger.info("=" * 60)
            logger.info("测试执行完成，结果统计:")
            logger.info(f"总用例数: {result.testsRun}")
            logger.info(f"通过: {result.success_count}")
            logger.info(f"失败: {len(result.failures)}")
            logger.info(f"错误: {len(result.errors)}")
            logger.info("=" * 60)

            return report_file
        except Exception as e:
            logger.error(f"测试执行异常: {str(e)}", exc_info=True)
            raise

    def generate_email_body(self, report_file):
        """生成邮件正文（动态替换报告链接）"""
        # 假设报告可通过HTTP访问（如部署到服务器），若无则显示本地路径
        report_url = os.getenv('REPORT_URL', f"file://{report_file}")
        body = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试完成通知</title>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <style>
        body {{ margin: 0; padding: 20px; font-family: 'Segoe UI', Roboto, sans-serif; background-color: #f7f9fc; line-height: 1.6; }}
        .email-container {{ max-width: 600px; margin: 0 auto; }}
        .notify-card {{ background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden; }}
        .card-content {{ padding: 40px 30px; text-align: center; }}
        .success-icon {{ color: #28a745; font-size: 60px; margin-bottom: 25px; }}
        .main-title {{ color: #2d3748; font-size: 24px; font-weight: 600; margin: 0 0 15px 0; }}
        .description {{ color: #718096; font-size: 16px; margin: 0 0 30px 0; }}
        .action-button {{ display: inline-block; background-color: #3182ce; color: #fff; font-size: 16px; font-weight: 500; padding: 12px 30px; border-radius: 6px; text-decoration: none; transition: background-color 0.2s; }}
        .action-button:hover {{ background-color: #2c5282; }}
        .footer {{ background-color: #f7fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #edf2f7; }}
        .footer-text {{ color: #a0aec0; font-size: 12px; margin: 0; }}
        .result-stat {{ margin: 20px 0; padding: 15px; background-color: #f7fafc; border-radius: 8px; text-align: left; }}
        .stat-item {{ margin: 8px 0; font-size: 14px; color: #4a5568; }}
    </style>
</head>
<body>
    <div class="email-container">
        <table class="notify-card" width="100%">
            <tr>
                <td class="card-content">
                    <div class="success-icon">
                        <i class="fa fa-check-circle"></i>
                    </div>
                    <h1 class="main-title">自动化测试已完成</h1>
                    <p class="description">您提交的接口自动化测试任务已执行结束，以下是简要结果：</p>

                    <div class="result-stat">
                        <div class="stat-item"><strong>测试环境：</strong>{os.getenv('TEST_ENV', 'test_env')}</div>
                        <div class="stat-item"><strong>总用例数：</strong>{self.get_test_suite().countTestCases()}</div>
                        <div class="stat-item"><strong>报告生成时间：</strong>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>

                    <a href="{report_url}" class="action-button" target="_blank">
                        <i class="fa fa-file-text-o mr-2"></i>查看详细测试报告
                    </a>
                </td>
            </tr>
            <tr>
                <td class="footer">
                    <p class="footer-text">此邮件由自动化测试系统发送，无需回复 | 报告路径：{report_file}</p>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
        """
        return body


    # def run_all_cases(request):
    #     """触发run_case.py执行全量用例"""
    #     try:
    #         run_case_path = os.path.join(settings.FRAMEWORK_DIR, 'test_runner', 'run_case.py')
    #         # 后台执行（避免阻塞请求）
    #         subprocess.Popen(
    #             [settings.PYTHON_EXECUTABLE, run_case_path],
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             text=True
    #         )
    #         messages.success(request, "全量用例执行已启动！请稍后查看报告。")
    #     except Exception as e:
    #         messages.error(request, f"全量执行启动失败：{str(e)}")
    #     return redirect(reverse('api_auto:case_list'))

if __name__ == '__main__':
    try:
        # 1. 执行测试
        runner = RunCase()
        report_file = runner.run()
        if not report_file or not os.path.exists(report_file):
            logger.error("测试报告生成失败，无法发送邮件")
            exit(1)

        # 2. 生成邮件正文并发送
        logger.info("开始准备测试报告邮件")
        email_body = runner.generate_email_body(report_file)
        email_utils = EmailUtils(
            smtp_body=email_body,
            smtp_attch_path=report_file  # 附件添加报告文件
        )

        # 3. 发送邮件（带重试）
        if email_utils.send_email(retry=2):
            logger.info("测试报告邮件发送成功")
        else:
            logger.error("测试报告邮件发送失败")

        logger.info("=" * 60)
        logger.info("接口自动化测试流程全部结束")
        logger.info("=" * 60)
    except Exception as e:
        logger.critical(f"测试流程致命错误: {str(e)}", exc_info=True)
        exit(1)