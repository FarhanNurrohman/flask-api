from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models import ItemModel
import uuid
from db import db
from sqlalchemy.exc import SQLAlchemyError
from schemas import ItemSchema, ItemUpdateSchema
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("item", __name__, description="Operation on item")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    @jwt_required()
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message":"Item Deleted"}, 200

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemUpdateSchema)
    def put(self,item_requet, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_requet["price"]
            item.name = item_requet["name"]
        else:
            item = ItemModel(id = item_id,**item_requet)
        db.session.add(item)
        db.session.commit()

        return item
        
@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    @jwt_required()
    def get(self):
        return ItemModel.query.all()
    
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    @jwt_required(fresh=True)
    def post(self,item_request):
        item = ItemModel(**item_request)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the item")
            
        return item


    