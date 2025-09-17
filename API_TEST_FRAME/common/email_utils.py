import os.path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from common import config
from common.log_utils import logger


class EmailUtils():
    def __init__(self, smtp_body, smtp_attch_path=None):
        """
        初始化邮件配置
        :param smtp_body: 邮件正文内容
        :param smtp_attch_path: 附件路径，默认为None（无附件）
        """
        # 加载邮件配置并验证
        self._load_and_validate_config()

        self.smtp_body = smtp_body  # 邮件正文
        self.smtp_attch = self._validate_attachment_path(smtp_attch_path)  # 附件路径

        logger.info("邮件工具初始化完成")

    def _load_and_validate_config(self):
        """加载并验证邮件配置参数"""
        required_configs = [
            'SMTP_SERVER', 'SMTP_PORT', 'SMTP_PASSWORD',
            'SMTP_SENDER', 'SMTP_RECEIVER'
        ]

        # 检查必要配置是否存在
        for config_name in required_configs:
            if not hasattr(config, config_name):
                error_msg = f"邮件配置缺失: {config_name} 未在config中定义"
                logger.error(error_msg)
                raise AttributeError(error_msg)

        # 加载配置
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.smtp_password = config.SMTP_PASSWORD  # 授权码
        self.smtp_sender = config.SMTP_SENDER  # 发件人邮箱
        self.smtp_receiver = config.SMTP_RECEIVER  # 收件人，多个用逗号分隔
        self.smtp_cc = getattr(config, 'SMTP_CC', '')  # 抄送，多个用逗号分隔，可选配置
        self.smtp_subject = getattr(config, 'SMTP_SUBJECT', '自动化测试报告')  # 邮件主题，默认值

        logger.debug(f"加载邮件配置: 服务器={self.smtp_server}, 端口={self.smtp_port}, 发件人={self.smtp_sender}")

    def _validate_attachment_path(self, attch_path):
        """验证附件路径是否有效"""
        if not attch_path:
            return None

        # 处理相对路径
        normalized_path = os.path.abspath(attch_path)

        if not os.path.exists(normalized_path):
            logger.warning(f"附件路径不存在: {normalized_path}")
            return None

        if not os.path.isfile(normalized_path):
            logger.warning(f"附件路径不是文件: {normalized_path}")
            return None

        logger.debug(f"验证附件路径成功: {normalized_path}")
        return normalized_path

    def mail_message_body(self):
        """构建邮件内容（包括正文和附件）"""
        try:
            messages = MIMEMultipart()
            messages['From'] = self.smtp_sender
            messages['To'] = self.smtp_receiver
            messages['Cc'] = self.smtp_cc
            messages['Subject'] = self.smtp_subject

            # 添加HTML正文
            messages.attach(MIMEText(self.smtp_body, 'html', 'utf-8'))
            logger.debug("已添加邮件正文")

            # 添加附件（如果有）
            if self.smtp_attch:
                with open(self.smtp_attch, 'rb') as f:
                    attach_file = MIMEText(f.read(), 'base64', 'utf-8')

                attach_file['Content-Type'] = 'application/octet-stream'
                # 处理中文文件名
                filename = os.path.basename(self.smtp_attch)
                attach_file.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=('utf-8', '', filename)
                )
                messages.attach(attach_file)
                logger.debug(f"已添加附件: {filename}")

            return messages
        except Exception as e:
            logger.error(f"构建邮件内容失败: {str(e)}", exc_info=True)
            raise

    def send_email(self):
        """发送邮件"""
        smtp = None
        try:
            # 建立连接
            logger.info(f"开始连接邮件服务器: {self.smtp_server}:{self.smtp_port}")
            smtp = smtplib.SMTP_SSL(
                self.smtp_server,
                self.smtp_port,
                local_hostname='localhost'
            )

            # 登录邮箱
            logger.info(f"登录邮箱: {self.smtp_sender}")
            smtp.login(self.smtp_sender, self.smtp_password)

            # 处理收件人和抄送人列表
            receivers = []
            if self.smtp_receiver:
                receivers.extend([addr.strip() for addr in self.smtp_receiver.split(',') if addr.strip()])
            if self.smtp_cc:
                receivers.extend([addr.strip() for addr in self.smtp_cc.split(',') if addr.strip()])

            # 去重处理
            receivers = list(set(receivers))
            if not receivers:
                logger.warning("没有有效的收件人，取消发送邮件")
                return False

            logger.info(f"准备发送邮件到: {', '.join(receivers)}")

            # 发送邮件
            smtp.sendmail(
                self.smtp_sender,
                receivers,
                self.mail_message_body().as_string()
            )

            logger.info("邮件发送成功")
            return True
        except smtplib.SMTPException as e:
            logger.error(f"SMTP错误导致邮件发送失败：{str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"邮件发送失败：{str(e)}", exc_info=True)
            return False
        finally:
            # 确保连接关闭
            if smtp:
                try:
                    smtp.quit()
                    logger.debug("SMTP连接已关闭")
                except Exception as e:
                    logger.warning(f"关闭SMTP连接失败：{str(e)}")


if __name__ == '__main__':
    # 测试邮件发送
    try:
        # 构建测试用的HTML正文
        test_body = """
        <html>
        <body>
            <h3>接口自动化测试报告</h3>
            <p>测试已完成，详情请查看附件报告</p>
        </body>
        </html>
        """

        # 计算报告路径（实际使用时应从配置或参数获取）
        html_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            config.REPORT_PATH,
            '接口自动化测试报告V1.0/接口自动化测试报告V1.0.html'
        )
        html_path = os.path.abspath(html_path)

        # 发送带附件的测试邮件
        email = EmailUtils(
            smtp_body=test_body,
            smtp_attch_path=html_path
        )
        email.send_email()
    except Exception as e:
        logger.error(f"测试邮件发送失败: {str(e)}")
