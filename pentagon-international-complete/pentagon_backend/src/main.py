# This is the main file that starts our Pentagon International web application
# Think of this as the "brain" of our application that controls everything

import os
import sys
# DON'T CHANGE THIS !!! - This helps Python find our files
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Flask and other tools we need
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS  # This allows our website to talk to our app from different addresses
from flask_jwt_extended import JWTManager  # This handles user login tokens

# Import our database and all our models
from src.models.user import db, User
from src.models.product import Product
from src.models.order import Order, OrderItem, create_sample_orders
from src.models.inventory import Inventory

# Import all our API routes (these handle different types of requests)
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.product import product_bp
from src.routes.order import order_bp
from src.routes.inventory import inventory_bp

# Create our Flask application - like building the foundation of a house
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Enable CORS - this allows our frontend (website) to talk to our backend (this app)
# It's like opening the doors so different parts of our system can communicate
CORS(app, origins="*")

# Set up JWT (JSON Web Tokens) for user authentication
# This is like a digital ID card system for users
app.config['JWT_SECRET_KEY'] = 'pentagon-international-jwt-secret-2024'  # Change this in production!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire (for development)

# Initialize JWT
jwt = JWTManager(app)

# Set a secret key - this is like a password that keeps our app secure
app.config['SECRET_KEY'] = 'pentagon-international-secret-key-2024'

# Register our blueprints - these are like different sections of our API
# Each blueprint handles different types of requests (users, products, orders, etc.)
app.register_blueprint(auth_bp, url_prefix='/api')      # Login, logout, register
app.register_blueprint(user_bp, url_prefix='/api')      # User management
app.register_blueprint(product_bp, url_prefix='/api')   # Product management
app.register_blueprint(order_bp, url_prefix='/api')     # Order management
app.register_blueprint(inventory_bp, url_prefix='/api') # Inventory management

# Set up our database - this is where we store all our information
# We're using SQLite which is like a simple filing cabinet for our data
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with our app
db.init_app(app)

# Create all database tables and sample data when the app starts
with app.app_context():
    # Create all tables
    db.create_all()
    print("📊 Database tables created successfully!")
    
    # Create sample data if it doesn't exist
    print("🔧 Setting up sample data...")
    
    # Create sample users
    User.create_sample_users()
    
    # Create sample products
    Product.create_sample_products()
    
    # Create sample inventory
    Inventory.create_sample_inventory()
    
    # Create sample orders
    create_sample_orders()
    
    print("✅ Sample data setup complete!")

# API endpoint to check if the server is running
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    This endpoint checks if our API is working properly
    It's like asking "Are you there?" and getting "Yes, I'm here!"
    """
    return jsonify({
        'success': True,
        'message': 'Pentagon International API is running successfully!',
        'version': '1.0.0',
        'status': 'healthy'
    }), 200

# API endpoint to get basic information about the API
@app.route('/api', methods=['GET'])
def api_info():
    """
    This endpoint provides information about our API
    It's like a welcome message that explains what our API can do
    """
    return jsonify({
        'success': True,
        'message': 'Welcome to Pentagon International API',
        'version': '1.0.0',
        'description': 'API for managing sales, inventory, and orders for Pentagon International',
        'endpoints': {
            'authentication': '/api/login, /api/register, /api/profile',
            'users': '/api/users',
            'products': '/api/products',
            'orders': '/api/orders',
            'inventory': '/api/inventory'
        },
        'documentation': 'Visit /api/health to check API status'
    }), 200

# Handle JWT errors gracefully
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """
    This function handles when a user's login token expires
    """
    return jsonify({
        'success': False,
        'message': 'Your login session has expired. Please log in again.'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """
    This function handles when a user provides an invalid login token
    """
    return jsonify({
        'success': False,
        'message': 'Invalid login token. Please log in again.'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    """
    This function handles when a user tries to access protected content without logging in
    """
    return jsonify({
        'success': False,
        'message': 'Login required. Please provide a valid access token.'
    }), 401

# This route serves our website files (HTML, CSS, JavaScript)
# It's like a waiter that brings the right page to visitors
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
    This function serves static files (like HTML, CSS, JS) to users
    If someone visits our website, this gives them the right page
    """
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({
            'success': False,
            'message': 'Frontend not configured. Please build and deploy the frontend first.'
        }), 404

    # If a specific file is requested and exists, serve it
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Otherwise, serve the main index.html file (our main website page)
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'success': False,
                'message': 'Frontend not found. Please build and deploy the frontend first.',
                'api_info': 'API is available at /api'
            }), 404

# This is where our app starts running
# It's like turning on the lights and opening the doors of our digital store
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Pentagon International Application...")
    print("="*60)
    print("📊 Admin Panel will be available at: http://localhost:5000")
    print("💼 Sales Team interface will be available at: http://localhost:5000/sales")
    print("🔧 API documentation available at: http://localhost:5000/api")
    print("❤️  Health check available at: http://localhost:5000/api/health")
    print("="*60)
    print("📝 Default Login Credentials:")
    print("   👑 Admin: username='admin', password='admin123'")
    print("   💼 Sales: username='sales1', password='sales123'")
    print("   💼 Sales: username='sales2', password='sales123'")
    print("   👑 Manager: username='manager', password='manager123'")
    print("="*60)
    print("🔒 Security Note: Change default passwords in production!")
    print("="*60 + "\n")
    
    # Start the application
    # host='0.0.0.0' means anyone can access it (not just this computer)
    # port=5000 means it runs on port 5000
    # debug=True means it will show helpful error messages and restart when we make changes
    app.run(host='0.0.0.0', port=5000, debug=True)

