from model import db

class WalletBalance(db.Model):
    __tablename__ = 'wallet_balances'
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    balance  = db.Column(db.Float, nullable=False, default=0.0)

    user = db.relationship('User', backref='wallets')