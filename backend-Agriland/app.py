from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from pymongo import MongoClient
import re
import os

app = Flask(__name__, template_folder=os.path.abspath('/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland'), static_folder=os.path.abspath('/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland/images'))
app.secret_key = 'c30b7150c42e87caef910ca5aebddbcce8309d5f'

client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']
profiles_collection = db['profiles']
frontend_path = '/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'

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
    return send_from_directory(frontend_path, 'index.html')

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




if __name__ == '__main__':
    app.run(debug=True)
