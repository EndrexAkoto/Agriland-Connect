from flask import Blueprint, render_template, request, current_app, session, redirect, url_for

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
        approved = False

        # Validate form fields and files
        files = request.files.getlist('farmImages')
        print(f"Received files: {files}")  # Debug: Check received files

        if not all([land_size, location, price_per_acre, amenities, road_access, fencing, title_deed, lease_duration, payment_frequency]) or not files:
            return render_template('landlord.html', msg='Please fill out all fields and upload at least one image!')

        # Prepare data for MongoDB
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
            'approved': approved,
            'farm_images': []  # Placeholder for image IDs
        }

        # Insert initial document without images to get ObjectId
        result = land_collection.insert_one(land_listing_data)
        listing_id = result.inserted_id
        print(f"Inserted land listing with ID: {listing_id}")  # Debug: Check if the initial document is inserted correctly

        # Save each uploaded image to GridFS
        image_ids = []
        for file in files:
            if file:
                print(f"File: {file.filename}")  # Debug: Check if file is being processed
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_id = fs.put(file, filename=filename, listing_id=listing_id)  # Associate with the listing
                    image_ids.append(file_id)
                    print(f"Stored file with ID: {file_id}")  # Debug: Check if file is stored in GridFS correctly
                else:
                    print("File type not allowed.")  # Debug: Check if file is valid
            else:
                print("Empty file received.")  # Debug: Check if any empty files are received

        print(f"Image IDs to be updated: {image_ids}")  # Debug: Check the image IDs to be saved in MongoDB

        # Update MongoDB document with GridFS image IDs
        land_collection.update_one(
            {'_id': listing_id},
            {'$set': {'farm_images': image_ids}}
        )
        print("Updated MongoDB document with image IDs.")  # Debug: Check if the update operation is executed

        return render_template('landlord.html', msg='Land listing submitted successfully!')

    # Render form with county names
    counties = counties_collection.find({}, {'_id': 0, 'County': 1})
    county_names = [county['County'] for county in counties]
    return render_template('landlord.html', county_names=county_names, msg='')
