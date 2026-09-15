from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask.views import MethodView
from flask_jwt_extended import (create_access_token, get_jwt, jwt_required, get_jwt_identity, create_refresh_token)
from blocklist import BLOCKLIST

from db import db
from schemas import UserSchema
from models import UserModel

blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/register")
class UserRegist(MethodView):
    @blp.arguments(UserSchema)
    def post(self, data_request):
        if UserModel.query.filter(UserModel.username ==  data_request["username"]).first():
            abort(405, message="A user with that username already exists.")
        user = UserModel(username=data_request["username"], password=pbkdf2_sha256.hash(data_request["password"]))
        db.session.add(user)
        db.session.commit()

        return {"message":"User created successfully."}, 201

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, data_request):
        user  = UserModel.query.filter(UserModel.username == data_request["username"]).first()

        if user and pbkdf2_sha256.verify(data_request["password"], user.password):
            jwt_access = create_access_token(identity=str(user.id), fresh=True)
            refresh_token =  create_refresh_token(identity=str(user.id))
            return {"access_token":jwt_access, "refresh_token":refresh_token}, 200
        
        abort(404, message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(sefl):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message":"Successfully logged out"}, 200

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=True)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token":new_token}, 200
        
