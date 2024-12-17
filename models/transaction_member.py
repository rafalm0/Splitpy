from db import db


class TransactionMember(db.Model):
    __tablename__ = "transaction_member"

    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), primary_key=True, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), primary_key=True, nullable=False)
    is_payer = db.Column(db.Boolean, unique=False, default=True, nullable=False)
    amount_paid = db.Column(db.Float(precision=2), unique=False, nullable=True)

