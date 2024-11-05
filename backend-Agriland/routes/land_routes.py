from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from models.land import land_collection  # Import your land model
from bson import ObjectId  # To work with MongoDB ObjectId
from utils.helpers import *
import os

land_routes = Blueprint('land', __name__)



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
        user_id = session.get('id')  # Get user ID from session
        username = session.get('username')
        print(user_id & username)  # Get username from session

        if not user_id or not username:
            return redirect(url_for('user.login'))  # Redirect if not logged in



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

        if not all([land_size, location, price_per_acre, amenities, road_access, fencing, title_deed, lease_duration, payment_frequency]):
            return render_template('landlord.html', msg='Please fill out all fields!')

        
        land_listing_data = {
            'land_size': land_size,
            'location': location,
            'price_per_acre': price_per_acre,
            'amenities': amenities,
            'road_access': road_access,
            'fencing': fencing,
            'title_deed': title_deed,
            'lease_duration': lease_duration,
            'payment_frequency': payment_frequency,
            'farm_images': []
        }
        
        # Insert and retrieve the ObjectId
        result = land_collection.insert_one(land_listing_data)
        listing_id = str(result.inserted_id)  # MongoDB ObjectId as a string
        
        # Set up directory to store images based on ObjectId
        listing_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], listing_id, 'images')
        os.makedirs(listing_folder, exist_ok=True)
        
        # Process uploaded image files and save them in the ObjectId directory
        files = request.files.getlist('farmImages')
        image_filenames = []

        for file in files:
            if file and allowed_file(file.filename):
                image_filename = secure_filename(file.filename)
                file_path = os.path.join(listing_folder, image_filename)
                file.save(file_path)
                image_filenames.append(image_filename)

        # Update MongoDB with the filenames for this listing
        land_collection.update_one(
            {'_id': ObjectId(listing_id)},
            {'$set': {'farm_images': image_filenames}}
        )
        
        return render_template('landlord.html', msg='Land listing submitted successfully!')
    
    return render_template('landlord.html', msg='')




@land_routes.route("/land-listings.html")
def land_listings():
    listings = get_all_land_listings()
    return render_template('land-listings.html', listings=listings)
