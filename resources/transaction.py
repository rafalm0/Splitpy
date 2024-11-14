from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TransactionModel, GroupModel, MemberModel, TransactionMember
from schemas import TransactionSchema, TransactionUpdateSchema, TransactionMemberSchema
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity

blp = Blueprint("Transactions", __name__, description="Operations on transactions")


@blp.route("/transaction/<int:transaction_id>")
class Transaction(MethodView):
    @jwt_required()
    @blp.response(200, TransactionSchema)
    def get(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        group = GroupModel.query.get_or_404(transaction.group_id)
        current_user_id = get_jwt_identity()

        if group.user_id != current_user_id:
            abort(403, message="You are not authorized to view this transaction.")

        return transaction

    @jwt_required()
    def delete(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        group = GroupModel.query.get_or_404(transaction.group_id)
        current_user_id = get_jwt_identity()

        if group.user_id != current_user_id:
            abort(403, message="You are not authorized to delete this transaction.")

        db.session.delete(transaction)
        db.session.commit()
        return {"message": "Transaction deleted."}

    @jwt_required()
    @blp.arguments(TransactionUpdateSchema)
    @blp.response(200, TransactionSchema)
    def put(self, transaction_data, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        group = GroupModel.query.get_or_404(transaction.group_id)
        current_user_id = get_jwt_identity()

        if group.user_id != current_user_id:
            abort(403, message="You are not authorized to update this transaction.")

        transaction.price = transaction_data["price"]
        transaction.description = transaction_data["description"]

        # Handle member linking
        if "members" in transaction_data:
            transaction.members.clear()
            for member_data in transaction_data["members"]:
                member = MemberModel.query.get_or_404(member_data["member_id"])
                if member.group_id != group.id:
                    abort(400, message="Member does not belong to the group.")

                transaction_member_link = TransactionMember(
                    transaction_id=transaction.id,
                    member_id=member.id,
                    is_payer=member_data.get("is_payer", False)
                )
                db.session.add(transaction_member_link)

        db.session.add(transaction)
        db.session.commit()

        return transaction


@blp.route("/transaction")
class TransactionList(MethodView):
    @jwt_required()
    @blp.response(200, TransactionSchema(many=True))
    def get(self):
        current_user_id = get_jwt_identity()
        # Fetch transactions only belonging to groups owned by the logged-in user
        transactions = (
            db.session.query(TransactionModel)
            .join(GroupModel)
            .filter(GroupModel.user_id == current_user_id)
            .all()
        )
        return transactions

    @jwt_required()
    @blp.arguments(TransactionSchema)
    @blp.response(201, TransactionSchema)
    def post(self, transaction_data):
        current_user_id = get_jwt_identity()
        group = GroupModel.query.get_or_404(transaction_data["group_id"])

        if group.user_id != current_user_id:
            abort(403, message="You are not authorized to add a transaction to this group.")

        transaction = TransactionModel(**transaction_data)
        try:
            db.session.add(transaction)
            db.session.flush()  # Ensures the transaction has an ID before adding members

            # Handle member linking
            if "members" in transaction_data:
                for member_data in transaction_data["members"]:
                    member = MemberModel.query.get_or_404(member_data["member_id"])
                    if member.group_id != group.id:
                        abort(400, message="Member does not belong to the group.")

                    transaction_member_link = TransactionMember(
                        transaction_id=transaction.id,
                        member_id=member.id,
                        is_payer=member_data.get("is_payer", False)
                    )
                    db.session.add(transaction_member_link)

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while inserting the transaction.")

        return transaction
