from flask_smorest import Blueprint, abort
from schemas import MemberSchema, TransactionMemberSchema
from flask.views import MethodView
from models import MemberModel, GroupModel, TransactionMember, TransactionModel
from flask_jwt_extended import get_jwt, jwt_required
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Members", __name__, description="Operations on members")


@blp.route("/group/<int:group_id>/member")
class MemberInGroup(MethodView):
    @blp.response(200, MemberSchema(many=True))
    def get(self, group_id):
        group = GroupModel.query.get_or_404(group_id)
        return group.members.all()

    @blp.arguments(MemberSchema)
    @blp.response(201, MemberSchema)
    def post(self, tag_data, group_id):
        member = MemberModel(group_id=group_id, **tag_data)
        try:
            db.session.add(member)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e) + str(tag_data) + str(group_id))

        return member


@blp.route("/transaction/<int:transaction_id>/member/<int:member_id>")
class LinkMembersToTransaction(MethodView):

    # @blp.arguments()
    @blp.response(201, MemberSchema)
    def get(self, transaction_id, member_id):
        transaction = TransactionModel.get_or_404(transaction_id)
        member = MemberModel.get_or_404(member_id)

        transaction.members.append(member)
        try:
            db.session.add(transaction)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"error linking member and transaction message={e}")
        return member

    @blp.response(200, MemberSchema)
    def delete(self, transaction_id, member_id):
        transaction = TransactionModel.get_or_404(transaction_id)
        member = MemberModel.get_or_404(member_id)

        transaction.members.remove(member)
        try:
            db.session.add(transaction)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"error removing member and transaction message={e}")
        return {'message': "transaction removed from member ", "transaction": transaction, "member": member}


@blp.route("/member/<int:member_id>")
class Group(MethodView):

    @blp.response(200, MemberSchema)
    def get(self, member_id):
        member = MemberModel.query.get_or_404(member_id)
        return member

    @blp.response(202, description="deletes a member if no transaction is tagged with it.")
    @blp.alt_response(404, description="member not found")
    @blp.alt_response(400, description="Returns if the member is assigned to one or more transactions, the member is not deleted")
    def delete(self, member_id):
        member = GroupModel.query.get_or_404(member_id)
        if not member.transactions:
            db.session.delete(member)
            db.session.commit()
            return {"message": "member deleted"}
        abort(400, message="Could not delete member. make sure member is not associated with any transactions")
