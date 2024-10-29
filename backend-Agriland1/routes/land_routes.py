from flask import Blueprint, render_template, request
from models.land import land_collection  # Import your land model
from utils.helpers import *
from pymongo import  MongoClient

client = MongoClient('localhost', 27017)
db = client['Agriconnect']
land_collection = db['land_listings']

land_routes = Blueprint('land', __name__) 
Backend = '/home/hp/Agrilandproj/Agriland-Connect/backend-Agriland/routes'

@land_routes.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        image_filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        file.save(file_path)
        return "File uploaded successfully"
    return "No file uploaded"


@land_routes.route('/landlord.html', methods=['GET', 'POST'])
def landlord():
    if request.method == 'POST':
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

        # Process uploaded image file
        files = request.files.getlist('farmImages')  # Fetch all uploaded images
        image_filenames = []  # List to store filenames
        
        for file in files:
            if file and allowed_file(file.filename):  # Check if the file is allowed
                image_filename = secure_filename(file.filename)  # Secure the filename
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)  # Define file path
                file.save(file_path)  # Save the file
                image_filenames.append(image_filename)  # Store the filename
                
                # Debugging output to see the saved filename
                print(f"Image saved: {image_filename}")

        # Continue processing the other form data
        land_listing_data = {
            'land_size': land_size,
            'location': location,
            'price_per_acre': price_per_acre,
            'amenities': amenities,
            'road_access': road_access,
            'fencing': fencing,
            'title_deed': title_deed,
            'farm_images': image_filenames,  # Store list of filenames
            'lease_duration': lease_duration,
            'payment_frequency': payment_frequency
        }

        # Insert data into MongoDB
        try:
            land_collection.insert_one(land_listing_data)
            msg = 'Land listing submitted successfully!'
        except Exception as e:
            msg = f"An error occurred: {str(e)}"

        return render_template('landlord.html', msg=msg)

    return render_template('landlord.html', msg='')

@land_routes.route("/land-listings.html")
def land_listings():
    listings = get_all_land_listings()
    return render_template('land-listings.html', listings=listings)

