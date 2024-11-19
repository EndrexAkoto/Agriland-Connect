from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, Response, jsonify
from models.user import get_user_by_email, create_user, authenticate_user
from models.profile import *
from models.land import *
from werkzeug.security import check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from bson import ObjectId

# Assuming MongoDB setup
client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']
counties_collection = db['Counties'] 
land_collection = db['land_listings']

import re
import os

user_routes = Blueprint('user', __name__)
frontend_path = '/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland'

@user_routes.route("/")
def index():
    return render_template('index.html')

@user_routes.route("/signup.html", methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        # Gather form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = db.users.find_one({'email': email})
        if existing_user:
            msg = 'Account with this email already exists!'
        else:
            # Insert the new user with 'active' status
            new_user = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,  # Consider hashing the password for security
                'status': 'active'  # Set status to 'active' for new users
            }
            db.users.insert_one(new_user)
            msg = 'Signup successful! You can now log in.'
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
            # Check if the user's status is active
            if user.get('status') == 'deactivated':
                msg = 'Your account has been deactivated. Please contact admin for assistance.'
            elif user.get('status') == 'active':
                # Proceed with login if status is active
                session['loggedin'] = True
                session['id'] = str(user['_id'])
                session['email'] = user['email']
                session['name'] = user['first_name']
                msg = 'Logged in successfully!'
                return redirect(url_for('user.dashboard'))
        else:
            msg = 'Incorrect username/password!'
    
    return render_template('login.html', msg=msg)


@user_routes.route("/dashboard.html")
def dashboard():
    user_id = session.get('id')  # Assuming the user ID is stored in the session

    # Check if user ID is present in the session
    if user_id:
        # Retrieve the user's data from the database using the user ID
        user = users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"first_name": 1, "last_name": 1, "email": 1}  # Only fetch required fields
        )
        if user:
            # Extract user details
            user_data = {
                "name": f"{user.get('first_name', 'Guest')} {user.get('last_name', '')}",
                "email": user.get('email', 'Not Available')
            }
            # Render dashboard.html with the actual user data
            return render_template('dashboard.html', user_data=user_data)

    # If user ID is not in the session or no user is found, render with default values
    user_data = {"name": "Guest", "email": "Not Available"}
    return render_template('dashboard.html', user_data=user_data)



@user_routes.route("/edit-profile.html", methods=['GET', 'POST'])
def profile():
    msg = ''
    user_id = session.get('id')  # Assuming you store the user_id in the session
    if user_id:
        user = get_user_by_id(user_id)
        if not user:
            return "User not found", 404
    else:
        return "User not logged in", 401

    if request.method == 'POST':
        # Extract form data and validate it
        profile_data, next_of_kin_data, msg = extract_and_validate_form_data()
        if msg:
            return render_template('edit-profile.html', msg=msg)

        # Process profile picture and ID image
        profile_picture_id = save_profile_picture()  # Save profile picture
        id_image_id = save_id_image()  # Save ID image

        # Update profile data with image IDs
        profile_data['profile_picture_id'] = profile_picture_id
        profile_data['id_image_id'] = id_image_id

        # Update or insert profile in the database
        save_profile_data(profile_data, id_image_id)

        msg = 'Profile updated successfully!' if profiles_collection.find_one({'email': profile_data['email']}) else 'Profile created successfully!'
        return redirect(url_for('user.profile'))
    
    return render_template('edit-profile.html', user=user, msg=msg)

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
            # 'user_id': ObjectId(user_id),
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
            return render_template('farmer.html', msg='User not found!')

        # Update role logic
        current_role = user.get('role', 'N/A')
        if current_role == 'Landlord':
            new_role = 'Farmer, Landlord'
        else:
            new_role = 'Farmer'

        user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})

        return render_template('farmer.html', msg='Land request submitted successfully!')

    # Fetch county names for the dropdown
    counties = counties_collection.find({}, {'_id': 0, 'County': 1})
    county_names = [county['County'] for county in counties]
    return render_template('farmer.html', county_names=county_names, msg='')

@user_routes.route('/user-profile.html')
def userprofile():
    # Fetch user profile data from the database using the email from the session
    user_profile = db.users.find_one({"email": session.get('email')})
    
    if user_profile:
        return render_template('user-profile.html', user_profile=user_profile)
    else:
        return render_template('user-profile.html', msg="User profile not found.")
# Serve other static files
@user_routes.route('/logout.html')
def logout():
    return render_template('logout.html')

@user_routes.route('/index.html')
def homepage():
    return render_template('index.html')

