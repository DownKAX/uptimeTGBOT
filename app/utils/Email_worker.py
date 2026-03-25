import smtplib
from email.mime.text import MIMEText

import json
from smtplib import SMTP_SSL

from app.core.settings import settings
from redis_client import get_sync_redis


class Email_sender:
    def __init__(self):
        self.r = get_sync_redis()
        self.email = settings.EMAIL_ADDR_SMTP
        self.password = settings.EMAIL_PASS_SMTP

    def send_email(self, server: SMTP_SSL, msg: dict):
        email, msg = iter(msg.items()).__next__()
        msg = MIMEText(msg)
        try:
            server.send_message(msg=msg, to_addrs=email, from_addr=self.email)
        except Exception as e:
            print(f'Email sending failed: {e}')

    def worker(self):
        print('Email worker started')
        while True:
            msg = self.r.blpop('email_codes_for_worker', timeout=2)
            if msg is None:
                continue
            else:
                msg = json.loads(msg[1])
                with smtplib.SMTP_SSL("smtp.mail.ru", 465) as server:
                    server.login(self.email, self.password)
                    self.send_email(server, msg)

# email_worker = Email_sender()
# email_worker.worker()