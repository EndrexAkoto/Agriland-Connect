from flask import Flask
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from pymongo import MongoClient
from routes import user_routes, admin_routes, land_routes
import os
from db import db
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
frontend_path = '/home/hp/Agrilandproj/Agriland-Connect/frontend-Agriland'
app = Flask(__name__, template_folder='../frontend-Agriland', static_folder="../frontend-Agriland")
app.secret_key = 'c30b7150c42e87caef910ca5aebddbcce8309d5f' 
app.config['UPLOAD_FOLDER'] = './uploads'
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Register blueprints
app.register_blueprint(user_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(land_routes)

if __name__ == '__main__':
    app.run(debug=True)
