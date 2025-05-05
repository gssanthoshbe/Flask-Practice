from db import db

class UserModel(db.Model):

    id = db.Column(db.Integer,primary_key =True)
    username = db.Column(db.String(30),unique=True,nullable=False)
    password = db.Column(db.String(30),nullable=False)