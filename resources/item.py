import sqlite3

from flask_restful import Resource, reqparse
# from flask_jwt import jwt_required
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity, fresh_jwt_required

from models.item import ItemModel
from models.store import StoreModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field cannot be blanked!"
    )

    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item need a store id."
    )

    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found.'}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': f'An item with name `{name}` already exists.'}, 400

        data = Item.parser.parse_args()

        if not StoreModel.find_by_id(data['store_id']):
            return {'message': 'Invalid `store_id`.'}

        item = ItemModel(name, **data)
        item.save_to_db()

        return item.json(), 201

    @jwt_required
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete()

        return {'message': 'Item deleted.'}, 204

    def put(self, name):
        data = Item.parser.parse_args()

        if not StoreModel.find_by_id(data['store_id']):
            return {'message': 'Invalid `store_id`.'}

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()
        return item.json(), 200


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'More data available if you log in.'}
