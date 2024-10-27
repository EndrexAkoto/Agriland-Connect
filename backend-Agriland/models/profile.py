from flask import request, render_template, session
from pymongo import MongoClient
import gridfs

# Database connection
client = MongoClient('localhost', 27017)
db = client['Agriconnect']
profiles_collection = db['users']
fs = gridfs.GridFS(db)



# Step 2: Function to extract and validate form data
def extract_and_validate_form_data():
    email = session.get('email')
    if not email:
        return None, None, 'Invalid email address!'

    profile_data = {
        'first_name': request.form.get('firstName'),
        'middle_name': request.form.get('middleName'),
        'last_name': request.form.get('lastName'),
        'gender': request.form.get('gender'),
        'email': email,
        'phone': request.form.get('phone'),
        'id_number': request.form.get('idNumber'),
        'kra_pin': request.form.get('kraPin'),
        'dob': request.form.get('dob'),
        'pobox': request.form.get('pobox'),
        'county': request.form.get('county'),
        'town': request.form.get('town')
    }

    next_of_kin_data = {
        'name': request.form.get('nextOfKinName'),
        'gender': request.form.get('nextOfKinGender'),
        'phone': request.form.get('nextOfKinPhone'),
        'id_number': request.form.get('nextOfKinIdNumber')
    }

    # Validate required fields
    required_fields = [profile_data['first_name'], profile_data['last_name'], profile_data['phone'], profile_data['id_number'], profile_data['kra_pin'], profile_data['dob']]
    if not all(required_fields):
        return None, None, 'Please fill out all required fields!'
    
    return profile_data, next_of_kin_data, ''

# Step 3: Function to handle image uploads
def save_images():
    profile_image = request.files.get('profile-picture')
    next_of_kin_image = request.files.get('nextOfKinIdImage')
    
    profile_image_id = fs.put(profile_image, filename=profile_image.filename) if profile_image else None
    next_of_kin_image_id = fs.put(next_of_kin_image, filename=next_of_kin_image.filename) if next_of_kin_image else None

    return profile_image_id, next_of_kin_image_id

# Step 4: Function to save profile data in the database
def save_profile_data(profile_data, next_of_kin_data, profile_image_id, next_of_kin_image_id):
    profile_data['profile_image_id'] = profile_image_id
    profile_data['next_of_kin'] = next_of_kin_data
    profile_data['next_of_kin']['next_of_kin_image_id'] = next_of_kin_image_id
    
    # Check if the profile exists, update or insert accordingly
    existing_profile = profiles_collection.find_one({'email': profile_data['email']})
    if existing_profile:
        profiles_collection.update_one({'email': profile_data['email']}, {'$set': profile_data})
    else:
        profiles_collection.insert_one(profile_data)
