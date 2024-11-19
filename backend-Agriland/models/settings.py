from flask import current_app as app
from bson import ObjectId

def process_user_data(form_data, db):
    # Extract user details from the form data
    first_name = form_data.get('first-name')
    middle_name = form_data.get('middle-name', '')  # Optional
    last_name = form_data.get('last-name')
    id_number = form_data.get('id-number')
    phone = form_data.get('phone')
    email = form_data.get('email')
    dob = form_data.get('dob')
    role = form_data.get('role')

    # Select the correct collection based on role
    if role == 'farmer':
        collection = db['farmer']
    elif role == 'landlord':
        collection = db['land_listings']
    elif role == 'admin':
        collection = db['admins']
    else:
        return 'Invalid role selected'

    # Create user document
    user_data = {
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'id_number': id_number,
        'phone': phone,
        'email': email,
        'dob': dob,
        'role': role
    }

    # Insert the document into the collection
    collection.insert_one(user_data)
    return f'User data successfully added to the {role} collection.'

def manage_user_status(email, db, action):
    # Find the user in all relevant collections
    for role in ['users', 'admins']:
        collection = db[role]
        user = collection.find_one({"email": email})
        
        if user:
            if action == 'terminate':
                if user.get('status') == 'deactivated':
                    return f'The user with email {email} is already deactivated.'
                else:
                    collection.update_one({"email": email}, {"$set": {"status": "deactivated"}})
                    return f'The user with email {email} has been terminated and status set to deactivated.'

            elif action == 'reset':
                if user.get('status') == 'deactivated':
                    collection.update_one({"email": email}, {"$set": {"status": "active"}})
                    return f'The user with email {email} was deactivated and has now been set to active.'
                else:
                    return f'The user with email {email} is already active.'
    
    return f'No user found with email {email}.'