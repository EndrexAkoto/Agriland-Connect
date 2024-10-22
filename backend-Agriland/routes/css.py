from flask import Blueprint, render_template, request, redirect, url_for, session
from models.user import get_user_by_email, create_user
import re

@app.route('/admin/css/<path:filename>')
def serve_admin_css(filename):
    return send_from_directory(os.path.join(frontend_path, 'admin_panel', 'css'), filename)

@app.route('/admin/images/<path:filename>')
def serve_admin_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'admin_panel', 'images'), filename)

@app.route('/admin/js/<path:filename>')
def serve_admin_js(filename):
    return send_from_directory(os.path.join(frontend_path, 'admin_panel', 'js'), filename)

# Serve other static files
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(frontend_path, 'images'), filename)

@app.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join(frontend_path, 'styles'), filename)