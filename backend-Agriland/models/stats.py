from pymongo import MongoClient
from datetime import datetime

client = MongoClient('localhost', 27017)
db = client['Agriconnect']
users_collection = db['profiles']  # Use 'profiles' as per your description
leases_collection = db['land_listings']
payments_collection = db['payments']

def calculate_age_bracket(dob):
    if not isinstance(dob, datetime):
        return 'Other'
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if 18 <= age <= 25:
        return '18-25'
    elif 26 <= age <= 35:
        return '26-35'
    elif 36 <= age <= 50:
        return '36-50'
    return 'Other'

def get_user_statistics():
    try:
        total_users = users_collection.count_documents({})
        one_month_ago = datetime.today().replace(day=1)
        new_users = users_collection.count_documents({'registration_date': {'$gte': one_month_ago}})
        farmers = users_collection.count_documents({'role': 'farmer'})
        landowners = users_collection.count_documents({'role': 'landowner'})
        total_males = users_collection.count_documents({'gender': 'male'})  # Ensure consistent case
        total_females = users_collection.count_documents({'gender': 'female'})  # Ensure consistent case
        male_percentage = (total_males / total_users) * 100 if total_users > 0 else 0
        female_percentage = (total_females / total_users) * 100 if total_users > 0 else 0

        users = users_collection.find({}, {'dob': 1})
        age_brackets = {'18-25': 0, '26-35': 0, '36-50': 0}
        for user in users:
            dob = user.get('dob')
            if dob and isinstance(dob, datetime):  # Ensure dob is a datetime object
                bracket = calculate_age_bracket(dob)
                if bracket in age_brackets:
                    age_brackets[bracket] += 1
        age_brackets_percentage = {k: (v / total_users) * 100 if total_users > 0 else 0 for k, v in age_brackets.items()}

        active_leases = leases_collection.count_documents({'status': 'active'})
        pending_payments = payments_collection.count_documents({'status': 'pending'})

        return {
            'Total Users': total_users,
            'New Users': new_users,
            'Farmers': farmers,
            'Landowners': landowners,
            'Gender Distribution': {
                'Male': male_percentage,
                'Female': female_percentage
            },
            'Age Bracket': {
                '18-25': age_brackets_percentage['18-25'],
                '26-35': age_brackets_percentage['26-35'],
                '36-50': age_brackets_percentage['36-50']
            },
            'Active Leases': active_leases,
            'Pending Payments': pending_payments
        }

    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        return None
