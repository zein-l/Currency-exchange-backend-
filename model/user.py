from model import db, ma

class User(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    email        = db.Column(db.String(120))

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        fields = ("id","firebase_uid","email")

user_schema = UserSchema()
