from mongoengine import Document, StringField, FloatField, DictField, ListField


class User(Document):
    user_id = StringField(required=True, unique=True)
    expenses_paid = ListField(DictField())
    shares_received = DictField()

    meta = {
        'collection': 'users'
    }


class Expense(Document):
    payer_id = StringField(required=True)
    amount = FloatField(required=True)
    shares = DictField()

    meta = {
        'collection': 'expenses'
    }
