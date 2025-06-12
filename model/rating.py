from model import db
from datetime import datetime

class Rating(db.Model):
    __tablename__ = 'ratings'
    id         = db.Column(db.Integer, primary_key=True)
    rater_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ratee_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score      = db.Column(db.Integer, nullable=False)   # 1–5
    comment    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rater = db.relationship('User', foreign_keys=[rater_id])
    ratee = db.relationship('User', foreign_keys=[ratee_id])
