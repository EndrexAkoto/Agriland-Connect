from flask import request, render_template, session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import gridfs
import os
from datetime import datetime
# Database connection
client = MongoClient('localhost', 27017)
db = client['Agriconnect']
profiles_collection = db['users']
fs = gridfs.GridFS(db)



def extract_and_validate_form_data():
    email = session.get('email')
    if not email:
        return None, None, 'Invalid email address!'

    profile_data = {
        'first_name': request.form.get('firstName'),
        'middle_name': request.form.get('middleName'),
        'last_name': request.form.get('lastName'),
        'dob': request.form.get('dob'),
        'gender': request.form.get('gender'),
        'email': email,
        'phone': request.form.get('phone'),
        'id_number': request.form.get('idNumber'),
        'kra_pin': request.form.get('kraPin')
    }

    next_of_kin_data = {
        'name': request.form.get('kinName'),
        'relationship': request.form.get('kinRelationship')
    }

    return profile_data, next_of_kin_data, ''

# Save images to a specified path or database
def save_id_image():
    # Fetch the ID image from the request
    id_image = request.files.get('idImage')
    
    # Initialize the image ID to None
    id_image_id = None

    # Save the ID image if it was uploaded
    if id_image:
        id_image_id = fs.put(id_image, filename=id_image.filename)
        print("ID image saved with ID:", id_image_id)  # Debugging line
    else:
        print("No ID image uploaded")  # Debugging line

    return id_image_id


# Save profile data in MongoDB
def save_profile_data(profile_data, id_image_id):
    profile_data['id_image_id'] = id_image_id  # Add the ID image ID to profile data

    # Check if the profile exists and update or insert accordingly
    existing_profile = profiles_collection.find_one({'email': profile_data['email']})
    if existing_profile:
        result = profiles_collection.update_one({'email': profile_data['email']}, {'$set': profile_data})
        print("Profile updated with result:", result.modified_count)  # Debugging line
        return result.modified_count > 0
    else:
        result = profiles_collection.insert_one(profile_data)
        print("New profile inserted with ID:", result.inserted_id)  # Debugging line
        return result.inserted_id is not None