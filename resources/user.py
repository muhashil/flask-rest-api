from werkzeug.security import safe_str_cmp

from flask import request, make_response, render_template
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    jwt_refresh_token_required)

from marshmallow import ValidationError
from models.user import UserModel
from models.confirmation import ConfirmationModel
from schemas.user import UserSchema
from blacklist import BLACKLIST


user_schema = UserSchema()


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
        try:
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.username):
            username = user.username
            return {'message': f'A user with username `{username}` already exists.'}, 400

        if UserModel.find_by_email(user.email):
            email = user.email
            return {'message': f'A user with email `{email}` already exists.'}, 400

        user.save_to_db()

        confirmation = ConfirmationModel(user_id=user.id)
        confirmation.save_to_db()

        return {'message': 'User successfully created.'}, 201


class User(Resource):
    def get(self, id_):
        user = UserModel.find_by_id(id_)
        if not user:
            return {'message': 'User not found.'}, 404
        return user_schema.dump(user), 200

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
        try:
            user = user_schema.load(request.get_json(), partial=('email',))
        except ValidationError as err:
            return err.messages, 400

        # get user from database
        existing_user = UserModel.find_by_username(user.username)
        # check user password
        if existing_user and safe_str_cmp(existing_user.password, user.password):
            if existing_user.is_active:
                # create access token
                access_token = create_access_token(identity=existing_user.id, fresh=True)
                # create refresh token
                refresh_token = create_refresh_token(existing_user.id)
                # return token
                return {'access_token': access_token, 'refresh_token': refresh_token}, 200
            return {'message': 'User is not activated. Please check your email.'}, 401

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


class UserEmailActivation(Resource):
    def get(self, user_id: str):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404

        user.is_active = True
        user.save_to_db()

        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('user_verified_page.html', context={'email': user.email}), 200, headers)

        # return {'message': 'User successfully activated.'}, 200