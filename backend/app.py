from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
DATA_FILE = 'db.json'

# Load data
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Save data
def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    users = load_users()

    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists.'}), 400

    users[username] = {
        'email': email,
        'password': password,
        'is_premium': False
    }

    save_users(users)
    return jsonify({'success': True, 'message': 'Registration successful.'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    users = load_users()

    user = users.get(username)
    if not user or user['password'] != password:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    return jsonify({'success': True, 'message': 'Login successful', 'is_premium': user['is_premium']})

@app.route('/upgrade', methods=['POST'])
def upgrade():
    data = request.get_json()
    username = data.get('username')

    users = load_users()
    user = users.get(username)

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # Set premium = True and expiry = 30 days from now
    user['premium'] = True
    user['premium_expiry'] = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    save_users(users)
    return jsonify({'success': True})

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    username = request.form['username']
    users = load_users()

    if username in users:
        users[username]['premium'] = True
        users[username]['premium_expiry'] = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        save_users(users)
        return redirect('/main.html')
    return "User not found", 404

def check_premium_expiry(user):
    if user.get("premium") and "premium_expiry" in user:
        expiry = datetime.strptime(user["premium_expiry"], "%Y-%m-%d")
        if datetime.now() > expiry:
            user["premium"] = False
            user["premium_expiry"] = None

if __name__ == '__main__':
    app.run(debug=True)
