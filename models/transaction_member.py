from db import db


class TransactionAndMember(db.Model):
    __tablename__ = "transaction_member"

    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), primary_key=True, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), primary_key=True, nullable=False)
    is_payer = db.Column(db.Boolean, unique=False, default=True, nullable=False)
