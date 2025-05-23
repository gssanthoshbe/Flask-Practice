from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from flask_smorest import Blueprint,abort
from flask.views import MethodView
from schemas import StoreSchema
from flask_jwt_extended import jwt_required,get_jwt
from db import db
from models import StoreModel

blp = Blueprint("Stores",__name__,description = "Operations on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @jwt_required()
    @blp.response(200,StoreSchema)
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    def delete(self,store_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401,message = "Admin privilage required")
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return{"Message":"Store Deleted"}   

@blp.route("/store")
class StoreList(MethodView): 

    @jwt_required()
    @blp.response(200,StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required()    
    @blp.arguments(StoreSchema)
    @blp.response(201,StoreSchema)
    def post(self,requestBody):
        new_store =StoreModel(**requestBody)
        try:
            db.session.add(new_store)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A store with that name already exists."
            )
        except SQLAlchemyError:
            abort(
                500,
                message="An error occurred creating the store."
            )
        return new_store,201

