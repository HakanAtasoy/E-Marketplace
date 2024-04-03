# app.py
import string
import random

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mail import Mail, Message
from auth import login_required, auth_signup, auth_login, auth_logout, auth_update_user_account, auth_delete_user, \
    hash_password
from pymongo import MongoClient
import pymongo
from models import Vehicle, Computer, Phone, PrivateLesson
from bson import ObjectId
from datetime import timedelta

app = Flask(__name__)


# Set a secret key for the Flask application
app.secret_key = 'my_verY_HighLevel_screet'

# Set the lifetime of the session to X minutes
app.permanent_session_lifetime = timedelta(minutes=20)

MONGO_URI = "mongodb+srv://LewsTherin:v1YIRAguI3Tr8z4A@cluster0.kce9iqe.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client["cengden"]

# Check if the database object is not None
if db is not None:
    print("Connected to the database successfully!")
else:
    print("Failed to connect to the database.")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        phone = request.form['phone']

        # Call auth_signup function from auth.py
        result = auth_signup(email, password, name, phone, db)
        if result is True:
            # Print signup successful message
            print("Signup successful")
            # Redirect to login page
            return redirect(url_for('login'))
        else:
            # Render signup template with error message
            return render_template('signup.html', error_message=result)

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Logic for user login
    if request.method == 'POST':
        # Handle form submission
        if auth_login(request.form['email'], request.form['password'], db):
            return redirect(url_for('home'))
        else:
            # Invalid credentials message
            error_message = "Invalid email or password. Please try again."
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    # Logic for user logout
    auth_logout()
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    # Render the profile page template
    return render_template('profile.html')

# Route for verifying user's email
@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        # Verify the provided verification code/token
        verification_code = request.form['verification_code']
        email = session.get('email')
        if verify_email(email, verification_code):
            # Verification successful, proceed with user signup
            auth_signup(email, request.form['password'], request.form['name'], request.form['phone'], db)
            # Clear session data after successful signup
            session.pop('verification_code')
            session.pop('email')
            return redirect(url_for('login'))
        else:
            # Verification failed, display error message
            error_message = "Invalid verification code. Please try again."
            return render_template('verify_email.html', error_message=error_message)
    return render_template('verify_email.html')


# Route for updating user's account
@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        email = session['email']  # Assuming the user email is stored in the session
        new_email = request.form['new_email']
        new_password = request.form['new_password']
        new_name = request.form['new_name']
        new_phone = request.form['new_phone']
        # Call update_user_account function from auth.py
        if email:
            if auth_update_user_account(email, new_email, new_password, new_name, new_phone, db):
                return redirect(url_for('profile'))
            else:
                return "Failed to update profile"
        else:
            return redirect(url_for('login_route'))  # Redirect to login if user not logged in

    return render_template('update_profile.html')


# Route for deleting user account
@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if request.method == 'POST':
        email = session.get('email')  # Assuming the user email is stored in the session
        if email:
            # Call delete_user function from auth.py
            if auth_delete_user(email, db):
                # User account successfully deleted
                session.clear()  # Clear session after deleting the user account
                return redirect(url_for('home'))
            else:
                # User account deletion failed
                return "Failed to delete user account", 500
        else:
            # Email not found in session
            return "User email not found in session", 400


def fetch_latest_items(offset, limit, owner_name=None, favorites_only=False, category=None):
    items_collection = db["items"]
    query = {}  # Default query to fetch latest items

    # If category is provided, add it to the query
    if category:
        query['category'] = category

    # If owner_name is provided and favorites_only is True, fetch favorite items of the owner
    if owner_name and favorites_only:
        favorites_collection = db["favorites"]
        favorite_items_cursor = favorites_collection.find({"owner": owner_name})
        favorite_item_ids = [favorite['item_id'] for favorite in favorite_items_cursor]
        query['_id'] = {'$in': favorite_item_ids}
    elif owner_name:
        query['owner'] = owner_name

    latest_items_cursor = items_collection.find(query).sort("date", pymongo.DESCENDING).skip(offset).limit(limit)
    latest_items = list(latest_items_cursor)

    # Count the total number of items in the database or belonging to the owner
    total_items_count = items_collection.count_documents(query)

    for item in latest_items:
        item['_id'] = str(item['_id'])

    return latest_items, total_items_count


def fetch_item_details(item_id):
    # Logic to fetch item details from the database based on item_id
    try:
        item = db["items"].find_one({"_id": ObjectId(item_id)})
        if item:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string for consistency
            return item
        else:
            return "Item not found", 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while fetching item details."


