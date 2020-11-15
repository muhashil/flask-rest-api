from flask_restful import Resource
from flask import make_response, render_template

from models.confirmation import ConfirmationModel

class UserConfirmation(Resource):
    def get(self, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(id_=confirmation_id)

        if not confirmation:
            return {'message': 'Invalid confirmation key'}, 404

        if confirmation.is_expired:
            return {'message': 'Confirmation url already expired.'}, 400

        if confirmation.confirmed:
            return {'message': 'User already confirmed.'}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('user_verified_page.html', email=confirmation.user.email), 200, headers)


class ConfirmationByUser(Resource):
    def get(self, confirmation_id: str):
        pass

    def post(self):
        pass
