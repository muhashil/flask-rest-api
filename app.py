import os

from flask import Flask, jsonify
from flask_restful import Api
# from flask_jwt import JWT
from flask_jwt_extended import JWTManager

from db import db
from ma import ma
from blacklist import BLACKLIST
from authentication import authenticate, identity
from resources.user import (
    UserRegister, 
    User, 
    UserLogin, 
    UserTokenRefresh, 
    UserLogout, 
    # UserEmailActivation
)

from resources.confirmation import UserConfirmation
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True # allowing blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh'] # allowing token blacklist for access & refresh token

api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

# jwt = JWT(app, authenticate, identity)
jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}

# Check apakah token termasuk dalam daftar blacklist, lihat config["JWT_BLACKLIST_ENABLED"]
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({'message': 'The token has expired', 'action': False}), 401

# Callback jika token sudah expired
# Bawaan sudah ada, ini digunakan jika hendak melakukan modifikasi
@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({'message': 'The token is not fresh.', 'action': False}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': 'Request header does not contain an access token', 'action': False}), 401

# Callback jika token tidak benar
# Bawaan sudah ada, ini digunakan jika hendak melakukan modifikasi
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Invalid token.', 'action': False}), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({'message': 'The token has been revoked', 'action': False}), 401


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:id_>')
# api.add_resource(UserEmailActivation, '/user/activate/<int:user_id>')
api.add_resource(UserConfirmation, '/confirm_user/<string:confirmation_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserTokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    db.init_app(app)
    ma.init_app(app)

    app.run(debug=True, port=5000)