# Routes
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    items_per_page = 5  # Adjust as needed
    offset = (page - 1) * items_per_page
    latest_items, total_items_count = fetch_latest_items(offset, items_per_page)
    num_pages = (total_items_count + items_per_page - 1) // items_per_page
    return render_template('index.html', items=latest_items, page=page, num_pages=num_pages)


@app.route('/item/<item_id>')
def item_details(item_id):
    # Logic to fetch item details and render item details template
    item = fetch_item_details(item_id)

    # Check if the item is in the user's favorites
    user_id = session.get('user_id')
    liked = False
    if user_id:
        favorites = db["favorites"]
        if favorites.find_one({"user_id": user_id, "item_id": item_id}):
            liked = True

    # Check if the current user is the owner of the item
    is_owner = item.get('owner') == session.get('user_name')

    # Check if the current user is an admin
    is_admin = session.get('role') == 'admin'

    # Add email and phone to item if the user is authenticated
    if user_id:  # Authenticated user
        # Add email and phone from session to the item
        item['email'] = session.get('email')
        item['phone'] = session.get('phone')

    return render_template('item_details.html', item=item, liked=liked, is_owner=is_owner, is_admin=is_admin)



@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        print("we here")
        try:
            # Process form data and add a new item to the database
            category = request.form['category']
            # Extract additional attributes from form data
            additional_attributes = {}
            additional_keys = request.form.getlist('additional_attributes[key][]')
            additional_values = request.form.getlist('additional_attributes[value][]')

            # Filter out empty key-value pairs
            for key, value in zip(additional_keys, additional_values):
                if key and value:  # Check if both key and value are not empty
                    additional_attributes[key] = value

            if category == 'Vehicle':
                item = Vehicle(
                    title=request.form['title'],
                    owner=session['user_name'],
                    vehicle_type=request.form['type'],
                    brand=request.form['brand'],
                    model=request.form['model'],
                    year=request.form['year'],
                    color=request.form['color'],
                    engine_displacement=request.form['engine_displacement'],
                    fuel_type=request.form['fuel_type'],
                    transmission_type=request.form['transmission_type'],
                    mileage=request.form['mileage'],
                    price=request.form['price'],
                    image_url=request.form['image_url'],
                    description=request.form['description'],
                    active = True if request.form.get('active') == 'yes' else False,
                    additional_attributes=additional_attributes,
                    db=db
                )

            elif category == 'Computer':
                item = Computer(
                    title=request.form['title'],
                    owner=session['user_name'],
                    computer_type=request.form['type'],
                    brand=request.form['brand'],
                    model=request.form['model'],
                    year=request.form['year'],
                    processor=request.form['processor'],
                    ram=request.form['ram'],
                    ssd=request.form['ssd'],
                    hdd=request.form['hdd'],
                    graphics_card=request.form['graphics_card'],
                    operating_system=request.form['operating_system'],
                    price=request.form['price'],
                    image_url=request.form['image_url'],
                    description=request.form['description'],
                    active=True if request.form.get('active') == 'yes' else False,
                    additional_attributes=additional_attributes,
                    db=db
                )

            elif category == 'Phone':
                item = Phone(
                    title=request.form['title'],
                    owner=session['user_name'],
                    brand=request.form['brand'],
                    model=request.form['model'],
                    year=request.form['year'],
                    operating_system=request.form['operating_system'],
                    processor=request.form['processor'],
                    ram=request.form['ram'],
                    storage=request.form['storage'],
                    camera_specifications=request.form['camera_specifications'],
                    battery_capacity=request.form['battery_capacity'],
                    price=request.form['price'],
                    image_url=request.form['image_url'],
                    description=request.form['description'],
                    active=True if request.form.get('active') == 'yes' else False,
                    additional_attributes=additional_attributes,
                    db=db
                )

            elif category == 'Private Lesson':

                item = PrivateLesson(
                    title=request.form['title'],
                    owner=session['user_name'],
                    tutor_name=request.form['tutor_name'],
                    first_lesson=request.form['first_lesson'],
                    second_lesson=request.form['second_lesson'],
                    third_lesson=request.form['third_lesson'],
                    location=request.form['location'],
                    duration=request.form['duration'],
                    price=request.form['price'],
                    image_url=request.form['image_url'],
                    description=request.form['description'],
                    active=True if request.form.get('active') == 'yes' else False,
                    additional_attributes=additional_attributes,
                    db=db
                )

            print("Form data:", request.form)
            print(item)
            # Save the item
            print("checkpoint 1")
            item.save()
            print("checkpoint 2")
            return redirect('/')

        except Exception as e:
            # Handle any potential errors
            print(f"An error occurred: {e}")
            return "An error occurred while adding the item."

    else:
        return render_template('add_item.html')


