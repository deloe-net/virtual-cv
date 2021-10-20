#  Copyright 2021 Ismael Lugo <ismaelrlg.dev@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password

    def draft(self, to: str, subject: str, text: str = None, html: str = None):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.__username
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        return msg

    def send_mail(self, draft):
        server = smtplib.SMTP(self.__host, self.__port)
        # server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(self.__username, self.__password)
        server.sendmail(draft['From'], draft['To'], draft.as_string())
        server.quit()


# Step 4 - Declare SMTP credentials
# yandex_pass = "q0S5i41%CR#B2LMQ"
# yandex_mail = "noreply@deloe.net"
# host 'smtp.yandex.com'
# port 587
