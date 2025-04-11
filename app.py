from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'users.db'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'adminpass'  # Change this to something secure!

def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''CREATE TABLE users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL
                            )''')
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (ADMIN_USERNAME, ADMIN_PASSWORD))
            conn.commit()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash('Signup successful! Please login.', 'success')
                return redirect('/login')
            except sqlite3.IntegrityError:
                flash('Username already exists.', 'error')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cur.fetchone()
            if user:
                session['username'] = username
                return redirect('/dashboard')
            else:
                flash('Invalid username or password!', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    if session['username'] == ADMIN_USERNAME:
        with sqlite3.connect(DB_NAME) as conn:
            users = conn.execute("SELECT username FROM users").fetchall()
        return render_template('admin_dashboard.html', users=users, username=session['username'])
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    print("Starting app locally...")
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
