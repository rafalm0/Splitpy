from marshmallow import Schema, fields

'''Schemas for the objects, in python we'll have the plain values with only their fixed values, and super objects
for versions that include more and could be related to other objects or key'''


class PlainTransactionSchema(Schema):
    id = fields.Int(dump_only=True)  # means that we generate this, so we never receive it
    description = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainMemberSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class PlainGroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class TransactionSchema(PlainTransactionSchema):
    group_id = fields.Int(required=True, load_only=True)
    # group = fields.Nested(PlainTransactionSchema(), dump_only=True)
    group = fields.Nested(PlainGroupSchema(), dump_only=True)
    payer_id = fields.Int(required=True, load_only=True)
    members = fields.List(fields.Nested(PlainMemberSchema()), dump_only=True)


class TransactionUpdateSchema(Schema):
    description = fields.Str()
    price = fields.Float()


class MemberSchema(PlainMemberSchema):
    group_id = fields.Int(load_only=True)
    group = fields.Nested(PlainGroupSchema(), dump_only=True)
    transactions = fields.List(fields.Nested(PlainTransactionSchema()), dump_only=True)
    # store = fields.Nested(PlainStoreSchema(), dump_only=True)
    # items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TransactionAndMemberSchema(Schema):
    transaction = fields.Nested(TransactionSchema)
    member = fields.Nested(MemberSchema)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class GroupSchema(PlainGroupSchema):
    user = fields.Nested(UserSchema(), dump_only=True)
    user_id = fields.Int(required=True, load_only=True)


class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)
