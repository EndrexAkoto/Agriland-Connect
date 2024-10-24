from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
import re

@app.route('/frontend-Agriland/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        