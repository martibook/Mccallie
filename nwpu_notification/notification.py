import logging
import time

import datetime
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
from requests import get


logger = logging.getLogger('notify')
logging.basicConfig(level=logging.INFO, filename='log.txt')

msg_template = """
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, user-scalable=no,
initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="ie=edge">
<title>Message</title>
</head>
<body>
{content}
</body>
</html>
"""

source_url = "http://guoji.nwpu.edu.cn/tzgg.htm"
ahead_url = 'http://guoji.nwpu.edu.cn/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/39.0.2171.95 Safari/537.36'}

css_query = 'table a[title]'


# email will send to this address
receiver = 'mail_address@example.com'
account = 'mail_address@example.com' # your email address
password = 'password'            # your password
email_host = "smtp.example.com"   # the email server host
email_port = 587             # the server's port


def create_email_server():
    server = smtplib.SMTP(email_host, email_port)
    server.set_debuglevel(0)
    server.ehlo()
    server.starttls()
    server.login(account, password)
    return server


def create_email(receiver, content, subject):
    # 创建一个带附件的实例
    msg = MIMEMultipart()
    # 邮件头
    msg['from'], msg['to'] = account, receiver
    # 添加内容
    msg.attach(MIMEText(content, 'html', 'utf-8'))
    # 指定主题
    msg['subject'] = Header(subject, 'utf-8')
    return msg


def send_email(receiver, subject, content):
    try:
        with create_email_server() as server:
            msg = create_email(receiver, content, subject)
            server.sendmail(account, receiver, msg.as_string())

            now = datetime.datetime.now()
            print('An email sent at {now}.'.format(now=now))
            logger.info('An email sent at {now}.'.format(now=now))
    except Exception as e:
        print('Can not send email because: {e}'.format(e=e))
        logger.error('Can not send email because: {e}'.format(e=e))


def request():
    try:
        response = get(url=source_url, headers=headers)
        dom = BeautifulSoup(response.content, 'html.parser')

        titles = []
        for a in dom.select(css_query):
            url = ahead_url + a['href']
            title = a['title']
            titles.append('<a href="{url}">{title}</a>'.format(url=url, title=title))
        return titles
    except Exception as e:
        print('An error occurred when get information from website: {e}'.format(e=e))
        logger.error('An error occurred when get information from website: {e}'.format(e=e))


if __name__ == '__main__':
    print('Start!')
    logger.info('Start!')

    history_titles = []
    while True:
        titles = request()
        new_titles = [title for title in titles if title not in history_titles]
        if new_titles:
            content = msg_template.format(content='<br>\n<br>\n'.join(new_titles))
            send_email(receiver, '通知公告更新推送', content)
            history_titles = titles

        print('Sleeping...')
        logger.info('Sleeping...')
        time.sleep(60 * 60 * 1)
