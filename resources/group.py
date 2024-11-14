import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import GroupModel
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from db import db
from schemas import GroupSchema

blp = Blueprint("groups", __name__, description="Operations on groups")


@blp.route("/group/<int:group_id>")
class Group(MethodView):

    @jwt_required()
    @blp.response(200, GroupSchema)
    def get(self, group_id):
        group = GroupModel.query.get_or_404(group_id)
        current_user_id = get_jwt_identity()
        if group.user_id != current_user_id:
            abort(403, message="You are not authorized to view this group.")

        return group

    @jwt_required()
    def delete(self, group_id):
        group = GroupModel.query.get_or_404(group_id)

        current_user_id = get_jwt_identity()
        if group.user_id != current_user_id:
            abort(403, message="You are not authorized to delete this group.")
        db.session.delete(group)
        db.session.commit()
        return {"message": "group deleted"}


@blp.route("/group")
class GroupList(MethodView):
    @jwt_required()
    @blp.response(200, GroupSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()

        # Filter groups by the user_id to get only the groups belonging to the logged-in user
        groups = GroupModel.query.filter_by(user_id=user_id).all()
        return groups


    @jwt_required()
    @blp.arguments(GroupSchema)
    @blp.response(201, GroupSchema)
    def post(self,
             group_data):  # the method only has this other param because marshmallow is feeding it with the blp.schema

        group_data['user_id'] = get_jwt_identity()  # Automatically link to the logged-in user

        item = GroupModel(**group_data)  # just passing the arguments to create the item

        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Group name already exists")
        except SQLAlchemyError:
            abort(500, message="Error creating item IN post /ITEM")

        return item
