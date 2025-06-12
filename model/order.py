from model import db
from datetime import datetime

class Order(db.Model):
    __tablename__     = 'orders'
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type              = db.Column(db.Enum('BUY','SELL', name='order_type'), nullable=False)
    base_currency     = db.Column(db.String(3), nullable=False)
    target_currency   = db.Column(db.String(3), nullable=False)
    amount            = db.Column(db.Float, nullable=False)
    price             = db.Column(db.Float, nullable=False)
    status            = db.Column(db.Enum('OPEN','CANCELLED','COMPLETED',
                                          name='order_status'), default='OPEN')
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='orders')
