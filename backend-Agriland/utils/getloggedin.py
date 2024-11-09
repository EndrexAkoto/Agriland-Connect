from flask import session

def get_logged_in_user():
    """Retrieve logged-in user data from session."""
    user_id = session.get("id")
    username = session.get("username")
    
    if user_id and username:
        return {"user_id": user_id, "username": username}
    return None
