import os

from typing import List
from requests import Response, post

class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')

    FROM_EMAIL = ''
    FROM_TITLE = ''

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:

        if cls.MAILGUN_API_KEY is None:
            raise MailgunException('Invalid Mailgun API Key.')

        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException('Invalid Mailgun domain.')

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=('api', cls.MAILGUN_API_KEY),
            data={
                'from': f'{cls.FROM_TITLE} <{cls.FROM_EMAIL}>',
                'to': email,
                'subject': subject,
                'text': text,
                'html': html,
            },
        )

        if response.status_code != 200:
            raise MailgunException('Error sending email.')

        return response