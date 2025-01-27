from db import db
from datetime import datetime


class TransactionModel(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=False, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=True)
    group = db.relationship("GroupModel", back_populates="transactions")

    members = db.relationship("MemberModel", back_populates="transactions", secondary="transaction_member")
