from db import db


class MemberModel(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)

    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)

    group = db.relationship("GroupModel", back_populates="members")
    # transaction = db.relationship("TransactionModel", back_populates="member", secondary="items_tags")
    transactions = db.relationship("TransactionModel", back_populates="members", secondary="transaction_member")