from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['Agriconnect']

users_collection = db['users']

# Define user-related functions, e.g., registration, authentication
def create_user(user_data):
    users_collection.insert_one(user_data)

def get_user_by_email(email):
    return users_collection.find_one({'email': email})

def authenticate_user(email, password):
    return users_collection.find_one({'email': email, 'password': password})

def total_users_view():
    total_users = get_total_users()