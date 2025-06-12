from model import db, ma
import datetime

class Transaction(db.Model):
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usd_amount = db.Column(db.Float, nullable=False)
    lbp_amount = db.Column(db.Float, nullable=False)
    usd_to_lbp = db.Column(db.Boolean, nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        include_fk = True

transaction_schema  = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
