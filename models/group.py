from db import db


class GroupModel(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    members = db.relationship("MemberModel", back_populates="groups", lazy="dynamic")
    transactions = db.relationship("TransactionModel", back_populates="groups", lazy="dynamic")

    # https://docs.sqlalchemy.org/en/20/orm/cascades.html

    '''lazy avoids contant refreshing data instead of only when needed, and cascade deletes the child when parant
    is deleted, therefore here items are deleted if their store is deleted'''
