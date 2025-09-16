import smtplib
import os
from common import config
from email.mime.text import MIMEText
from datetime import datetime
from email.mime.multipart import MIMEMultipart


html_path = os.path.join(os.path.dirname(__file__), '..', config.REPORT_PATH,'接口自动化测试报告V1.0/接口自动化测试报告V1.0.html')
print(os.path.basename(html_path))
# 生成当前时间用于报告
current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

# 美化后的邮件内容
body_str = f"""
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333;}}
        .container {{max-width: 800px; margin: 0 auto; padding: 20px;}}
        .header {{background-color: #f5f7fa; padding: 15px 20px; border-radius: 5px; margin-bottom: 20px;}}
        .title {{color: #2c3e50; margin: 0; font-size: 20px;}}
        .subtitle {{color: #666; margin-top: 5px; font-size: 14px;}}
        .content {{background-color: #fff; padding: 20px; border: 1px solid #eee; border-radius: 5px;}}
        .link-box {{margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db; border-radius: 0 4px 4px 0;}}
        .report-link {{color: #3498db; text-decoration: none; font-weight: bold; font-size: 16px;}}
        .report-link:hover {{text-decoration: underline;}}
        .footer {{margin-top: 20px; color: #999; font-size: 12px; text-align: center;}}
        .divider {{border: 0; border-top: 1px dashed #ddd; margin: 15px 0;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 class="title">接口自动化测试报告通知</h2>
            <p class="subtitle">生成时间: {current_time}</p>
        </div>

        <div class="content">
            <p>您好，</p>
            <p>接口自动化测试已执行完成，测试报告已生成，您可以通过以下链接查看详细内容：</p>

            <div class="link-box">
                <a href="http://192.168.1.100:8080/jenkins/job/接口自动化测试/" class="report-link">
                    点击查看完整测试报告 →
                </a>
            </div>

            <hr class="divider">

            <p>报告内容包括：</p>
            <ul>
                <li>测试用例执行结果统计</li>
                <li>失败用例详细日志</li>
                <li>接口响应时间分析</li>
                <li>错误截图及详细信息</li>
            </ul>

            <p>如有任何问题，请及时与测试团队联系。</p>
        </div>

        <div class="footer">
            <p>此邮件为系统自动发送，请勿直接回复 | 接口自动化测试系统</p>
        </div>
    </div>
</body>
</html>
"""

msg = MIMEMultipart()
msg.attach(MIMEText(body_str, 'html', 'utf-8'))
msg['From'] = '821745075@qq.com'
msg['To'] = '821745075@qq.com'
msg['Cc'] = ''  # 抄送地址，没有可以留空
msg['Subject'] = '【测试报告】接口自动化测试结果通知'

attach_file = MIMEText(open(html_path, 'rb').read(), 'base64', 'utf-8')
attach_file['Content-Type'] = 'application/octet-stream'
attach_file.add_header('Content-Disposition','attachment',filename=('gbk','','接口自动化测试报告V1.0.html'))
# attach_file['Content-Disposition'] = 'attachment; filename="test.html"'
msg.attach(attach_file)

# QQ邮箱需要使用SSL连接，端口465
try:
    # 使用SSL连接，指定local_hostname避免中文主机名问题
    smtp = smtplib.SMTP_SSL('smtp.qq.com', 465, local_hostname='localhost')
    # 登录（使用QQ邮箱授权码）
    smtp.login('821745075@qq.com', 'kczeduxhlbbabffd')
    # 发送邮件
    smtp.sendmail('821745075@qq.com', ['821745075@qq.com'], msg.as_string())
    print("邮件发送成功")
except Exception as e:
    print(f"邮件发送失败：{str(e)}")
finally:
    # 关闭连接
    smtp.quit()
