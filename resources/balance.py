from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from main_logic import calculate_balance

from db import db
from models import TransactionModel, GroupModel, MemberModel, TransactionMember
from schemas import TransactionSchema, TransactionUpdateSchema, TransactionMemberSchema, EnrichedTransactionSchema
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity

blp = Blueprint("Balances", __name__, description="Operations on total balance")


@blp.route("/balance/<int:group_id>")
class GroupBalance(MethodView):
    @jwt_required()
    def get(self, group_id):
        group = GroupModel.query.get_or_404(group_id)
        current_user_id = get_jwt_identity()

        if str(group.user_id) != str(current_user_id):
            abort(403, message="You are not authorized to view this balance.")

        transactions = (
            db.session.query(TransactionModel)
            .join(GroupModel, GroupModel.id == TransactionModel.group_id)
            .join(TransactionMember, TransactionMember.transaction_id == TransactionModel.id)
            .join(MemberModel, MemberModel.id == TransactionMember.member_id)
            .filter(GroupModel.user_id == current_user_id)
            .add_columns(MemberModel.name, TransactionMember.is_payer, GroupModel.id)
            .all()
        )

        settle_transactions = calculate_balance(transactions)

        return settle_transactions

