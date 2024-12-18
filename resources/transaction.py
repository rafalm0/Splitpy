from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TransactionModel, GroupModel, MemberModel, TransactionMember
from schemas import TransactionSchema, TransactionUpdateSchema, TransactionMemberSchema, EnrichedTransactionSchema
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

        if str(group.user_id) != str(current_user_id):
            abort(403, message="You are not authorized to view this transaction.")

        return transaction

    @jwt_required()
    def delete(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        group = GroupModel.query.get_or_404(transaction.group_id)
        current_user_id = get_jwt_identity()

        if str(group.user_id) != str(current_user_id):
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

        if str(group.user_id) != str(current_user_id):
            abort(403, message="You are not authorized to update this transaction.")

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
                    paid=member_data["amount_paid"],
                    consumed=member_data["amount_consumed"]
                )
                db.session.add(transaction_member_link)

        db.session.add(transaction)
        db.session.commit()

        return transaction


@blp.route("/transaction")
class TransactionList(MethodView):
    @jwt_required()
    @blp.response(200, EnrichedTransactionSchema(many=True))
    def get(self):
        current_user_id = get_jwt_identity()
        transactions = (
            db.session.query(TransactionModel)
            .join(GroupModel, GroupModel.id == TransactionModel.group_id)
            .join(TransactionMember, TransactionMember.transaction_id == TransactionModel.id)
            .join(MemberModel, MemberModel.id == TransactionMember.member_id)
            .filter(GroupModel.user_id == current_user_id)
            .add_columns(MemberModel.name, GroupModel.id, TransactionMember.paid, TransactionMember.consumed)
            .all()
        )

        # Build the response structure
        enriched_transactions = {}
        for t in transactions:
            transaction = t[0]
            member_name = t[1]
            group_id = t[2]
            paid = t[3]
            consumed = t[4]
            if transaction.id not in enriched_transactions:
                enriched_transactions[transaction.id] = {
                    "id": transaction.id,
                    "group_id": group_id,
                    "description": transaction.description,
                    "members": []
                }
            enriched_transactions[transaction.id]["members"].append({
                "name": member_name,
                "paid": paid,
                "consumed":consumed
            })

        return list(enriched_transactions.values())

    @jwt_required()
    @blp.arguments(TransactionSchema)
    @blp.response(201, TransactionSchema)
    def post(self, transaction_data):
        current_user_id = get_jwt_identity()
        group = GroupModel.query.get_or_404(transaction_data["group_id"])

        if str(group.user_id) != str(current_user_id):
            abort(403, message="You are not authorized to add a transaction to this group.")

        transaction = TransactionModel(
            description=transaction_data['description'],
            group_id=transaction_data['group_id']
        )
        try:

            members_list = []
            raw_members = transaction_data.get('members_raw')  # only one of these are accepted by marshmallow
            nested_members = transaction_data.get('members')

            if raw_members:
                for member_data in raw_members:
                    members_list.append({
                        "member_id": member_data.get("member_id"),
                        "amount_paid": member_data.get("amount_paid", 0),
                        "amount_consumed": member_data.get("amount_consumed", 0)
                    })

            elif nested_members:
                for member_obj in nested_members:
                    members_list.append({
                        "member_id": member_obj.member_id,
                        "amount_consumed": member_obj.amount_consumed,
                        "amount_paid": member_obj.amount_paid
                    })


            total_paid = sum(x['amount_paid'] for x in members_list)
            total_consumed = sum(x['amount_consumed'] for x in members_list)
            if total_paid != total_consumed:
                abort(400, message=f"Amount paid: {total_paid} does not match total bill: {total_consumed}.")
            db.session.add(transaction)
            db.session.flush()  # Ensure transaction ID is available

            # Process each member in the unified list
            for member_data in members_list:
                member = MemberModel.query.get_or_404(member_data["member_id"])
                if member.group_id != group.id:
                    abort(400, message="Member does not belong to the group.")

                transaction_member_link = TransactionMember(
                    transaction_id=transaction.id,
                    member_id=member.id,
                    paid=member_data["amount_paid"],
                    consumed=member_data["amount_consumed"]
                )
                db.session.add(transaction_member_link)

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while inserting the transaction.")

        return transaction
