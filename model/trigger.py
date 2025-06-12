from model import db, ma
import datetime

class Trigger(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    base_currency   = db.Column(db.String(3), nullable=False)
    target_currency = db.Column(db.String(3), nullable=False)
    operator        = db.Column(db.String(2), nullable=False)
    threshold       = db.Column(db.Float, nullable=False)
    triggered       = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class TriggerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Trigger

trigger_schema = TriggerSchema()
