from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory
from models.user import get_user_by_email, create_user, authenticate_user
from models.profile import *
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['Agriconnect']

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
    # Assuming 'name' is stored in session upon login
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
        # Get form data
        land_size = request.form.get('landSize')
        location = request.form.get('location')
        crop_type = request.form.get('cropType')
        budget_per_acre = request.form.get('budgetPerAcre')
        lease_duration = request.form.get('leaseDuration')
        payment_method = request.form.get('paymentMethod')

        # Validate form data
        if not land_size or not location or not crop_type or not budget_per_acre or not lease_duration or not payment_method:
            return render_template('farmer.html', msg='Please fill out all fields!')
        
        # Create land request data dictionary
        land_request_data = {
            'land_size': land_size,
            'location': location,
            'crop_type': crop_type,
            'budget_per_acre': budget_per_acre,
            'lease_duration': lease_duration,
            'payment_method': payment_method
        }

        # Insert the land request into MongoDB
        try:
            db['farmer'].insert_one(land_request_data)
            msg = 'Land request submitted successfully!'
        except Exception as e:
            msg = f"An error occurred while submitting your request: {str(e)}"

        # Render the form again with a success/failure message
        return render_template('farmer.html', msg=msg)

    # Render the form if method is GET
    return render_template('farmer.html', msg='')

# Serve other static files
@user_routes.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)

@user_routes.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join(frontend_path, 'styles'), filename)
