from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TransactionModel
from schemas import TransactionSchema, TransactionUpdateSchema
from flask_jwt_extended import get_jwt, jwt_required

blp = Blueprint("Transactions", __name__, description="Operations on transactions")


@blp.route("/transaction/<int:transaction_id>")
class Transaction(MethodView):
    @blp.response(200, TransactionSchema)
    def get(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        return transaction

    def delete(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        return {"message": "Transaction deleted."}

    @blp.arguments(TransactionUpdateSchema)
    @blp.response(200, TransactionSchema)
    def put(self, transaction_data, transaction_id):
        transaction = TransactionModel.query.get(transaction_id)

        if transaction:
            transaction.price = transaction_data["price"]
            transaction.description = transaction_data["description"]
        else:
            transaction = TransactionModel(id=transaction_id, **transaction_data)

        db.session.add(transaction)
        db.session.commit()

        return transaction


@blp.route("/transaction")
class TransactionList(MethodView):
    # @jwt_required()
    @blp.response(200, TransactionSchema(many=True))
    def get(self):
        return TransactionModel.query.all()

    @blp.arguments(TransactionSchema)
    @blp.response(201, TransactionSchema)
    def post(self, transaction_data):
        transaction = TransactionModel(**transaction_data)

        try:
            db.session.add(transaction)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the transaction.")

        return transaction
