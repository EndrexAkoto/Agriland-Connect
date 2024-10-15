from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
import re
import os

app = Flask(__name__, template_folder=os.path.abspath('/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'), static_folder=os.path.abspath('/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland/images'))
app.secret_key = 'c30b7150c42e87caef910ca5aebddbcce8309d5f'

client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/images/landleasing01.jpg")
def promote():
    return render_template("/images/landleasing01.jpg")
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
