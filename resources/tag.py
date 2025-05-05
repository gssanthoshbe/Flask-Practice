from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from flask_smorest import Blueprint,abort
from flask.views import MethodView
from db import db
from flask_jwt_extended import jwt_required
from schemas import TagSchema,ItemTagSchema
from models import TagModel,StoreModel,ItemModel

blp = Blueprint("tags",__name__,description="Operations on Tags")

@blp.route("/tag")
class TagList(MethodView):

    @jwt_required()
    @blp.response(200,TagSchema(many=True))
    def get(self):
        return TagModel.query.all()
    
@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):

    @jwt_required()
    @blp.response(200,TagSchema)
    def get(self,tag_id):
        return TagModel.query.get_or_404(tag_id)

    @jwt_required()    
    @blp.response(200,description="deletes a tag",example={"message": "Tag deleted."})
    @blp.alt_response(400,example={"message": "Could not delete tag. Make sure tag is not associated with any items, then try again."})
    @blp.alt_response(404,description="Tag not found")
    def delete(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            try:
                db.session.delete(tag)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="An error occurred while deleting the tag.")
            return {"message": "Tag deleted."}
        abort(400,message="Could not delete tag. Make sure tag is not associated with any items, then try again.")

@blp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView):

    @jwt_required()
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @jwt_required()    
    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self,tag_data,store_id):
        new_tag = TagModel(**tag_data,store_id=store_id)
        try:
            db.session.add(new_tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")
        return new_tag

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")    
class ItemTag(MethodView):

    @jwt_required()
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if item.store_id == tag.store_id:
            item.tags.append(tag)
            try:
                db.session.add(item)
                db.session.commit()
            except IntegrityError as i:
                if "UNIQUE constraint failed: itemtags.item_id, itemtags.tag_id'" in str(i._sql_message):
                    abort(500, message="The item is already linked to the tag ")
            except SQLAlchemyError as e:
                #pass
                abort(500, message="An error occurred while linking the tag. "+str(e._sql_message))
            return tag
        else:
            abort(400,"Make sure item and tag belong to the same store before linking. and not linked already")

    @jwt_required()    
    @blp.response(200,ItemTagSchema)
    def delete(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the tag link.")
        return {"message": "Item removed from tag", "item": item, "tag": tag} 

