from db import db


class GroupUser(db.Model):
    __tablename__ = "group_invite"

    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False)
    is_owner = db.Column(db.Boolean, unique=False, default=True, nullable=False)
