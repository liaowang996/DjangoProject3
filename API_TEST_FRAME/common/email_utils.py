import os.path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from common import config

# 计算报告路径
html_path = os.path.join(
    os.path.dirname(__file__),
    '..',
    config.REPORT_PATH,
    '接口自动化测试报告V1.0/接口自动化测试报告V1.0.html'
)
# 规范化路径（处理..等相对路径）
html_path = os.path.abspath(html_path)


class EmailUtils():
    def __init__(self, smtp_body, smtp_attch_path=None):
        """
        初始化邮件配置
        :param smtp_body: 邮件正文内容
        :param smtp_attch_path: 附件路径，默认为None（无附件）
        """
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.smtp_password = config.SMTP_PASSWORD  # 授权码
        self.smtp_sender = config.SMTP_SENDER  # 发件人邮箱
        self.smtp_receiver = config.SMTP_RECEIVER  # 收件人，多个用逗号分隔
        self.smtp_cc = config.SMTP_CC  # 抄送，多个用逗号分隔
        self.smtp_subject = config.SMTP_SUBJECT  # 邮件主题
        self.smtp_attch = smtp_attch_path  # 附件路径
        self.smtp_body = smtp_body  # 邮件正文

    def mail_message_body(self):
        """构建邮件内容（包括正文和附件）"""
        # 关键修正：创建MIMEMultipart实例时需要加括号
        messages = MIMEMultipart()
        messages['From'] = self.smtp_sender
        messages['To'] = self.smtp_receiver
        messages['Cc'] = self.smtp_cc
        messages['Subject'] = self.smtp_subject

        # 添加HTML正文
        messages.attach(MIMEText(self.smtp_body, 'html', 'utf-8'))

        # 添加附件（如果有）
        if self.smtp_attch and os.path.exists(self.smtp_attch):
            try:
                with open(self.smtp_attch, 'rb') as f:
                    attach_file = MIMEText(f.read(), 'base64', 'utf-8')

                attach_file['Content-Type'] = 'application/octet-stream'
                # 处理中文文件名，使用utf-8编码
                filename = os.path.basename(self.smtp_attch)
                attach_file.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=('utf-8', '', filename)
                )
                messages.attach(attach_file)
            except Exception as e:
                print(f"添加附件失败: {str(e)}")
        elif self.smtp_attch:
            print(f"附件路径不存在: {self.smtp_attch}")

        return messages

    def send_email(self):
        """发送邮件"""
        smtp = None  # 初始化smtp变量，避免finally中引用未定义变量
        try:
            # 建立SSL连接
            smtp = smtplib.SMTP_SSL(
                self.smtp_server,
                self.smtp_port,
                local_hostname='localhost'
            )
            # 登录邮箱
            smtp.login(self.smtp_sender, self.smtp_password)

            # 处理收件人和抄送人列表
            receivers = []
            if self.smtp_receiver:
                receivers.extend(self.smtp_receiver.split(','))
            if self.smtp_cc:
                receivers.extend(self.smtp_cc.split(','))
            # 去重处理
            receivers = list(set(receivers))

            # 发送邮件
            smtp.sendmail(
                self.smtp_sender,
                receivers,
                self.mail_message_body().as_string()
            )
            print("邮件发送成功")
            return True
        except Exception as e:
            print(f"邮件发送失败：{str(e)}")
            return False
        finally:
            # 确保连接关闭
            if smtp:
                try:
                    smtp.quit()
                except Exception as e:
                    print(f"关闭SMTP连接失败：{str(e)}")


if __name__ == '__main__':
    # 测试邮件发送
    # 构建测试用的HTML正文
    test_body = """
    <html>
    <body>
        <h3>接口自动化测试报告</h3>
        <p>测试已完成，详情请查看附件报告</p>
    </body>
    </html>
    """
    # 发送带附件的测试邮件
    email = EmailUtils(
        smtp_body=test_body,
        smtp_attch_path=html_path  # 使用上面计算的报告路径作为附件
    )
    email.send_email()
