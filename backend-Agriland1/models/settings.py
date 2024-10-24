from flask import current_app as app

def process_user_data(form_data, db):
    # Extract user role and other details from the form data
    user_role = form_data.get('user-role')
    email = form_data.get('email')
    password = form_data.get('password')
    name = form_data.get('name')
    phone = form_data.get('phone')
    site_status = form_data.get('site-status')

    # Depending on the role, insert the data into the appropriate collection
    if user_role == 'farmer':
        collection = db['farmers']
    elif user_role == 'landlord':
        collection = db['landlord']
    elif user_role == 'admin':
        collection = db['admins']
    else:
        return 'Invalid user role'

    # Create a document to insert
    user_data = {
        'email': email,
        'password': password,
        'name': name,
        'phone': phone,
        'site_status': site_status
    }

    # Insert the document into the corresponding collection
    collection.insert_one(user_data)
    return f'User data successfully added to the {user_role} collection.'