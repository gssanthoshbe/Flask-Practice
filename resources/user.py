
from sqlalchemy.exc import SQLAlchemyError
from db import db
from schemas import UserSchema
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from models.user import UserModel
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt , jwt_required
from blocklist import BLOCKLIST

blp = Blueprint("Users",__name__,description="Operations on Users")


@blp.route("/users")
class UserList(MethodView):

    @blp.response(200,UserSchema(many=True))
    def get(self):
        return UserModel.query.all()
    
@blp.route("/users/<int:user_id>")
class User(MethodView):

    @blp.response(200,UserSchema)
    def get(self,user_id):
        return UserModel.query.get_or_404(user_id)
    
    def delete(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,"Error Occured while deleting the user")
        return {"message":"User Deleted Successfully"},200

@blp.route("/register")
class UserRegister(MethodView):    
    
    @blp.arguments(UserSchema)
    def post(self,user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            print("user name taken")
            abort(409,message="username already taken")

        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
                         )        
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while registering the user.")

        return {"message":"User Created Successfully"},201
    
    @blp.route("/login")
    class UserLogin(MethodView):

        @blp.arguments(UserSchema)
        def post(self,user_data):
            user = UserModel.query.filter(UserModel.username == user_data["username"]).first()
            if user and  pbkdf2_sha256.verify(user_data["password"],user.password):
                print(type(str(user.id)))
                access_token = create_access_token(identity=str(user.id))
                return {"access_token":access_token},200
            abort(401,message="Invalid Credentials")

    @blp.route("/logout")   
    class UserLogout(MethodView):

        @jwt_required()
        def post(self):
            jti = get_jwt()["jti"]
            BLOCKLIST.add(jti)
            return {"message":"Successfully logged out"},200

    
        