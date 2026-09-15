from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import StoreModel
from db import db
import uuid 
from schemas import StoreSchema

blp = Blueprint("stores", __name__, description="Operation on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message":"store deleted"}
    
    @blp.arguments(StoreSchema)
    def put(self,store_request, store_id):
        store = StoreModel.query.get(store_id)
        if store:
            store.name = store_request["name"]
            #store.items = store_request["items"]
        else:
            store = StoreModel(id=store_id, **store_request)
        db.session.add(store)
        db.session.commit()
        raise NotImplementedError("Updating a store is not implemented")

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self,store_request):
        store = StoreModel(**store_request)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="The store with that name already exist")
        
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the store")

        return store
