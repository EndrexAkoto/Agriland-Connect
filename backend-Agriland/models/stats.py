from pymongo import MongoClient
from datetime import datetime

client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['users']  # Use 'profiles' as per your description
leases_collection = db['land_listings']
payments_collection = db['payments']

def categorize_age_bracket(age):
    """Categorizes the given age into specific age brackets."""
    if 18 <= age <= 25:
        return '18-25'
    elif 26 <= age <= 35:
        return '26-35'
    elif 36 <= age <= 50:
        return '36-50'
    return 'Other'

def calculate_lease_rate_by_county():
    """Calculates average lease rates by county."""
    pipeline = [
        {"$match": {"price_per_acre": {"$exists": True, "$ne": ""}}},  # Ensure valid price_per_acre
        {
            "$group": {
                "_id": "$location",
                "average_lease_rate": {"$avg": {"$toDouble": "$price_per_acre"}}
            }
        },
        {"$project": {"county": "$_id", "average_lease_rate": 1, "_id": 0}}
    ]
    results = leases_collection.aggregate(pipeline)
    return {result["county"]: result["average_lease_rate"] for result in results}

def get_user_statistics():
    try:
        # Calculate general user statistics
        total_users = users_collection.count_documents({})
        one_month_ago = datetime.today().replace(day=1)
        new_users = users_collection.count_documents({'registration_date': {'$gte': one_month_ago}})
        farmers = users_collection.count_documents({'role': 'farmer'})
        landowners = users_collection.count_documents({'role': 'landowner'})
        total_males = users_collection.count_documents({'gender': 'male'})
        total_females = users_collection.count_documents({'gender': 'female'})
        male_percentage = (total_males / total_users) * 100 if total_users > 0 else 0
        female_percentage = (total_females / total_users) * 100 if total_users > 0 else 0

        # Age bracket calculation based on the 'age' field
        age_brackets = {'18-25': 0, '26-35': 0, '36-50': 0, 'Other': 0}
        users = users_collection.find({}, {'age': 1})
        for user in users:
            age = user.get('age')
            if isinstance(age, int):
                bracket = categorize_age_bracket(age)
                age_brackets[bracket] += 1
        age_brackets_percentage = {k: (v / total_users) * 100 if total_users > 0 else 0 for k, v in age_brackets.items()}

        # Other statistics
        active_leases = leases_collection.count_documents({'approved': "False"})
        total_listings = leases_collection.count_documents({})
        pending_payments = payments_collection.count_documents({'Payment Status': 'Completed'})
        county_lease_counts = {}
        leases = leases_collection.find({}, {'location': 1})
        for lease in leases:
            location = lease.get('location', 'Unknown')
            if location:
                county_lease_counts[location] = county_lease_counts.get(location, 0) + 1
        county_lease_rates = calculate_lease_rate_by_county()

        # Return all statistics
        return {
            'Total Users': total_users,
            'New Users': new_users,
            'Farmers': farmers,
            'Landowners': landowners,
            'Gender Distribution': {
                'Male': male_percentage,
                'Female': female_percentage
            },
            'Age Bracket': age_brackets_percentage,
            'Active Leases': active_leases,
            'Total Listings': total_listings,
            'Pending Payments': pending_payments,
            'County Lease Counts': county_lease_counts,
            'County Lease Rates': county_lease_rates 
        }

    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        return None