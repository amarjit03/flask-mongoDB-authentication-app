from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MongoDB Connection URI (Your local database and collection)
app.config["MONGO_URI"] = "mongodb://localhost:27017/flask_user_details"  # Change with your database name
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Home Route (Index Page)
@app.route('/')
def home():
    return render_template('index.html')

# Registration Route (Register a new user)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Check if username already exists
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
            flash('Username already exists, please choose another one.', 'error')
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Store the new user in the database
        mongo.db.users.insert_one({'username': username, 'password': hashed_password})
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login Route (Authenticate user with username and password)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find user in the database
        user = mongo.db.users.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Logout Route (Logout the user)
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
