from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['Agriconnect']

land_collection = db['land_listings']

# Define functions related to land operations
def add_land_listing(land_data):
    result = land_collection.insert_one(land_data)
    return result.inserted_id if result.acknowledged else None

def get_all_land_listings():
    return land_collection.find()

def get_land_listing_by_id(listing_id):
    return land_collection.find_one({'_id': listing_id})

def add_listing_with_images(location, size, price, description, image_paths):
    land_data = {
        'location': location,
        'size': size,
        'price': price,
        'description': description,
        'images': image_paths
    }
    add_land_listing(land_data)

def get_field(listing, *keys, default='N/A'):
    """
    Retrieve the first matching key from the listing dictionary.
    If no key is found, return the default value.
    """
    for key in keys:
        if key in listing:
            return listing[key]
    return default
