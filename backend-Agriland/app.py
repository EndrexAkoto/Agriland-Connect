from flask import Flask
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from pymongo import MongoClient
from routes import user_routes, admin_routes, land_routes
import os
from db import db
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder=os.path.abspath('/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'), static_folder=os.path.abspath('/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'))
app.secret_key = 'c30b7150c42e87caef910ca5aebddbcce8309d5f'
frontend_path = '/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'
app = Flask(__name__, template_folder='../frontend-Agriland', static_folder="../frontend-Agriland")
frontend_path = '/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'
app.secret_key = 'c30b7150c42e87caef910ca5aebddbcce8309d5f' 
app.config['UPLOAD_FOLDER'] = './uploads'

# Register blueprints
app.register_blueprint(user_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(land_routes)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)
@app.route('/admin/images/<path:filename>')
def serve_admin_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'admin_panel', 'images'), filename)

@app.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join(frontend_path, 'styles'), filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        username = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': username, 'password': password})
        if user:
            session['loggedin'] = True
            session['id'] = str(user['_id'])
            session['email'] = user['email']
            session['password']  = user['password']
            msg = 'Logged in successfully!'
            return render_template('dashboard.html', msg=msg)
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user = users_collection.find_one({'username': username})
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            users_collection.insert_one({'username': username, 'password': password, 'email': email})
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('signup.html', msg=msg)

if __name__ == '__main__':
    app.run(debug=True)
