from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory
from models.user import get_user_by_email, create_user, authenticate_user
from werkzeug.security import check_password_hash
from pymongo import MongoClient
from bson import ObjectId

# Assuming MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['Agriland-Connect']
users_collection = db['users']

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
            session['name'] = user['username'] 
            msg = 'Logged in successfully!'
            return redirect(url_for('user.dashboard'))
        else:
            msg = 'Incorrect username/password!'
    
    return render_template('login.html', msg=msg)


@user_routes.route("/dashboard.html")
def dashboard():
    user_data = {
        "name": session.get("name", "Guest")  # Default to "Guest" if name is not in session
    }
    return render_template('dashboard.html', user_data=user_data)

@user_routes.route("/edit-profile.html", methods=['GET', 'POST'])
def profile():
    msg = ''
    if request.method == 'POST':
        # Extract form data and validate it
        profile_data, next_of_kin_data, msg = extract_and_validate_form_data()
        if msg:
            return render_template('edit-profile.html', msg=msg)

        # Process images
        profile_image_id, next_of_kin_image_id = save_images()

        # Update or insert profile in the database
        save_profile_data(profile_data, next_of_kin_data, profile_image_id, next_of_kin_image_id)

        msg = 'Profile updated successfully!' if profiles_collection.find_one({'email': profile_data['email']}) else 'Profile created successfully!'
    
    return render_template('edit-profile.html', msg=msg)

@user_routes.route("/farmer.html", methods=['GET', 'POST'])
def farmer():
    if request.method == 'POST':
        user_id = session.get('id')  # Get user ID from session
        username = session.get('name')  # Get username from session

        if not user_id or not username:
            return redirect(url_for('user.login'))  # Redirect if not logged in

        # Collect form data
        land_size = request.form.get('landSize')
        location = request.form.get('location')
        crop_type = request.form.get('cropType')
        budget_per_acre = request.form.get('budgetPerAcre')
        lease_duration = request.form.get('leaseDuration')
        payment_method = request.form.get('paymentMethod')

        if not all([land_size, location, crop_type, budget_per_acre, lease_duration, payment_method]):
            return render_template('farmer.html', msg='Please fill out all fields!')

        # Insert land request into the 'farmer' collection with the user_id and username
        db['farmer'].insert_one({
            'user_id': ObjectId(user_id),
            'username': username,
            'land_size': land_size,
            'location': location,
            'crop_type': crop_type,
            'budget_per_acre': budget_per_acre,
            'lease_duration': lease_duration,
            'payment_method': payment_method
        })

        # Update the user's role
        user_collection = db['users']
        user = user_collection.find_one({'_id': ObjectId(user_id)})

        if user is None:
            return render_template('farmer.html', msg='User not found!')  # Handle user not found

        # Update role logic
        current_role = user.get('role', 'N/A')
        if current_role == 'Landlord':
            new_role = 'Farmer, Landlord'
        else:
            new_role = 'Farmer'

        user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})

        return render_template('farmer.html', msg='Land request submitted successfully!')

    return render_template('farmer.html', msg='')


@user_routes.route('/find-land.html')
def findland():
    return render_template('find-land.html')
# Serve other static files
@user_routes.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)

@user_routes.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join(frontend_path, 'styles'), filename)
