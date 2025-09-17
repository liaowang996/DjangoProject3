import os
import unittest
import logging
from common import config, HTMLTestReportCN
from common.email_utils import EmailUtils
from common.log_utils import logger  # 假设你有日志工具类

# 配置路径处理
current_path = os.path.dirname(__file__)
test_case_path = os.path.join(current_path, '..', config.CASE_PATH)
test_report_path = os.path.join(current_path, '..', config.REPORT_PATH)
# 确保报告目录存在
os.makedirs(test_report_path, exist_ok=True)


class RunCase():
    def __init__(self):
        self.test_case_path = test_case_path
        self.test_report_path = test_report_path
        self.title = '接口自动化测试报告'
        self.description = '接口自动化测试报告详情'
        self.tester = '测试-Liaowang'

        # 验证测试用例目录是否存在
        if not os.path.exists(self.test_case_path):
            logger.error(f"测试用例目录不存在: {self.test_case_path}")
            raise FileNotFoundError(f"测试用例目录不存在: {self.test_case_path}")

    def get_test_suite(self):
        """收集测试用例，返回测试套件"""
        try:
            logger.info(f"开始收集测试用例，路径: {self.test_case_path}")
            # 发现指定路径下所有符合模式的测试用例
            discover = unittest.defaultTestLoader.discover(
                start_dir=self.test_case_path,
                pattern='api_test.py',
                top_level_dir=self.test_case_path
            )

            test_suite = unittest.TestSuite()
            test_suite.addTest(discover)

            # 统计测试用例数量
            test_count = test_suite.countTestCases()
            logger.info(f"测试用例收集完成，共 {test_count} 个用例")
            return test_suite
        except Exception as e:
            logger.error(f"收集测试用例失败: {str(e)}", exc_info=True)
            raise

    def run(self):
        """执行测试并生成报告"""
        try:
            logger.info("开始执行接口自动化测试")

            # 创建报告目录
            report_dir = HTMLTestReportCN.ReportDirectory(self.test_report_path)
            report_dir.create_dir(self.title)
            report_file_path = HTMLTestReportCN.GlobalMsg.get_value('report_path')

            logger.info(f"测试报告将保存至: {report_file_path}")

            # 执行测试并生成报告
            with open(report_file_path, 'wb') as fp:
                runner = HTMLTestReportCN.HTMLTestRunner(
                    stream=fp,
                    title=self.title,
                    description=self.description,
                    tester=self.tester
                )
                result = runner.run(self.get_test_suite())

            # 记录测试结果统计
            logger.info(f"测试执行完成: 共 {result.testsRun} 个用例，"
                        f"成功 {result.success_count} 个，"
                        f"失败 {len(result.failures)} 个，"
                        f"错误 {len(result.errors)} 个")

            return report_file_path
        except Exception as e:
            logger.error(f"测试执行过程中发生错误: {str(e)}", exc_info=True)
            raise


if __name__ == '__main__':


    body_str = """
    <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试完成通知</title>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <style>
        /* 基础样式重置，适配邮件客户端 */
        body { 
            margin: 0; 
            padding: 0; 
            font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; 
            background-color: #f7f9fc;
            line-height: 1.5;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            max-width: 600px; 
            margin: 0 auto;
        }
        td { 
            padding: 0; 
        }
        a { 
            text-decoration: none; 
        }
        
        /* 卡片样式 */
        .email-container {
            padding: 20px;
        }
        .notify-card {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            overflow: hidden;
        }
        
        /* 内容区域 */
        .card-content {
            padding: 40px 30px;
            text-align: center;
        }
        .success-icon {
            color: #28a745;
            font-size: 60px;
            margin-bottom: 25px;
        }
        .main-title {
            color: #2d3748;
            font-size: 24px;
            font-weight: 600;
            margin: 0 0 15px 0;
        }
        .description {
            color: #718096;
            font-size: 16px;
            margin: 0 0 30px 0;
            line-height: 1.6;
        }
        
        /* 按钮样式 */
        .action-button {
            display: inline-block;
            background-color: #3182ce;
            color: #ffffff;
            font-size: 16px;
            font-weight: 500;
            padding: 12px 30px;
            border-radius: 6px;
            margin-bottom: 30px;
            transition: background-color 0.2s ease;
        }
        .action-button:hover {
            background-color: #2c5282;
        }
        
        /* 页脚 */
        .footer {
            background-color: #f7fafc;
            padding: 20px 30px;
            text-align: center;
            border-top: 1px solid #edf2f7;
        }
        .footer-text {
            color: #a0aec0;
            font-size: 12px;
            margin: 0;
        }
    </style>
</head>
<body>
    <table class="email-container">
        <tr>
            <td>
                <table class="notify-card">
                    <!-- 卡片内容 -->
                    <tr>
                        <td class="card-content">
                            <div class="success-icon">
                                <i class="fa fa-check-circle"></i>
                            </div>
                            <h1 class="main-title">自动化测试已完成</h1>
                            <p class="description">您提交的测试任务已顺利执行结束</p>
                            <a href="#" class="action-button">查看详细报告</a>
                        </td>
                    </tr>
                    <!-- 页脚 -->
                    <tr>
                        <td class="footer">
                            <p class="footer-text">此邮件由自动化系统发送，无需回复</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    try:
        logger.info("===== 开始接口自动化测试流程 =====")
        html_path = RunCase().run()

        # 发送邮件报告
        if html_path and os.path.exists(html_path):
            logger.info("开始发送测试报告邮件")
            email_utils = EmailUtils(body_str, html_path)
            if email_utils.send_email():
                logger.info("测试报告邮件发送成功")
            else:
                logger.warning("测试报告邮件发送失败")
        else:
            logger.warning("测试报告文件不存在，无法发送邮件")

        logger.info("===== 接口自动化测试流程结束 =====")
    except Exception as e:
        logger.critical(f"测试流程发生致命错误: {str(e)}", exc_info=True)
        exit(1)
