from typing import Dict, Union

from db import db

UserJSON = Dict[str, Union[int, str]]

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
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
    def find_by_id(cls, id_: int) -> "UserModel":
        return cls.query.filter_by(id=id_).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
