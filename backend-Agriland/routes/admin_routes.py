from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, request
from flask import current_app as app
from models.user import get_user_by_email, create_user
from models.stats import  get_user_statistics
from models.land import add_land_listing, get_all_land_listings, add_listing_with_images
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

@admin_routes.route("/admin/add-land-lease.html")
def add_land_lease():

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
def unapproved_uploads():
    # Query unapproved listings and transform to list, constructing image paths directly in the query result.
    listings = [
        {
            '_id': str(listing['_id']),
            'user_name': listing.get('user_name', 'Unknown User'),
            'land_size': listing.get('land_size', 'N/A'),
            'location': listing.get('location', 'N/A'),
            'price_per_acre': listing.get('price_per_acre', 'N/A'),
            'description': listing.get('description', 'N/A'),
            'amenities': listing.get('amenities', 'N/A'),
            'road_access': listing.get('road_access', 'N/A'),
            'fencing': listing.get('fencing', 'N/A'),
            'title_deed': listing.get('title_deed', 'N/A'),
            'lease_duration': listing.get('lease_duration', 'N/A'),
            'payment_frequency': listing.get('payment_frequency', 'N/A'),
            'images': [f"uploads/{str(listing['_id'])}/images/{listing.get('farm_image', '')}"]  # Construct image path
        }
        for listing in land_listing_collection.find({'approved': 'False'})
    ]

    return render_template('admin_panel/unapproved_uploads.html', listings=listings)


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

@admin_routes.route("/admin/users.html")
def users():
    users = list(users_collection.find())
    return render_template('admin_panel/users.html', users= users)
# Serve CSS files from the 'admin_panel/css' directory
@admin_routes.route('/admin/css/<path:filename>')
def serve_admin_css(filename):
    return send_from_directory(os.path.join(frontend_path, 'css'), filename)

# Serve image files from the 'admin_panel/images' directory
@admin_routes.route('/admin/images/<path:filename>')
def serve_admin_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)