from flask_restful import Resource
from flask import make_response, render_template

from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema


confirmation_schema = ConfirmationSchema()

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
    def get(self, user_id: str):
        user = UserModel.find_by_id(id_=user_id)
        if not user:
            return {'message': 'User not found'}, 404

        return (
            {
                'current_time': int(time()),
                'confirmation': [confirmation_schema.dump(confirmation) for confirmation in user.confirmation.order_by(ConfirmationModel.expire_at)]
            },
            200
        )

    def post(self, user_id: str):
        """
        Resend confirmation email.
        """
        user = UserModel.find_by_id(id_=user_id)
        if not user:
            return {'message': 'User not found'}, 404

        try:
            last_confirmation = user.most_recent_confirmation
            if last_confirmation:
                if last_confirmation.confirmed:
                    return {'message': 'You are already confirmed'}, 400

                last_confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id=user_id)
            new_confirmation.save_to_db()

            return {'message': 'Successfully resend confirmation.'}, 200

        except Exception:
            return {'message': 'Failed to resend confirmation'}, 500