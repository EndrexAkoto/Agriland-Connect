from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import time
import base64
import json

app = Flask(__name__)

# M-Pesa API credentials
consumer_key = "fHRzqNPpLxHaEWeSHo65nu4kemzHhj9NYrV1G0a45laWJxvd"
consumer_secret = "crGkPmlQhDYwOEtWtR0uqjmlbZG9Iq6vi4Ku9GfOEhgbmKrAtrubsUO8pk5Nt01Z"

# M-Pesa API URLs
api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

# Function to get access token
def get_access_token():
    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return json.loads(response.text)['access_token']

# Function to make STK push request
def make_stk_push_request(access_token, payload):
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = requests.post(stk_push_url, json=payload, headers=headers)
    return response.text

# Function to generate password
def generate_password(passcode, timestamp):
    return base64.b64encode(bytes(u'174379' + passcode + timestamp, 'UTF-8')).decode('utf-8')

# API endpoint to make STK push request
@app.route('/stk-push', methods=['POST'])
def stk_push():
    # Get access token
    access_token = get_access_token()

    # Get request data
    data = request.get_json()

    # Generate password
    timestamp = str(time.strftime("%Y%m%d%H%M%S"))
    password = generate_password("bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919", timestamp)

    # Create payload
    payload = {
        "BusinessShortCode": "174379",
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": data['amount'],
        "PartyA": data['phone_number'],
        "PartyB": "174379",
        "PhoneNumber": data['phone_number'],
        "CallBackURL": "https://mydomain.com/path",
        "AccountReference": "CompanyXLTD",
        "TransactionDesc": "Payment of X"
    }

    # Make STK push request
    response = make_stk_push_request(access_token, payload)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
