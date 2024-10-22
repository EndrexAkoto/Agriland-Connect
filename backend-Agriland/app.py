from flask import Flask
from pymongo import MongoClient
from routes import user_routes, admin_routes, land_routes
import os
from db import db

static_folder=os.path.abspath('/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland/images')
app = Flask(__name__, template_folder='../frontend-Agriland', static_folder="../frontend-Agriland")
frontend_path = '/home/hp/Desktop/Agriland/Agriland-Connect/frontend-Agriland'

# Register blueprints
app.register_blueprint(user_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(land_routes)

if __name__ == '__main__':
    app.run(debug=True)
