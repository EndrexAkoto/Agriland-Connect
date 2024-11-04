from flask import request, render_template, session
from pymongo import MongoClient
import gridfs
from datetime import datetime
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
        'email': email,  # Retrieved from session for security
        'phone': request.form.get('phone'),
        'id_number': request.form.get('idNumber'),
        'kra_pin': request.form.get('kraPin'),
        'dob': request.form.get('dob'),  # Assume dob is passed as a string to be converted later if needed
        'registration_date': datetime.now(),  # Add registration date if it’s a new record
    }

    next_of_kin_data = {
        'name': request.form.get('kinName'),
        'relationship': request.form.get('kinRelationship'),
    }

    # Validate required fields
    # required_fields = [profile_data['first_name'], profile_data['last_name'], profile_data['phone'], profile_data['id_number'], profile_data['kra_pin']]
    # if not all(required_fields):
    #     return None, None, 'Please fill out all required fields!'
    
    return profile_data, next_of_kin_data, ''


# Step 3: Function to handle image uploads
# def save_images():
#     profile_image = request.files.get('idImage')
    
#     profile_image_id = fs.put(profile_image, filename=profile_image.filename) if profile_image else None

#     return profile_image_id

# Step 4: Function to save profile data in the database
def save_images():
    profile_image = request.files.get('idImage')
    next_of_kin_image = request.files.get('nextOfKinIdImage')
    
    profile_image_id = None
    next_of_kin_image_id = None

    # Save the profile image if it exists
    if profile_image:
        profile_image_id = fs.put(profile_image, filename=profile_image.filename)
        print("Profile image saved with ID:", profile_image_id)  # Debugging line
    else:
        print("No profile image uploaded")  # Debugging line

    # Save the next of kin image if it exists
    if next_of_kin_image:
        next_of_kin_image_id = fs.put(next_of_kin_image, filename=next_of_kin_image.filename)
        print("Next of kin image saved with ID:", next_of_kin_image_id)  # Debugging line
    else:
        print("No next of kin image uploaded")  # Debugging line

    # Ensure a tuple is always returned
    return profile_image_id, next_of_kin_image_id

def save_profile_data(profile_data, next_of_kin_data, profile_image_id, next_of_kin_image_id):
    profile_data['profile_image_id'] = profile_image_id
    profile_data['next_of_kin'] = next_of_kin_data
    profile_data['next_of_kin_image_id'] = next_of_kin_image_id  # Add next of kin image ID to profile data
    
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

