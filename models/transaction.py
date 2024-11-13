from db import db


class TransactionModel(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)

    # payer_id = db.Column(db.Integer, db.ForeignKey("member.id"), unique=False, nullable=False)
    # payer = db.relationship("MemberModel", back_populates="transaction")

    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), unique=False, nullable=False)
    groups = db.relationship("GroupModel", back_populates="transactions")

    members = db.relationship("MemberModel", back_populates="transactions", secondary="transaction_member")
