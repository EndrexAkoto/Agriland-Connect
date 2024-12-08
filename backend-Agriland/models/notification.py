from datetime import datetime
from bson import ObjectId

def create_notification(user_id, title, message, type="info"):
    notification = {
        "user_id": ObjectId(user_id),
        "title": title,
        "message": message,
        "type": type,
        "is_read": False,
        "created_at": datetime.utcnow(),
        "read_at": None
    }
    db['notifications'].insert_one(notification)