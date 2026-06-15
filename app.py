from functools import wraps
from datetime import timedelta
import json
import os

from elasticsearch import Elasticsearch
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

ES_HOST = os.environ.get('ES_HOST', 'http://localhost:9200')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
USER_CONFIG = os.environ.get('SIEM_USERS', 'admin:adminpass:admin;analyst:analystpass:analyst')
USERS_FILE = os.environ.get('SIEM_USERS_FILE', 'users.json')

DEBUG_MODE = os.environ.get('DEBUG', 'False').lower() == 'true'


def load_persistent_users():
    users = {}
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            for username, info in data.items():
                if 'password_hash' in info and 'role' in info:
                    users[username] = {
                        'password_hash': info['password_hash'],
                        'role': info['role']
                    }
    except Exception:
        pass
    return users


def save_persistent_user(username, password_hash, role='analyst'):
    users = load_persistent_users()
    users[username] = {
        'password_hash': password_hash,
        'role': role
    }
    with open(USERS_FILE, 'w', encoding='utf-8') as fh:
        json.dump(users, fh, indent=2)


def load_users():
    users = parse_users(USER_CONFIG)
    users.update(load_persistent_users())

    return users


app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=SECRET_KEY,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
    SESSION_COOKIE_SAMESITE=os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax'),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
)
app.secret_key = SECRET_KEY
es = Elasticsearch([ES_HOST], request_timeout=30)


def parse_users(config):
    users = {}

    for entry in config.split(';'):
        if not entry.strip():
            continue

        parts = entry.split(':')
        if len(parts) != 3:
            continue

        username, password, role = parts
        users[username] = {
            'password_hash': generate_password_hash(password),
            'role': role,
        }

    return users


USERS = load_users()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login', next=request.path))
            if session.get('role') not in allowed_roles:
                flash('Access denied: insufficient permissions', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def inject_user():
    return {'current_user': session.get('user'), 'current_role': session.get('role')}


@app.route('/healthz')
def healthz():
    try:
        if es.ping():
            return jsonify(status='ok'), 200
    except Exception:
        pass
    return jsonify(status='unavailable'), 503


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = USERS.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user'] = username
            session['role'] = user['role']
            flash(f'Logged in as {username}', 'success')
            next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
        flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not username or not password:
            flash('Username and password are required', 'error')
        elif password != confirm:
            flash('Passwords do not match', 'error')
        elif username in USERS:
            flash('Username already exists', 'error')
        else:
            password_hash = generate_password_hash(password)
            save_persistent_user(username, password_hash)
            USERS[username] = {'password_hash': password_hash, 'role': 'analyst'}
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    try:
        res = es.search(
            index='siem-*',
            body={
                'size': 20,
                'sort': [{'@timestamp': {'order': 'desc'}}],
            },
        )
        hits = res.get('hits', {}).get('hits', [])
        events = [h.get('_source', {}) for h in hits]
    except Exception:
        events = []

    return render_template('index.html', events=events)


@app.route('/search')
@login_required
def search():
    q = request.args.get('q')
    body = {
        'query': {'query_string': {'query': q}}
    } if q else {'query': {'match_all': {}}}
    res = es.search(index='siem-*', body=body, size=50)
    return jsonify(res)


@app.route('/alerts')
@login_required
def alerts():
    body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"severity": "HIGH"}}
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}]
    }
    try:
        res = es.search(index='siem-*', body=body, size=50)
        hits = res.get('hits', {}).get('hits', [])
        alerts = [h.get('_source', {}) for h in hits]
    except Exception:
        alerts = []
    return render_template('alerts.html', alerts=alerts)


@app.route('/manage')
@role_required('admin')
def manage():
    return render_template('manage.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
