from typing import Dict, Union
from requests import Response
from flask import url_for, request

from db import db
from libs.mailgun import Mailgun, MailgunException

UserJSON = Dict[str, Union[int, str]]

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=False)

    def __init__(self, username: str, password: str, email: str=None):
        self.username = username
        self.password = password
        self.email = email

    def json(self) -> UserJSON:
        return {'id': self.id, 'username': self.username}

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, id_: int) -> "UserModel":
        return cls.query.filter_by(id=id_).first()

    def send_confirmation_email(self) -> Response:
        confirmation_link = request.url_root[:-1] + url_for('useremailactivation', user_id=self.id)

        subject = 'Registration confirmation'
        text = f'Please confirm your email using the following link: {confirmation_link}'
        html = f'<html>Please confirm your email using the following link: <a href="{confirmation_link}">{confirmation_link}</a></html>'

        return Mailgun.send_email([self.email], subject, text, html)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
