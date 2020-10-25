import sqlite3

from flask import request
from flask_restful import Resource, reqparse
# from flask_jwt import jwt_required
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity, fresh_jwt_required
from marshmallow import ValidationError

from models.item import ItemModel
from models.store import StoreModel
from schemas.item import ItemSchema

item_schema = ItemSchema()


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
            return item_schema.dump(item), 200
        return {'message': 'Item not found.'}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': f'An item with name `{name}` already exists.'}, 400

        json_data = request.get_json()
        json_data['name'] = name

        if not StoreModel.find_by_id(json_data['store_id']):
            return {'message': 'Invalid `store_id`.'}

        try:
            item = item_schema.load(json_data)
        except ValidationError as err:
            return err.messages, 400

        item.save_to_db()

        return item_schema.dump(item), 201

    @jwt_required
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete()
            return {'message': 'Item deleted.'}, 204
        return {'message': 'Item not found'}, 404

    def put(self, name):
        json_data = request.get_json()
        json_data['name'] = name

        if not StoreModel.find_by_id(json_data['store_id']):
            return {'message': 'Invalid `store_id`.'}

        item = ItemModel.find_by_name(name)

        if item is None:
            item = item_schema.load(json_data)
        else:
            item.price = json_data['price']
            item.store_id = json_data['store_id']

        item.save_to_db()
        return item_schema.dump(item), 200


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = ItemSchema(many=True).dump(ItemModel.find_all())
        if user_id:
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'More data available if you log in.'}
