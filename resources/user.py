from werkzeug.security import safe_str_cmp

from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    jwt_refresh_token_required)

from models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help='This field cannot be blanked!'
    )

    parser.add_argument('password',
        type=str,
        required=True,
        help='This field cannot be blanked!'
    )

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            username = data['username']
            return {'message': f'A user with username `{username}` already exists.'}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message': 'User successfully created.'}, 201


class User(Resource):
    def get(self, id_):
        user = UserModel.find_by_id(id_)
        if not user:
            return {'message': 'User not found.'}, 404

        return user.json()

    def delete(self, id_):
        user = UserModel.find_by_id(id_)
        if not user:
            return {'message': 'User not found.'}, 404

        user.delete_from_db()
        return {'message': 'User deleted.'}, 204


class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help='This field cannot be blanked!'
    )

    parser.add_argument('password',
        type=str,
        required=True,
        help='This field cannot be blanked!'
    )

    def post(self):
        # get data from parser
        data = UserLogin.parser.parse_args()
        # get user from database
        user = UserModel.find_by_username(data['username'])
        # check user password
        if user and safe_str_cmp(user.password, data['password']):
            # create access token
            # create refresh token
            # return token
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200

        return {'message': 'Invalid credentials.'}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # jti => JWT ID, unique identifier of JWT
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {'message': 'User <id:{}> successfully logged out.'.format(user_id)}, 200


class UserTokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        user_id = get_jwt_identity()
        new_token = create_access_token(identity=user_id, fresh=False)
        return {'access_token': new_token}, 200