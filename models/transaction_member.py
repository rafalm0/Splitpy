from db import db


class TransactionMember(db.Model):
    __tablename__ = "transaction_member"

    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id', ondelete='CASCADE'), primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete='CASCADE'), primary_key=True)
    is_payer = db.Column(db.Boolean, nullable=False)

    # Define the relationships (optional, for ease of access)
    transaction = db.relationship('TransactionModel', backref=db.backref('members', lazy='dynamic'))
    member = db.relationship('MemberModel', backref=db.backref('transactions', lazy='dynamic'))
