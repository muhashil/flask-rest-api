from uuid import uuid4
from time import time

from db import db


CONFIRMATION_EXPIRATION_DELTA = 1800 # 30 menit

class ConfirmationModel(db.Model):
    __tablename__ = 'confirmations'

    id = db.Column(db.String(80), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.confirmed = False
        self.user_id = user_id

    @classmethod
    def find_by_id(cls, id_: str) -> "ConfirmationModel":
        return cls.query.filter_by(id=id_).first()

    @property
    def is_expired(self) -> bool:
        return int(time()) > self.expire_at

    def force_to_expire(self) -> None:
        if not self.is_expired:
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

