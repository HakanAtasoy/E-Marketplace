from flask import session, redirect, url_for
import hashlib
from functools import wraps

# Define roles
ROLES = {
    'admin': 'Admin',
    'user': 'User'
}

# Hashing function
def hash_password(password):
    # Choose a secure hashing algorithm (e.g., SHA-256)
    hash_algorithm = hashlib.sha256()

    # Convert the password string to bytes before hashing
    password_bytes = password.encode('utf-8')

    # Update the hash object with the password bytes
    hash_algorithm.update(password_bytes)

    # Get the hashed password as a hexadecimal string
    hashed_password = hash_algorithm.hexdigest()

    return hashed_password

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def auth_signup(email, password, name, phone, db):
    # Check if the email is already registered
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        error_message = "Email already exists. Please choose a different email."
        return error_message

    users = db.users
    hashed_password = hash_password(password)  # Hash the password
    user_data = {
        'email': email,
        'password': hashed_password,  # Store the hashed password
        'name': name,
        'phone': phone,
        'role': 'user'
    }
    users.insert_one(user_data)
    return True

def auth_login(email, password, db):
    users = db.users
    hashed_password = hash_password(password)  # Hash the password for comparison
    user = users.find_one({'email': email, 'password': hashed_password})
    if user:
        # Convert ObjectId to string before storing in the session
        session['user_id'] = str(user['_id'])
        session['user_name'] = user.get('name')
        session['email'] = user.get('email')
        session['phone'] = user.get('phone')
        session['role'] = user.get('role', 'user')  # Set default role to 'user' if not provided
        return True
    else:
        return False


def auth_logout():
    session.clear()

def is_admin_user():
    # Determine if the user is an admin based on their role
    return session.get('role') == 'admin'


# Function to update user's account
def auth_update_user_account(email, new_email, new_password, new_name, new_phone, db):
    users = db.users
    result = users.update_one(
        {'email': email},
        {'$set': {'email': new_email, 'password': hash_password(new_password), 'name': new_name, 'phone': new_phone}}
    )
    return result.modified_count > 0


# Function to delete user account
def auth_delete_user(email, db):
    users = db.users

    # Check if the current user is an admin
    if session.get('role') == 'admin':
        result = users.delete_one({'email': email})
        return result.deleted_count > 0
    else:
        # Only admin users are allowed to delete users
        return False
