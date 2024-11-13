import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import GroupModel
from flask_jwt_extended import get_jwt, jwt_required
from db import db
from schemas import GroupSchema

blp = Blueprint("groups", __name__, description="Operations on groups")


@blp.route("/group/<int:group_id>")
class Group(MethodView):

    @jwt_required()
    @blp.response(200, GroupSchema)
    def get(self, group_id):
        group = GroupModel.query.get_or_404(group_id)
        return group

    @jwt_required()
    def delete(self, group_id):
        group = GroupModel.query.get_or_404(group_id)
        db.session.delete(group)
        db.session.commit()
        return {"message": "group deleted"}


@blp.route("/group")
class GroupList(MethodView):
    @jwt_required()
    @blp.response(200, GroupSchema(many=True))
    def get(self):
        return GroupModel.query.all()

    @jwt_required()
    @blp.arguments(GroupSchema)
    @blp.response(201, GroupSchema)
    def post(self,
             group_data):  # the method only has this other param because marshmallow is feeding it with the blp.schema
        item = GroupModel(**group_data)  # just passing the arguments to create the item

        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Group name already exists")
        except SQLAlchemyError:
            abort(500, message="Error creating item IN post /ITEM")

        return item
