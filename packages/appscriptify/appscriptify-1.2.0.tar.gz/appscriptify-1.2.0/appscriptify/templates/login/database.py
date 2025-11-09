import pymongo
from dotenv import load_dotenv
import os
import json
import hashlib
import secrets
import base64
import hmac
import datetime
import threading
import secrets
import uuid
import time
from bson import ObjectId

load_dotenv()

with open('config.json') as file:
    config = json.load(file)

if not config.get('users_database') or not config.get('users_collection'):
    print("Please set up your MongoDB configuration in config.json and .env files.")

USERS_DB = config['users_database']
USERS_COLLECTION = config['users_collection']
uri = os.environ['MONGO_URI']
client = pymongo.MongoClient(uri)
db = client[USERS_DB]
users = db[USERS_COLLECTION]

def write_data(data, collection=users):
    result = collection.insert_one(data)
    print("Inserted ID:", result.inserted_id)
    print('Data Updated')

def read_data(query):
    document = users.find_one(query)
    return document

def save_user(username, password, email, ip):
    # If already exist with same Email
    existing_user = read_data({'email': email})
    if existing_user:
        return {'ok':0, 'msg':'Email already registered'}
    id = secrets.token_hex(16)
    # Hash and salt the password together
    salt = secrets.token_bytes(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    pwd_storage = base64.b64encode(salt + pwd_hash).decode('utf-8')
    user_data = {
        'username': username,
        'password': pwd_storage,
        'email': email,
        'ip': ip,
        'id': id
    }
    write_data(user_data)
    return {'ok':1, 'id': id}

def get_user(email, password):
    # Input validation
    if not email or not password:
        return {'ok': 0, 'msg': 'Email/username and password are required'}

    try:
        # Fetch user by email or username
        user = read_data({
            '$or': [
                {'email': email},
                {'username': email}  # Allow login with username too
            ]
        })
        if not user:
            return {'ok': 0, 'msg': 'User not found'}
        
        # Verify password
        stored_data = base64.b64decode(user['password'])
        salt = stored_data[:16]
        stored_hash = stored_data[16:]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        if hmac.compare_digest(stored_hash, pwd_hash):
            return {'ok': 1, 'user': user}
        return {'ok': 0, 'msg': 'Invalid password'}
    except Exception as e:
        print(f"Error in get_user: {str(e)}")
        return {'ok': 0, 'msg': 'An error occurred during login'}