@user_routes.route('/find-land.html', methods=['GET', 'POST'])
def find_land():
    # Fetch counties
    counties = counties_collection.find({}, {'_id': 0, 'County': 1})
    county_names = [county['County'] for county in counties]

    # Initialize the query with approved listings
    query = {'approved': "True"}

    # Retrieve filter parameters from the request
    location = request.args.get('location')
    land_size = request.args.get('land_size')
    price_range = request.args.get('price_range')

    # Apply location filter
    if location and location != "Select a County":
        query['location'] = location

    # Apply land size filter
    if land_size and land_size != "any":
        size_range = land_size.split('-')
        if len(size_range) == 2:
            query['land_size'] = {
                '$gte': int(size_range[0]),
                '$lte': int(size_range[1])
            }
        elif land_size == "101+":
            query['land_size'] = {'$gt': 100}

    # Apply price range filter
    if price_range:
        price_values = [int(price.strip()) for price in price_range.split('-') if price.strip().isdigit()]
        if len(price_values) == 2:
            query['price_per_acre'] = {
                '$gte': price_values[0],
                '$lte': price_values[1]
            }

    # Fetch filtered listings from the database
    approved_listings = land_collection.find(query)

    # Process listings into a format for rendering
    listings = [
        {
            '_id': str(listing['_id']),
            'land_size': get_field(listing, 'land_size', 'size', default='N/A'),
            'location': get_field(listing, 'location', default='N/A'),
            'price_per_acre': get_field(listing, 'price_per_acre', 'price', default='N/A'),
            'amenities': get_field(listing, 'amenities', default='N/A'),
            'road_access': get_field(listing, 'road_access', default='N/A'),
            'fencing': get_field(listing, 'fencing', default='N/A'),
            'title_deed': get_field(listing, 'title_deed', default='N/A'),
            'lease_duration': get_field(listing, 'lease_duration', default='N/A'),
            'payment_frequency': get_field(listing, 'payment_frequency', default='N/A'),
            'farm_images': [
                f"/admin/uploads/{str(listing['_id'])}/images/{image}"
                for image in get_field(listing, 'images', 'farm_images', default=[])
            ]
        }
        for listing in approved_listings
    ]

    # Render the template with listings and county names
    return render_template('find-land.html', listings=listings, county_names=county_names)

@user_routes.route('/full-listing.html', methods=['GET'])
def full_listing():
    listing_id = request.args.get('id')  # Get the ID from the URL
    listing = land_collection.find_one({"_id": ObjectId(listing_id)})  # Query the database using the ID

    # Handle the case where the listing is not found
    if not listing:
        return render_template('404.html')  # Or any appropriate error page

    # Process the listing data
    listing_data = {
        '_id': str(listing['_id']),
        'land_size': get_field(listing, 'land_size', 'size', default='N/A'),
        'location': get_field(listing, 'location', default='N/A'),
        'price_per_acre': get_field(listing, 'price_per_acre', 'price', default='N/A'),
        'amenities': get_field(listing, 'amenities', default='N/A'),
        'road_access': get_field(listing, 'road_access', default='N/A'),
        'fencing': get_field(listing, 'fencing', default='N/A'),
        'title_deed': get_field(listing, 'title_deed', default='N/A'),
        'lease_duration': get_field(listing, 'lease_duration', default='N/A'),
        'payment_frequency': get_field(listing, 'payment_frequency', default='N/A'),
        'farm_images': [
            f"/admin/uploads/{str(listing['_id'])}/images/{image}"
            for image in get_field(listing, 'images', 'farm_images', default=[])
        ]
    }

    # Render the full listing details page with the fetched listing data
    return render_template('full-listing.html', listing=listing_data)

@user_routes.route('/api/land-listings', methods=['GET'])
def get_land_listings():
    try:
        # Fetch approved land listings
        approved_listings = land_collection.find({'approved': "True"})  # Fetch only approved listings

        listings = [
            {
                '_id': str(listing['_id']),
                'land_size': get_field(listing, 'land_size', 'size', default='N/A'),
                'location': get_field(listing, 'location', default='N/A'),
                'price_per_acre': get_field(listing, 'price_per_acre', 'price', default='N/A'),
                'amenities': get_field(listing, 'amenities', default='N/A'),
                'road_access': get_field(listing, 'road_access', default='N/A'),
                'fencing': get_field(listing, 'fencing', default='N/A'),
                'title_deed': get_field(listing, 'title_deed', default='N/A'),
                'lease_duration': get_field(listing, 'lease_duration', default='N/A'),
                'payment_frequency': get_field(listing, 'payment_frequency', default='N/A'),
                'farm_images': [
                    f"/admin/uploads/{str(listing['_id'])}/images/{image}"
                    for image in get_field(listing, 'images', 'farm_images', default=[])
                ]
            }
            for listing in approved_listings
        ]

        # Return JSON response
        return jsonify({'success': True, 'data': listings}), 200
    except Exception as e:
        print(f"Error fetching land listings: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch listings'}), 500

@user_routes.route('/image/<image_id>')
def image(image_id):
    try:
        # Fetch the image from GridFS using its ObjectId
        image_file = fs.get(ObjectId(image_id))
        return Response(image_file.read(), mimetype=image_file.content_type)
    except Exception as e:
        return f"An error occurred: {e}", 404
# Serve other static files
@user_routes.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)

@user_routes.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join(frontend_path, 'styles'), filename)