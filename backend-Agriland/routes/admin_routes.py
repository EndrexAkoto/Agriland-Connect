from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, request
from flask import current_app as app
from models.user import get_user_by_email, create_user
from models.stats import  get_user_statistics
from models.land import add_land_listing, get_all_land_listings, add_listing_with_images, get_unapproved_land_listings
from models.settings import process_user_data
from pymongo import MongoClient 
from db import db 
from werkzeug.utils import secure_filename
import re
import os

admin_routes = Blueprint('admin', __name__)
frontend_path = '/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland/admin_panel'
UPLOAD_FOLDER = '/home/hp/Agrilandproj/Agriland-Connect/'
client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']
land_listing_collection = db['land_listings']

# Serve the 'index.html' file from the admin panel directory
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@admin_routes.route("/admin/index.html")
def admin_html():
     stats = get_user_statistics()
     return render_template('admin_panel/index.html', stats=stats)

@admin_routes.route("/admin/add-land-lease.html", methods=['GET', 'POST'])
def add_land_lease():
    if request.method == 'POST':
        # Get form data
        location = request.form.get('location')
        size = request.form.get('size')
        price = request.form.get('price')
        description = request.form.get('description')

        # Handle images
        images = request.files.getlist('images')
        image_paths = []

        if images:
            for image in images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(UPLOAD_FOLDER, filename)
                    image.save(image_path)
                    image_paths.append(f'uploads/{filename}')  # Save relative path

        # Save data to the database
        lease_data = {
            'location': location,
            'size': size,
            'price': price,
            'description': description,
            'images': image_paths,
            'approved': False  # By default, new leases are unapproved
        }
        add_land_listing(lease_data)  # Call the function to save to the database

        # Redirect to a confirmation page or another route
        return render_template('admin_panel/add-land-lease.html')

    # Render the form template if the request is GET
    return render_template('admin_panel/add-land-lease.html')

@admin_routes.route("/admin/add-listing.html", methods=['GET', 'POST'])
def add_listing():
    msg = ''
    if request.method == 'POST':
        location = request.form['location']
        size = request.form['size']
        price = float(request.form['price'])
        description = request.form['description']
        
        # Handle file uploads
        images = request.files.getlist('images')
        image_paths = []
        
        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)
                image_paths.append(image_path)
        
        if image_paths:
            add_listing_with_images(location, size, price, description, image_paths)
            msg = 'Land listing created successfully!'
        else:
            msg = 'Please upload at least one valid image!'

    return render_template('admin_panel/add-listing.html', msg=msg)

@admin_routes.route('/admin/settings.html', methods=['GET', 'POST'])
def submit_form():
    msg = ''
    if request.method == 'POST':
        # Pass the form data and the database connection to the function
        msg = process_user_data(request.form, db)

    return render_template('admin_panel/settings.html', msg=msg)

@admin_routes.route("/admin/unapproved_uploads.html")
def get_unapproved_land_listings():
    try:
        # Fetch unapproved land listings from the database
        listings_cursor = land_listing_collection.find()
        print("Am here:", listings_cursor)
        # Convert cursor to a list of dictionaries
        listings = []
        for listing in listings_cursor:
            print("Iam looking", listing)
            # Process the data as needed
            listings.append({
                '_id': str(listing['_id']),
                'user_name': listing.get('user_name', 'Unknown User'),  # Replace with actual user name field if available
                'land_size': listing.get('size', 'N/A'),
                'location': listing.get('location', 'N/A'),
                'price_per_acre': listing.get('price', 'N/A'),
                'description': listing.get('description', 'N/A'),
                'amenities': listing.get('amenities', 'N/A'),
                'images': listing.get('images', [])
            })

        return render_template('admin_panel/unapproved_uploads.html', land_listings=listings)

    except Exception as e:
        print(f"Error fetching unapproved land listings: {e}")
        return render_template('admin_panel/unapproved_uploads.html', land_listings=[])

@admin_routes.route("/admin/leases.html")
def leases():
    return render_template('admin_panel/leases.html')

@admin_routes.route("/admin/listings.html")
def listings():
    return render_template('admin_panel/listings.html')

@admin_routes.route("/admin/payments.html")
def payments():
    return render_template('admin_panel/payments.html')

@admin_routes.route("/admin/settings.html")
def settings():
    return render_template('admin_panel/settings.html')

@admin_routes.route("/admin/users.html", methods=['GET'])
def users():
    users = list(users_collection.find())
    return render_template('admin_panel/users.html', users=users)
# Serve CSS files from the 'admin_panel/css' directory
@admin_routes.route('/admin/css/<path:filename>')
def serve_admin_css(filename):
    return send_from_directory(os.path.join(frontend_path, 'css'), filename)

# Serve image files from the 'admin_panel/images' directory
@admin_routes.route('/admin/images/<path:filename>')
def serve_admin_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)

@admin_routes.route('/manage-users', methods=['GET'])
def manage_users():
    users = list(users_collection.find())
    return render_template('manage_users.html')

@admin_routes.route('/api/users', methods=['GET'])
def get_users():
    users = list(users_collection.find())
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(users)

@admin_routes.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    user_data = request.json
    users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': user_data})
    return jsonify({"message": "User updated successfully"})

# Route to delete a user
@admin_routes.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    users_collection.delete_one({'_id': ObjectId(user_id)})
    return jsonify({"message": "User deleted successfully"})