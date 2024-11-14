from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TransactionModel
from schemas import TransactionSchema, TransactionUpdateSchema
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity

blp = Blueprint("Transactions", __name__, description="Operations on transactions")


@blp.route("/transaction/<int:transaction_id>")
class Transaction(MethodView):
    @jwt_required()
    @blp.response(200, TransactionSchema)
    def get(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        current_user_id = get_jwt_identity()

        if transaction.group.user_id != current_user_id:
            abort(403, message="You are not authorized to view or modify this transaction.")

        return transaction

    @jwt_required()
    def delete(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        current_user_id = get_jwt_identity()

        if transaction.group.user_id != current_user_id:
            abort(403, message="You are not authorized to delete this transaction.")

        db.session.delete(transaction)
        db.session.commit()
        return {"message": "Transaction deleted."}

    @jwt_required()
    @blp.arguments(TransactionUpdateSchema)
    @blp.response(200, TransactionSchema)
    def put(self, transaction_data, transaction_id):
        transaction = TransactionModel.query.get(transaction_id)
        current_user_id = get_jwt_identity()

        if transaction:
            if transaction.group.user_id != current_user_id:
                abort(403, message="You are not authorized to update this transaction.")
            transaction.price = transaction_data["price"]
            transaction.description = transaction_data["description"]
        else:
            abort(404, message="Transaction not found.")

        db.session.add(transaction)
        db.session.commit()

        return transaction


@blp.route("/transaction")
class TransactionList(MethodView):
    @jwt_required()
    @blp.response(200, TransactionSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()
        return TransactionModel.query.filter_by(user_id=user_id).all()

    @jwt_required()
    @blp.arguments(TransactionSchema)
    @blp.response(201, TransactionSchema)
    def post(self, transaction_data):
        user_id = get_jwt_identity()
        transaction_data["user_id"] = user_id

        transaction = TransactionModel(**transaction_data)

        try:
            db.session.add(transaction)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the transaction.")

        return transaction
