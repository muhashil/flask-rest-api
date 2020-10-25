from flask import request
from flask_restful import Resource, reqparse
from models.store import StoreModel
from schemas.store import StoreSchema

store_schema = StoreSchema()


class Store(Resource):
    # parser = reqparse.RequestParser()
    # parser.add_argument('name', type=str, required=True, help='This field cannot be blanked.')

    def get(self, name):
        store = StoreModel.find_by_name(name=name)
        if store:
            return store_schema.dump(store), 200
        return {'message': f'Store with name `{name}` not found.'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'message': f'Store with name `{name}` already exists.'}

        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except Exception:
            return {'message': 'Error when inserting store'}, 500
        return {'message': 'Store successfully created.'}, 201

    def delete(self, name):
        store = StoreModel.find_by_name(name=name)
        if store:
            store.delete_from_db()
        return {'message': 'Store deleted.'}, 204

class StoreList(Resource):
    def get(self):
        return {'stores': StoreSchema(many=True).dump(StoreModel.find_all())}