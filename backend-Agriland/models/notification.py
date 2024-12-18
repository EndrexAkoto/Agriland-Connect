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

def get_user_notifications(user_id, unread_only=False):
    query = {"user_id": ObjectId(user_id)}
    if unread_only:
        query["is_read"] = False
    notifications = list(db['notifications'].find(query).sort("created_at", -1))
    return notifications

def mark_notification_as_read(notification_id):
    db['notifications'].update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
    )

