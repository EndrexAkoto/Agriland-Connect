from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, request, jsonify
from flask import current_app as app
from models.user import get_user_by_email, create_user
from models.stats import  get_user_statistics
from models.land import add_land_listing, get_all_land_listings, add_listing_with_images
from models.settings import process_user_data, manage_user_status
from bson import ObjectId
from pymongo import MongoClient 
from db import db 
from werkzeug.utils import secure_filename
import re
import os

admin_routes = Blueprint('admin', __name__)
frontend_path = '/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland/admin_panel'
UPLOAD_FOLDER = '/home/hp/Agrilandproj/Agriland-Connect/'
upload_path = "/home/hp/Agrilandproj/Agriland-Connect/backend-Agriland/uploads"
client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']
land_listing_collection = db['land_listings']
counties_collection = db['Counties']

# Serve the 'index.html' file from the admin panel directory
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@admin_routes.route("/admin/index.html")
def admin_html():
     stats = get_user_statistics()
     return render_template('admin_panel/index.html', stats=stats)

@admin_routes.route("/api/user-stats", methods=["GET"])
def user_stats():
    stats = get_user_statistics()
    if stats:
        return jsonify(stats)
    else:
        return jsonify({"error": "Unable to fetch statistics"}), 500

@admin_routes.route("/admin/add-land-lease.html", methods=['GET', 'POST'])
def add_land_lease():
    msg = ''
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
        
        # Attempt to add the lease to the database
        try:
            result = add_land_listing(lease_data)  # Call the function to save to the database
            if result:  # If insertion returns a result, consider it successful
                msg = 'Lease successfully added!'
            else:
                msg = 'Failed to add lease. Please try again.'
        except Exception as e:
            msg = f'An error occurred: {e}'
        
        # Render the form template with a success or error message
        counties = db['Counties'].find({}, {'_id': 0, 'County': 1})
        county_names = [county['County'] for county in counties]
        return render_template('admin_panel/add-land-lease.html', county_names=county_names, msg=msg)
    
    # Render the form template if the request is GET
    counties = db['Counties'].find({}, {'_id': 0, 'County': 1})
    county_names = [county['County'] for county in counties]
    return render_template('admin_panel/add-land-lease.html', county_names=county_names, msg='')

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
        # Check which form is submitted
        if 'reset-email' in request.form:
            email = request.form.get('reset-email')
            msg = manage_user_status(email, db, action='reset')
        elif 'terminate-email' in request.form:
            email = request.form.get('terminate-email')
            msg = manage_user_status(email, db, action='terminate')
        else:
            # Process user data for adding a new user
            msg = process_user_data(request.form, db)

    return render_template('admin_panel/settings.html', msg=msg)

@admin_routes.route("/admin/unapproved_uploads.html", methods=["GET", "POST"])
def unapproved_uploads():
    # Handle form submission (approval, rejection, pending)
    if request.method == "POST":
        listing_id = request.form["_id"]
        action = request.form["action"]
        message = request.form.get("message", "")  # Optional rejection message

        # Set the status update based on the action
        if action == "approve":
            status_update = {"approved": "True", "message": ""}
        elif action == "reject":
            status_update = {"approved": "Rejected", "message": message}
        elif action == "pending":
            status_update = {"approved": "Pending Verification", "message": ""}
        
        # Update the listing in the database
        land_listing_collection.update_one({"_id": ObjectId(listing_id)}, {"$set": status_update})
        
        # Redirect to refresh the listings view
        return redirect(url_for("admin.unapproved_uploads"))
    
    # If GET request, fetch and display unapproved listings
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
            'images': [
                f"/admin/uploads/{str(listing['_id'])}/images/{listing.get('farm_image', '')}"
            ] if listing.get('farm_image') else []
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


@admin_routes.route('/admin/uploads/<listing_id>/images/<filename>')
def serve_uploaded_image(listing_id, filename):
    images_directory = os.path.join(upload_path, listing_id, 'images')
    return send_from_directory(images_directory, filename)

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