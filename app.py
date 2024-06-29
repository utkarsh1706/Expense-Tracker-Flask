from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = {}
expenses = []

class Expense:
    def __init__(self, payer_id, amount):
        self.payer_id = payer_id
        self.amount = amount
        self.shares = {}

    def add_share(self, user_id, share_amount):
        self.shares[user_id] = share_amount

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.expenses_paid = []
        self.shares_received = {}

    def add_expense(self, expense):
        self.expenses_paid.append(expense)

    def receive_share(self, payer_id, share_amount):
        if payer_id in self.shares_received:
            self.shares_received[payer_id] += share_amount
        else:
            self.shares_received[payer_id] = share_amount

    def get_amount_owed_by_friends(self):
        amount_owed = {}
        for expense in self.expenses_paid:
            for friend_id, share_amount in expense.shares.items():
                if friend_id in amount_owed:
                    amount_owed[friend_id] += share_amount
                else:
                    amount_owed[friend_id] = share_amount
        return amount_owed

    def get_amount_owed_to_friends(self):
        return self.shares_received


@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    user_id = data['user_id']
    if user_id in users:
        logger.warning(f"Attempt to add an existing user: {user_id}")
        return jsonify({'message': 'User already exists!'}), 400
    users[user_id] = User(user_id)
    logger.info(f"User added successfully: {user_id}")
    return jsonify({'message': 'User added successfully!'}), 200

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    payer_id = data['payer_id']
    amount = data['amount']
    shares = data['shares']

    if payer_id not in users:
        logger.error(f"Payer does not exist: {payer_id}")
        return jsonify({'message': 'Payer does not exist!'}), 400

    expense = Expense(payer_id, amount)
    for friend_id, share_amount in shares.items():
        if friend_id not in users:
            logger.error(f"User does not exist: {friend_id}")
            return jsonify({'message': f'User {friend_id} does not exist!'}), 400
        expense.add_share(friend_id, share_amount)
        users[friend_id].receive_share(payer_id, share_amount)

    users[payer_id].add_expense(expense)
    expenses.append(expense)
    logger.info(f"Expense added successfully by {payer_id} for amount {amount}")
    return jsonify({'message': 'Expense added successfully!'}), 200

@app.route('/amount_owed_by_friends/<user_id>', methods=['GET'])
def amount_owed_by_friends(user_id):
    if user_id not in users:
        logger.error(f"User does not exist: {user_id}")
        return jsonify({'message': 'User does not exist!'}), 400
    amount_owed = users[user_id].get_amount_owed_by_friends()
    logger.info(f"Amount owed by friends for user {user_id}: {amount_owed}")
    return jsonify(amount_owed), 200

@app.route('/amount_owed_to_friends/<user_id>', methods=['GET'])
def amount_owed_to_friends(user_id):
    if user_id not in users:
        logger.error(f"User does not exist: {user_id}")
        return jsonify({'message': 'User does not exist!'}), 400
    amount_owed_to = users[user_id].get_amount_owed_to_friends()
    logger.info(f"Amount owed to friends for user {user_id}: {amount_owed_to}")
    return jsonify(amount_owed_to), 200

if __name__ == '__main__':
    app.run(debug=True)
