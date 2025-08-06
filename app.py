from flask import Flask, render_template, request, jsonify
import json
import datetime
import os

app = Flask(__name__)
DB_FILE = 'db.json'

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/register.html')
def register_page():
    return render_template('register.html')

@app.route('/payment.html')
def payment_page():
    return render_template('payment.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db = load_db()

    username = data['username']
    password = data['password']

    if username in db:
        return jsonify({'success': False, 'message': 'Username already exists.'})

    db[username] = {
        'password': password,
        'is_premium': False,
        'premium_expiry': None
    }
    save_db(db)
    return jsonify({'success': True, 'message': 'Registration successful.'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = load_db()

    username = data['username']
    password = data['password']

    if username not in db or db[username]['password'] != password:
        return jsonify({'success': False, 'message': 'Invalid credentials.'})

    is_premium = db[username].get('is_premium', False)
    expiry = db[username].get('premium_expiry')
    if expiry:
        expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d")
        if expiry_date < datetime.datetime.today():
            is_premium = False
            db[username]['is_premium'] = False
            db[username]['premium_expiry'] = None
            save_db(db)

    return jsonify({'success': True, 'message': 'Login successful.', 'is_premium': is_premium})

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    username = request.form.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'No username provided'})

    db = load_db()
    if username in db:
        db[username]['is_premium'] = True
        expiry = (datetime.datetime.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        db[username]['premium_expiry'] = expiry
        save_db(db)
        return jsonify({'success': True, 'message': 'Premium activated for 30 days.'})
    else:
        return jsonify({'success': False, 'message': 'User not found.'})

if __name__ == '__main__':
    app.run(debug=True)
