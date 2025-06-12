from model import db
from datetime import datetime

class Escrow(db.Model):
    __tablename__ = 'escrows'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    buyer_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount     = db.Column(db.Float, nullable=False)
    target_currency = db.Column(db.String(3), nullable=False)
    price      = db.Column(db.Float, nullable=False)
    status     = db.Column(db.Enum('PENDING','RELEASED','CANCELLED',
                                   name='escrow_status'), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    order  = db.relationship('Order', backref='escrow')
    buyer  = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])
