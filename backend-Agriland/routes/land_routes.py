from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from flask import current_app as app
from models.land import land_collection  # Import your land model
from bson import ObjectId  # To work with MongoDB ObjectId
# from utils.helpers import *
import os
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from db import db 
import gridfs

land_routes = Blueprint('land', __name__)

client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']
land_collection = db['land_listings']
counties_collection = db['Counties'] 
upload_folder = "/home/hp/Agrilandproj/Agriland-Connect/backend-Agriland/uploads"
fs = gridfs.GridFS(db)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@land_routes.route('/upload', methods=['GET', 'POST'])
def upload_file():
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        image_filename = secure_filename(file.filename)
        # Save to UPLOAD_FOLDER directly
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        file.save(file_path)
        return "File uploaded successfully"
    return "No file uploaded"

@land_routes.route('/landlord.html', methods=['GET', 'POST'])
def landlord(): 
    msg = ''
    counties = counties_collection.find({}, {'_id': 0, 'County': 1})
    county_names = [county['County'] for county in counties]

    if request.method == 'POST':
        user_id = session.get('id')
        username = session.get('name')

        if not user_id or not username:
            return redirect(url_for('user.login'))

        # Collect form data
        land_size = request.form.get('landSize')
        location = request.form.get('location')
        price_per_acre = request.form.get('pricePerAcre')
        amenities = request.form.get('amenities')
        road_access = request.form.get('roadAccess')
        fencing = request.form.get('fencing')
        title_deed = request.form.get('titleDeed')
        lease_duration = request.form.get('leaseDuration')
        payment_frequency = request.form.get('paymentFrequency')
        description = request.form.get('description')
        files = request.files.getlist('images')  # Get list of uploaded images

        if not all([land_size, location, price_per_acre, amenities, road_access, fencing, title_deed, lease_duration, payment_frequency, description]) or not files:
            msg = 'Please fill out all fields and upload at least one image!'
            return msg  # Return plain message for fetch API response

        # Insert land listing data into MongoDB
        land_listing_data = {
            'name': username,
            'land_size': land_size,
            'location': location,
            'price_per_acre': price_per_acre,
            'amenities': amenities,
            'road_access': road_access,
            'fencing': fencing,
            'title_deed': title_deed,
            'lease_duration': lease_duration,
            'payment_frequency': payment_frequency,
            'description': description,
            'approved': "False",
            'images': []
        }

        try:
            result = land_collection.insert_one(land_listing_data)
            listing_id = result.inserted_id
        except Exception as e:
            print(f"Error inserting land listing: {e}")
            return "Error saving land listing."

        # Create directory for images
        listing_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(listing_id), 'images')
        os.makedirs(listing_folder, exist_ok=True)

        # Save images and update MongoDB
        image_filenames = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(listing_folder, filename)
                file.save(file_path)
                image_filenames.append(filename)

        try:
            land_collection.update_one({'_id': listing_id}, {'$set': {'images': image_filenames}})
            return "Land listing submitted successfully!"
        except Exception as e:
            print(f"Error updating land listing with images: {e}")
            return "Error saving images."

    return render_template('landlord.html', county_names=county_names, msg=msg)


