from ma import ma
from models.store import StoreModel
from schemas.item import ItemSchema

class StoreSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)

    class Meta:
        model = StoreModel
        dump_only = ('id', 'items')
        load_instance = True
