from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, jsonify, current_app, send_file
from flask import current_app as app
from models.user import get_user_by_email, create_user
from models.stats import get_user_statistics
from models.land import add_land_listing, get_all_land_listings, add_listing_with_images
from models.settings import process_user_data, manage_user_status
from gridfs import GridFS
from bson import ObjectId
from pymongo import MongoClient
from db import db
from werkzeug.utils import secure_filename
import os

admin_routes = Blueprint('admin', __name__)
frontend_path = '/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland/admin_panel'
UPLOAD_FOLDER = '/home/hp/Agrilandproj/Agriland-Connect/backend-Agriland/static/uploads'
upload_path = "/home/hp/Agrilandproj/Agriland-Connect/backend-Agriland/uploads"
client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']
land_listing_collection = db['land_listings']
counties_collection = db['Counties']
fs = GridFS(db)

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

def add_land_listing(lease_data):
    result = db['land_listings'].insert_one(lease_data)
    return result.inserted_id  # Return the inserted_id, not the entire result

# In the add_land_lease route, update the listing_id handling:
@admin_routes.route("/admin/add-land-lease.html", methods=['GET', 'POST'])
def add_land_lease():
    msg = ''
    if request.method == 'POST':
        # Get form data
        location = request.form.get('location')
        size = request.form.get('size')
        price = request.form.get('price')
        description = request.form.get('description')

        # Ensure all required fields are filled
        if not all([location, size, price, description]):
            msg = 'Please fill out all fields!'
            counties = db['Counties'].find({}, {'_id': 0, 'County': 1})
            county_names = [county['County'] for county in counties]
            return render_template('admin_panel/add-land-lease.html', county_names=county_names, msg=msg)

        # Prepare data for database insertion
        lease_data = {
            'name': "admin",
            'location': location,
            'land_size': size,
            'price_per_acre': price,
            'description': description,
            'images': [],
            'approved': "False"  # By default, new leases are unapproved
        }

        # Insert the data into the database and retrieve the ObjectId
        try:
            listing_id = add_land_listing(lease_data)  # This now returns only the inserted _id (ObjectId)
        except Exception as e:
            msg = f'An error occurred while saving the lease: {e}'
            counties = db['Counties'].find({}, {'_id': 0, 'County': 1})
            county_names = [county['County'] for county in counties]
            return render_template('admin_panel/add-land-lease.html', county_names=county_names, msg=msg)

        # Set up directory to store images based on ObjectId
        listing_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(listing_id), 'images')
        os.makedirs(listing_folder, exist_ok=True)

        # Process uploaded image files and save them in the ObjectId directory
        images = request.files.getlist('images')
        image_filenames = []

        for image in images:
            if image and allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                file_path = os.path.join(listing_folder, image_filename)
                image.save(file_path)
                image_filenames.append(image_filename)

        # Update MongoDB with the filenames for this listing
        try:
            db['land_listings'].update_one(
                {'_id': ObjectId(listing_id)},
                {'$set': {'images': image_filenames}}
            )
            msg = 'Lease successfully added!'
        except Exception as e:
            msg = f'An error occurred while saving images: {e}'

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
                # Save images in listing-specific folder
                listing_id = str(ObjectId())  # Generate a new listing ID
                listing_directory = os.path.join(upload_path, listing_id, 'images')
                
                # Ensure the directory exists
                os.makedirs(listing_directory, exist_ok=True)
                
                image_path = os.path.join(listing_directory, filename)
                image.save(image_path)
                image_paths.append(f'uploads/{listing_id}/images/{filename}')
        
        if image_paths:
            # You need to pass listing_id as argument for add_listing_with_images() to associate images with correct listing
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
            'user_name': listing.get('name', 'Unknown User'),
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
                f"/admin/uploads/{str(listing['_id'])}/images/{image_filename}"
                for image_filename in listing.get('images', [])
            ] if listing.get('images') else []
        }
        for listing in land_listing_collection.find({'approved': 'False'})
    ]
    
    return render_template('admin_panel/unapproved_uploads.html', listings=listings)


@admin_routes.route("/admin/rejected-land-leases.html", methods=["GET"])
def leases():
    return render_template('admin_panel/rejected-land-leases.html')

@admin_routes.route("/api/rejected-leases", methods=["GET"])
def fetch_rejected_leases():
    # Query for rejected land leases
    rejected_leases = [
        {
            '_id': str(lease['_id']),
            'name': lease.get('name', 'Unknown User'),
            'reason': lease.get('message', 'No reason provided'),
            'land_size': lease.get('land_size', 'N/A'),
            'location': lease.get('location', 'N/A'),
            'price_per_acre': lease.get('price_per_acre', 'N/A'),
            'images': [
                f"/admin/uploads/{str(lease['_id'])}/images/{image_filename}"
                for image_filename in lease.get('images', [])
            ] if lease.get('images') else []
        }
        for lease in land_listing_collection.find({'approved': 'Rejected'})
    ]
    return jsonify({'rejectedLeases': rejected_leases})

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
    return render_template('admin_panel/users.html', users=users)

@admin_routes.route("/admin/user-details/<user_id>")
def user_details(user_id):
    # Fetch the user details from the database
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return render_template('404.html')  # Handle user not found

    # Extract ID image details
    id_image_id = user.get("id_image_id")
    id_image_url = None
    if id_image_id:
        id_image_url = f"/admin/user-details/{user_id}/id-image"  # Create a route to serve the image

    user_data = {
        "id_number": user.get("id_number", "N/A"),
        "kra_pin": user.get("kra_pin", "N/A"),
        "phone_number": user.get("phone", "N/A"),
        "id_image_url": id_image_url
    }
    return render_template('admin_panel/user_details.html', user=user_data)

@admin_routes.route("/admin/user-details/<user_id>/id-image")
def serve_id_image(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("id_image_id"):
        return "Image not found", 404  # Handle cases where the image doesn't exist

    # Fetch the image from GridFS
    gridfs_id = user["id_image_id"]
    image_file = fs.get(ObjectId(gridfs_id))

    # Serve the file as a response
    return send_file(image_file, mimetype="image/jpeg") 

# Serve CSS files from the 'admin_panel/css' directory
@admin_routes.route('/admin/css/<path:filename>')
def serve_admin_css(filename):
    return send_from_directory(os.path.join(frontend_path, 'css'), filename)

# Serve image files from the 'admin_panel/images' directory
@admin_routes.route('/admin/images/<path:filename>')
def serve_admin_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)