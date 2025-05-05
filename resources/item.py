from sqlalchemy.exc import SQLAlchemyError
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel
from flask_jwt_extended import  jwt_required


blp = Blueprint("Items","items",description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):

    @jwt_required()
    @blp.response(200,ItemSchema)
    def get(self,item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item
    
    @jwt_required()
    def delete(self,item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return{"Message":"Itme Deleted"}   

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(201,ItemSchema)
    def put(self,requestBody,item_id):
        item = ItemModel.query.get_or_404(item_id)
        item.price = requestBody["price"]
        item.name = requestBody["name"]
        db.session.add(item)
        db.session.commit()
        return item


@blp.route("/item")
class ItemList(MethodView):

    @jwt_required()
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(200,ItemSchema)
    def post(self,requestBody):
        new_item = ItemModel(**requestBody)
        try:
            db.session.add(new_item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")
        return new_item