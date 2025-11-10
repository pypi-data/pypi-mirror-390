import smtplib
from email.mime.text import MIMEText
from typing import List

from ghkit.messenger.error import LoginError, SendError


def send(
    host: str,
    sender: str,
    password: str,
    recipients: List[str],
    subject: str = "",
    msg: str = "",
    msg_type="plain",
):
    """
    发送消息到邮箱
    :param host:
    :param sender:
    :param password:
    :param recipients:
    :param subject:
    :param msg:
    :param msg_type:
    :return:
    """
    with smtplib.SMTP_SSL(host) as server:
        try:
            server.login(sender, password)
        except Exception as e:
            raise LoginError(e) from e

        msg = MIMEText(msg, msg_type)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        try:
            server.sendmail(sender, recipients, msg.as_string())
        except Exception as e:
            raise SendError(e) from e
