from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, Response, jsonify, send_file
from models.user import get_user_by_email, create_user, authenticate_user
from models.profile import *
from models.land import *
from werkzeug.security import check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from bson import ObjectId
from io import BytesIO
from gridfs import GridFS

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

    if user_id:
        # Retrieve the user's data from the database using the user ID
        user = users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"first_name": 1, "last_name": 1, "email": 1, "profile_picture_id": 1}  # Fetch profile_picture_id
        )
        if user:
            user_data = {
                "name": f"{user.get('first_name', 'Guest')} {user.get('last_name', '')}",
                "email": user.get('email', 'Not Available'),
                "profile_picture_id": user.get('profile_picture_id')  # Include profile picture ID
            }

            # Fetch all land listings belonging to the user
            land_listings = list(land_collection.find({"name": user.get("first_name")}))

            # Filter approved listings
            approved_listings = [listing for listing in land_listings if listing.get("approved") == "True"]
            active_count = len(approved_listings)  # Count the approved listings

            # Render the dashboard template with user data and land counts
            return render_template(
                'dashboard.html',
                user_data=user_data,
                active_count=active_count,  # Pass the active (approved) count
                total_count=len(land_listings),  # Total number of listings
                land_listings=land_listings  # Pass all listings
            )

    # Default response when no user is found or not logged in
    user_data = {"name": "Guest", "email": "Not Available", "profile_picture_id": None}
    return render_template('dashboard.html', user_data=user_data, active_count=0, total_count=0)

@user_routes.route("/notifications.html")
def notifications():
    # Step 1: Get the session user ID
    user_id = session.get('id')
    notifications = []  # Initialize an empty list for notifications
    print(user_id)

    if user_id:
        # Step 2: Fetch user details from users_collection using the session ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})

        if user:
            first_name = user.get('first_name')  # Get the user's first name
            role = user.get('role', 'N/A')  # Role can be farmer, landowner, or N/A

            # Fetch all land listings where name matches the user's first_name
            land_listings = list(land_collection.find({"name": first_name}))

            if role == "farmer":
                # Farmer-specific notifications
                notifications.append({
                    "id": "1",
                    "title": "Accepted and Reviewing Request",
                    "message": "Thank you for submitting your land requirements! Your submission has been received and is currently being reviewed by our team.",
                    "isUrgent": False,
                    "isRead": False
                })

            if role == "landowner":
                # Landowner-specific notifications
                for listing in land_listings:
                    status = listing.get("approved", "Pending")
                    if status == "False":
                        notifications.append({
                            "id": str(listing["_id"]),
                            "title": "Accepted and Pending Verification",
                            "message": "Thank you for listing your land! Your submission has been received and is awaiting verification by our team.",
                            "isUrgent": True,
                            "isRead": False
                        })
                    elif status == "True":
                        notifications.append({
                            "id": str(listing["_id"]),
                            "title": "Approved",
                            "message": "Congratulations! Your land listing has been approved and is now live for farmers to view and lease.",
                            "isUrgent": False,
                            "isRead": False
                        })
                    elif status == "Rejected":
                        notifications.append({
                            "id": str(listing["_id"]),
                            "title": "Rejected",
                            "message": "We’re sorry, but your land listing was not approved. Please review our guidelines and re-upload your details or contact support for help.",
                            "isUrgent": True,
                            "isRead": False
                        })
        else:
            # If user is not found in the database
            notifications.append({
                "id": "0",
                "title": "No Notifications",
                "message": "No new notifications at this time.",
                "isUrgent": False,
                "isRead": False
            })
    else:
        # Default: No notifications if user is not logged in
        notifications.append({
            "id": "0",
            "title": "No Notifications",
            "message": "You must log in to view notifications.",
            "isUrgent": False,
            "isRead": False
        })

    # Render the notifications page with serialized notifications
    return render_template("notifications.html", notifications=notifications)

# @user_routes.route('/notifications/update', methods=['POST'])
# def update_notification():
#     # Step 1: Get the session user ID
#     user_id = session.get('id')
#     if not user_id:
#         return jsonify({"error": "Unauthorized access"}), 401

#     # Step 2: Get notification ID and update parameters from the request
#     data = request.get_json()
#     notification_id = data.get('id')
#     update_fields = data.get('update_fields', {})

#     if not notification_id:
#         return jsonify({"error": "Notification ID is required"}), 400

#     # Step 3: Check if the notification belongs to the logged-in user
#     # Here, notifications are derived dynamically, so we update related data such as land listings
#     land_listing = land_collection.find_one({"_id": ObjectId(notification_id)})

#     if not land_listing:
#         return jsonify({"error": "Notification not found"}), 404

#     # Step 4: Update the listing (e.g., `isRead` or `isUrgent`)
#     land_collection.update_one(
#         {"_id": ObjectId(notification_id)},
#         {"$set": update_fields}
#     )

#     return jsonify({"success": True, "message": "Notification updated successfully"})

@user_routes.route('/edit_listing/<string:listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    # Logic for editing the listing
    pass



@user_routes.route("/edit-profile.html", methods=['GET', 'POST'])
def profile():
    msg = ''
    user_id = session.get('id')  # Retrieve logged-in user ID
    if not user_id:
        return "User not logged in", 401

    user = get_user_by_id(user_id)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        # Extract form data
        profile_data, next_of_kin_data, msg = extract_and_validate_form_data()
        if msg:
            return render_template('edit-profile.html', msg=msg, user=user)

        # Process uploaded images
        profile_picture_id = save_profile_picture()
        id_image_id = save_id_image()

        # Save profile data
        save_profile_data(profile_data, next_of_kin_data, profile_picture_id, id_image_id)

        msg = 'Profile updated successfully!'
        return render_template('edit-profile.html', user=profile_data, msg=msg)

    return render_template('edit-profile.html', user=user, msg=msg)

@user_routes.route("/farmer.html", methods=['GET', 'POST'])
def farmer():
    msg = ''
    if request.method == 'POST':
        # Retrieve user ID from the session
        user_id = session.get('id')  # Get user ID from session

        if not user_id:
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

        # Insert land request into the 'farmer' collection with the user_id
        db['farmer'].insert_one({
            'user_id': ObjectId(user_id),  # Store user_id as ObjectId for reference
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

        # Update role logic based on current role
        current_role = user.get('role', 'N/A')
        if current_role == 'Landlord':
            new_role = 'Farmer, Landlord'
        else:
            new_role = 'Farmer'

        # Update user role in the database
        user_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})

        return render_template('farmer.html', msg='Land request submitted successfully!')

    # Handle the GET request to render the form
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
        'description': get_field(listing, 'description', default='N/A'),
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

@user_routes.route('/user-image/<image_id>')
def user_image(image_id):
    # Connect to GridFS
    fs = GridFS(db)  # Assuming db is your MongoDB database
    file = fs.get(ObjectId(image_id))
    return send_file(BytesIO(file.read()), mimetype='image/jpeg') 

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