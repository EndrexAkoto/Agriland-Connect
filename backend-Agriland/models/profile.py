from flask import request, render_template, session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import gridfs
import os
from datetime import datetime
from bson.objectid import ObjectId
# Database connection
client = MongoClient('localhost', 27017)
db = client['Agriconnect']
profiles_collection = db['users']
fs = gridfs.GridFS(db)



def extract_and_validate_form_data():
    email = session.get('email')
    if not email:
        return None, None, 'Invalid email address!'

    dob_str = request.form.get('dob')
    age = calculate_age(dob_str) if dob_str else None

    # Profile data
    profile_data = {
        'first_name': request.form.get('firstName'),
        'middle_name': request.form.get('middleName'),
        'last_name': request.form.get('lastName'),
        'dob': dob_str,
        'age': age,
        'gender': request.form.get('gender'),
        'email': email,
        'phone': request.form.get('phone'),
        'id_number': request.form.get('idNumber'),
        'kra_pin': request.form.get('kraPin')
    }

    # Next of kin data
    next_of_kin_data = {
        'name': request.form.get('kinName'),
        'relationship': request.form.get('kinRelationship')
    }

    return profile_data, next_of_kin_data, ''

def calculate_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return None 
# Save images to a specified path or database
def save_id_image():
    id_image = request.files.get('idImage')
    if id_image:
        id_image_id = fs.put(id_image, filename=id_image.filename)
        return id_image_id
    return None


# Save profile data in MongoDB
def save_profile_data(profile_data, next_of_kin_data, profile_picture_id, id_image_id):
    # Add images to the profile data
    profile_data['profile_picture_id'] = profile_picture_id
    profile_data['id_image_id'] = id_image_id
    profile_data['next_of_kin'] = next_of_kin_data

    existing_profile = profiles_collection.find_one({'email': profile_data['email']})
    if existing_profile:
        # Update existing profile
        profiles_collection.update_one({'email': profile_data['email']}, {'$set': profile_data})
    else:
        # Insert new profile
        profiles_collection.insert_one(profile_data)

def get_user_by_id(user_id):
    try:
        user_object_id = ObjectId(user_id)
        user = profiles_collection.find_one({"_id": user_object_id})
        return user if user else None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def save_profile_picture():
    profile_picture = request.files.get('profile-picture')
    if profile_picture:
        profile_picture_id = fs.put(profile_picture, filename=profile_picture.filename)
        return profile_picture_id
    return None