from flask import request, render_template, session
from pymongo import MongoClient
import gridfs

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
def save_images():
    upload_folder = 'static/uploads'  # Define your image storage path
    os.makedirs(upload_folder, exist_ok=True)

    profile_image = request.files.get('profile-picture')
    profile_image_path = None
    if profile_image:
        filename = secure_filename(profile_image.filename)
        profile_image_path = os.path.join(upload_folder, filename)
        profile_image.save(profile_image_path)

    return profile_image_path

# Save profile data in MongoDB
def save_profile_data(profile_data, next_of_kin_data, profile_image_path):
    profile_data['profile_image_path'] = profile_image_path
    profile_data['next_of_kin'] = next_of_kin_data

    existing_profile = profiles_collection.find_one({'email': profile_data['email']})
    if existing_profile:
        profiles_collection.update_one({'email': profile_data['email']}, {'$set': profile_data})
    else:
        profiles_collection.insert_one(profile_data)

@user_routes.route("/edit-profile.html", methods=['GET', 'POST'])
def profile():
    msg = ''
    if request.method == 'POST':
        # Extract form data
        profile_data, next_of_kin_data, msg = extract_and_validate_form_data()
        if msg:
            return render_template('edit-profile.html', msg=msg)

        # Save profile image
        profile_image_path = save_images()

        # Save profile data in the database
        save_profile_data(profile_data, next_of_kin_data, profile_image_path)

        msg = 'Profile updated successfully!'
    
    return render_template('edit-profile.html', msg=msg)