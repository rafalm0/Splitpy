from db import db


class GroupModel(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel", back_populates="groups")

    members = db.relationship("MemberModel", back_populates="group", lazy="dynamic")
    transactions = db.relationship("TransactionModel", back_populates="group", lazy="dynamic")
