from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory
from models.user import get_user_by_email, create_user, authenticate_user

import re
import os

user_routes = Blueprint('user', __name__)
frontend_path = '/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'

@user_routes.route("/")
def index():
    return render_template('index.html')

@user_routes.route("/signup.html", methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Input validation
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif get_user_by_email(email):
            msg = 'Account already exists!'
        else:
            create_user({'username': username, 'email': email, 'password': password})
            msg = 'You have successfully registered!'
            return redirect(url_for('user.login'))
    
    return render_template('signup.html', msg=msg)

@user_routes.route("/login.html", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = authenticate_user(email, password)

        if user:
            session['loggedin'] = True
            session['id'] = str(user['_id'])
            session['email'] = user['email']
            msg = 'Logged in successfully!'
            return redirect(url_for('user.dashboard'))
        else:
            msg = 'Incorrect username/password!'
    
    return render_template('login.html', msg=msg)

@user_routes.route("/dashboard.html")
def dashboard():
    return render_template('dashboard.html')



# Serve other static files
@user_routes.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)

@user_routes.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join(frontend_path, 'styles'), filename)