@app.route('/items/update/<item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if request.method == 'POST':
        try:
            # Fetch the item from the database
            item = db["items"].find_one({"_id": ObjectId(item_id)})
            if item:
                # Update item attributes based on its category
                category = item['category']
                # Extract additional attributes from form data
                additional_attributes = {}
                additional_keys = request.form.getlist('additional_attributes[key][]')
                additional_values = request.form.getlist('additional_attributes[value][]')

                # Filter out empty key-value pairs
                for key, value in zip(additional_keys, additional_values):
                    if key and value:  # Check if both key and value are not empty
                        additional_attributes[key] = value

                if category == 'Vehicle':
                    item['title'] = request.form['title']
                    item['type'] = request.form['type']
                    item['brand'] = request.form['brand']
                    item['model'] = request.form['model']
                    item['year'] = request.form['year']
                    item['color'] = request.form['color']
                    item['price'] = request.form['price']
                    item['description'] = request.form['description']
                    item['image_url'] = request.form['image_url']
                    item['engine_displacement'] = request.form['engine_displacement']
                    item['fuel_type'] = request.form['fuel_type']
                    item['transmission_type'] = request.form['transmission_type']
                    item['mileage'] = request.form['mileage']
                    item['active'] = True if request.form.get('active') == 'yes' else False,
                    item['additional_attributes'] = additional_attributes

                elif category == 'Computer':

                    item['title'] = request.form['title']
                    item['type'] = request.form['type']
                    item['brand'] = request.form['brand']
                    item['model'] = request.form['model']
                    item['year'] = request.form['year']
                    item['processor'] = request.form['processor']
                    item['ram'] = request.form['ram']
                    storage = {}
                    if request.form['ssd']:
                        storage['SSD'] = request.form['ssd']
                    if request.form['hdd']:
                        storage['HDD'] = request.form['hdd']
                    item['storage'] = storage
                    item['graphics_card'] = request.form['graphics_card']
                    item['operating_system'] = request.form['operating_system']
                    item['price'] = request.form['price']
                    item['description'] = request.form['description']
                    item['image_url'] = request.form['image_url']
                    item['active'] = True if request.form.get('active') == 'yes' else False,
                    item['additional_attributes'] = additional_attributes

                elif category == 'Phone':

                    item['title'] = request.form['title']
                    item['brand'] = request.form['brand']
                    item['model'] = request.form['model']
                    item['year'] = request.form['year']
                    item['operating_system'] = request.form['operating_system']
                    item['processor'] = request.form['processor']
                    item['ram'] = request.form['ram']
                    item['storage'] = request.form['storage']
                    item['camera_specifications'] = request.form['camera_specifications']
                    item['battery_capacity'] = request.form['battery_capacity']
                    item['price'] = request.form['price']
                    item['description'] = request.form['description']
                    item['image_url'] = request.form['image_url']
                    item['active'] = True if request.form.get('active') == 'yes' else False,
                    item['additional_attributes'] = additional_attributes

                elif category == 'Private Lessons':

                    item['title'] = request.form['title']
                    item['tutor_name'] = request.form['tutor_name']
                    item['first_lesson'] = request.form['first_lesson']
                    item['second_lesson'] = request.form['second_lesson']
                    item['third_lesson'] = request.form['third_lesson']
                    item['location'] = request.form['location']
                    item['duration'] = request.form['duration']
                    item['price'] = request.form['price']
                    item['description'] = request.form['description']
                    item['image_url'] = request.form['image_url']
                    item['active'] = True if request.form.get('active') == 'yes' else False,
                    item['additional_attributes'] = additional_attributes

                # Save the updated item
                db["items"].update_one({"_id": ObjectId(item_id)}, {"$set": item})
                return redirect('/')

            else:
                return "Item not found", 404

        except Exception as e:
            # Handle any potential errors
            print(f"An error occurred: {e}")
            return "An error occurred while updating the item."

    else:
        # Fetch the item from the database and render the update form
        item = db["items"].find_one({"_id": ObjectId(item_id)})
        if item:
            return render_template('update_item.html', item=item)
        else:
            return "Item not found", 404


@app.route('/items/delete/<item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    try:
        # Delete the item from the database
        result = db["items"].delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count == 1:
            # Also delete the item from the favorites collection
            db["favorites"].delete_many({"item_id": item_id})
            return redirect('/')
        else:
            return "Item not found", 404

    except Exception as e:
        # Handle any potential errors
        print(f"An error occurred: {e}")
        return "An error occurred while deleting the item."


# Route for reactivating/deactivating items
@app.route('/activate_deactivate_item/<item_id>', methods=['POST'])
@login_required
def activate_deactivate_item(item_id):
    try:
        # Toggle the status of the item (active/inactive)
        item = db["items"].find_one({"_id": ObjectId(item_id)})
        if item:
            active_status = not item.get('active', False)
            result = db["items"].update_one({"_id": ObjectId(item_id)}, {"$set": {"active": active_status}})
            if result.modified_count == 1:
                return redirect('/my_items')
            else:
                return "Item not found", 404
        else:
            return "Item not found", 404
    except Exception as e:
        # Handle any potential errors
        print(f"An error occurred: {e}")
        return "An error occurred while activating/deactivating the item."


@app.route('/add_to_favorites/<item_id>', methods=['POST'])
@login_required
def add_to_favorites(item_id):
    try:
        user_id = session.get('user_id')
        if user_id:
            # Add the item to the user's favorites list
            favorites = db["favorites"]
            favorite_item = {"user_id": user_id, "item_id": item_id}
            favorites.insert_one(favorite_item)
            return redirect('/')
        else:
            return "User not logged in", 401
    except Exception as e:
        # Handle any potential errors
        print(f"An error occurred: {e}")
        return "An error occurred while adding item to favorites."

# Route for removing items from favorites
@app.route('/remove_from_favorites/<item_id>', methods=['POST'])
@login_required
def remove_from_favorites(item_id):
    try:
        user_id = session.get('user_id')
        if user_id:
            # Remove the item from the user's favorites list
            favorites = db["favorites"]
            favorites.delete_one({"user_id": user_id, "item_id": item_id})
            return redirect('/')
        else:
            return "User not logged in", 401
    except Exception as e:
        # Handle any potential errors
        print(f"An error occurred: {e}")
        return "An error occurred while removing item from favorites."


@app.route('/check_favorite/<item_id>', methods=['GET'])
@login_required
def check_favorite(item_id):
    try:
        user_id = session.get('user_id')
        if user_id:
            favorites = db["favorites"]
            # Check if the item is in the user's favorites
            favorite_item = favorites.find_one({"user_id": user_id, "item_id": item_id})
            if favorite_item:
                return jsonify({"inFavorites": True})
            else:
                return jsonify({"inFavorites": False})
        else:
            return jsonify({"error": "User not logged in"}), 401
    except Exception as e:
        # Handle any potential errors
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while checking item in favorites"}), 500


@app.route('/my_items')
@login_required
def my_items():
    owner_name = session.get('user_name')  # Assuming the owner's name is stored in session
    page = request.args.get('page', 1, type=int)
    items_per_page = 5  # Adjust as needed
    offset = (page - 1) * items_per_page
    user_items, total_user_items_count = fetch_latest_items(offset, items_per_page, owner_name)
    num_pages = (total_user_items_count + items_per_page - 1) // items_per_page
    return render_template('my_items.html', items=user_items, page=page, num_pages=num_pages)


# Route for the Favorites page
@app.route('/favorites')
@login_required
def favorites():
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    items_per_page = 5  # Adjust as needed
    offset = (page - 1) * items_per_page
    favorite_items, total_favorite_items_count = fetch_latest_items(offset, items_per_page, user_id, favorites_only=True)
    num_pages = (total_favorite_items_count + items_per_page - 1) // items_per_page
    return render_template('favorites.html', favorite_items=favorite_items, page=page, num_pages=num_pages)


@app.route('/items/category/<category>')
def items_by_category(category):
    page = request.args.get('page', 1, type=int)
    items_per_page = 5  # Adjust as needed
    offset = (page - 1) * items_per_page
    category_items, total_category_items_count = fetch_latest_items(offset, items_per_page, category=category)
    num_pages = (total_category_items_count + items_per_page - 1) // items_per_page
    return render_template('items_by_category.html', category_items=category_items, category=category, page=page, num_pages=num_pages)


if __name__ == '__main__':
    app.run(debug=True)
