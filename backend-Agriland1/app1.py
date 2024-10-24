from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import re
import os

static_folder=os.path.abspath('/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland/images')
app = Flask(__name__, template_folder=os.path.abspath('/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland'), static_folder=static_folder)
app.secret_key = 'c30b7150c42e87caef910ca5aebddbcce8309d5f'

client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']
profiles_collection = db['profiles']
land_collection = db['land_listings']
frontend_path = '/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'

# Define the folder to upload images to

app.config['UPLOAD_FOLDER'] = static_folder

# Define allowed file extensions for images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# CSs and Images
@app.route('/admin/css/<path:filename>')
def serve_admin_css(filename):
    return send_from_directory(os.path.join(frontend_path, 'admin_panel', 'css'), filename)

@app.route('/admin/images/<path:filename>')
def serve_admin_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'admin_panel', 'images'), filename)

@app.route('/admin/js/<path:filename>')
def serve_admin_js(filename):
    return send_from_directory(os.path.join(frontend_path, 'admin_panel', 'js'), filename)

# Serve other static files
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)

@app.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join(frontend_path, 'styles'), filename)

# css and images 

#  USER HTMLS
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        username = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': username, 'password': password})
        if user:
            session['loggedin'] = True
            session['id'] = str(user['_id'])
            session['email'] = user['email']
            session['password']  = user['password']
            msg = 'Logged in successfully!'
            return render_template('dashboard.html', msg=msg)
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user = users_collection.find_one({'username': username})
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            users_collection.insert_one({'username': username, 'password': password, 'email': email})
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('signup.html', msg=msg)

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/land_listings.html')
def land_listings():
    return render_template('land-listings.html')

@app.route('/find_land.html')
def find_land():
    return render_template('find-land.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/edit-profile.html', methods=['GET', 'POST'])
def editprofile():
    msg = ''
    if request.method == 'POST':
        # Get all form data
        first_name = request.form.get('firstName')
        middle_name = request.form.get('middleName')
        last_name = request.form.get('lastName')
        gender = request.form.get('gender')
        email = request.form.get('email')
        phone = request.form.get('phone')
        id_number = request.form.get('idNumber')
        kra_pin = request.form.get('kraPin')
        dob = request.form.get('dob')
        pobox = request.form.get('pobox')
        county = request.form.get('county')
        town = request.form.get('town')

        # Next of Kin information
        next_of_kin_name = request.form.get('nextOfKinName')
        next_of_kin_gender = request.form.get('nextOfKinGender')
        next_of_kin_phone = request.form.get('nextOfKinPhone')
        next_of_kin_id_number = request.form.get('nextOfKinIdNumber')
        next_of_kin_kra_pin = request.form.get('nextOfKinKraPin')

        # Validate email
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not first_name or not last_name or not email or not phone or not id_number or not kra_pin or not dob:
            msg = 'Please fill out all required fields!'
        else:
            # Create profile data dictionary
            profile_data = {
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'gender': gender,
                'email': email,
                'phone': phone,
                'id_number': id_number,
                'kra_pin': kra_pin,
                'dob': dob,
                'pobox': pobox,
                'county': county,
                'town': town,
                'next_of_kin': {
                    'name': next_of_kin_name,
                    'gender': next_of_kin_gender,
                    'phone': next_of_kin_phone,
                    'id_number': next_of_kin_id_number,
                    'kra_pin': next_of_kin_kra_pin
                }
            }

            # Check if the profile already exists (based on email)
            existing_profile = profiles_collection.find_one({'email': email})
            if existing_profile:
                # Update the existing profile
                profiles_collection.update_one({'email': email}, {'$set': profile_data})
                msg = 'Profile updated successfully!'
            else:
                # Insert new profile into collection
                profiles_collection.insert_one(profile_data)
                msg = 'Profile created successfully!'
        
        # Always return a response after processing the form
        return render_template('edit-profile.html', msg=msg)

    # For GET requests, render the edit profile form
    return render_template('edit-profile.html', msg=msg)

@app.route('/farmer.html', methods=['GET', 'POST'])
def farmer():
    if request.method == 'POST':
        # Get form data
        land_size = request.form.get('landSize')
        location = request.form.get('location')
        crop_type = request.form.get('cropType')
        payment_method = request.form.get('paymentMethod')

        # Validate form data
        if not land_size or not location or not crop_type or not payment_method:
            return render_template('farmer.html', msg='Please fill out all fields!')
        
        # Create land request data dictionary
        land_request_data = {
            'land_size': land_size,
            'location': location,
            'crop_type': crop_type,
            'payment_method': payment_method
        }

        # Insert the land request into MongoDB
        try:
            db['farmer'].insert_one(land_request_data)
            msg = 'Land request submitted successfully!'
        except Exception as e:
            msg = f"An error occurred while submitting your request: {str(e)}"

        # Render the form again with a success/failure message
        return render_template('farmer.html', msg=msg)

    # Render the form if method is GET
    return render_template('farmer.html', msg='')


@app.route('/landlord.html', methods=['GET', 'POST'])
def landlord():
    if request.method == 'POST':
        # Get form data
        land_size = request.form.get('landSize')
        location = request.form.get('location')
        price_per_acre = request.form.get('pricePerAcre')
        amenities = request.form.get('amenities')
        road_access = request.form.get('roadAccess')
        fencing = request.form.get('fencing')
        title_deed = request.form.get('titleDeed')
        lease_duration = request.form.get('leaseDuration')
        payment_frequency = request.form.get('paymentFrequency')

        # Process single uploaded file (farm image)
        file = request.files.get('farmImages')
        image_filename = None

        print(f"land_size: {land_size}, location: {location}, image: {file}")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_filename = filename
        
        # Validate form data
        if not (land_size and location and price_per_acre and amenities and road_access and fencing and title_deed and lease_duration and payment_frequency and image_filename):
            return render_template('landlord.html', msg='Please fill out all fields and upload an image!')
        
        # Create land listing data dictionary
        land_listing_data = {
            'land_size': land_size,
            'location': location,
            'price_per_acre': price_per_acre,
            'amenities': amenities,
            'road_access': road_access,
            'fencing': fencing,
            'title_deed': title_deed,
            'farm_image': image_filename,  # Save filename for reference
            'lease_duration': lease_duration,
            'payment_frequency': payment_frequency
        }

        # Insert the land listing into MongoDB
        try:
            land_collection.insert_one(land_listing_data)
            msg = 'Land listing submitted successfully!'
        except Exception as e:
            msg = f"An error occurred while submitting your listing: {str(e)}"

        # Render the form again with a success/failure message
        return render_template('landlord.html', msg=msg)

    # Render the form if method is GET
    return render_template('landlord.html', msg='')

@app.route('/land-listings.html')
def landlistings():
    land_listings = land_collection.find()
    return render_template('land-listings.html',  land_listings=land_listings)

@app.route('/full-listing.html')
def fulllisting():
    return render_template('full-listing.html')

@app.route('/leasing-listings.html')
def leasinglistings():
    return render_template('leasing-listing.html')

@app.route('/find-land.html')
def findland():
    return render_template('find-land.html')

@app.route('/payment.html')
def payment():
    return render_template('payment.html')

@app.route('/transactions.html')
def transactions():
    return render_template('transactiond.html')

@app.route('/user-profile.html')
def userprofile():
    return render_template('user-profile.html')

@app.route('/lease-agreements.html')
def leaseagreements():
    return render_template('lease-agreements.html')

@app.route('/full-listings.html')
def fulllistings():
    return render_template('full-listings.html')

if __name__ == '__main__':
    app.run(debug=True)
