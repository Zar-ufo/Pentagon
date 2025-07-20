# This file defines what a "User" looks like in our database
# Think of this as a digital ID card for everyone who uses our system

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create our database connection
# This is like creating a filing cabinet where we store all our information
db = SQLAlchemy()

class User(db.Model):
    """
    This class represents a user in our system
    Users can be either Admin (managers) or Sales (sales representatives)
    """
    
    # This is like giving each user a unique ID number
    id = db.Column(db.Integer, primary_key=True)
    
    # Username - what the user types to log in (must be unique)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    # Email address - also used for login and communication
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Password - stored securely (encrypted)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Full name of the user
    full_name = db.Column(db.String(200), nullable=False)
    
    # Phone number for contact
    phone = db.Column(db.String(20), nullable=True)
    
    # User role: 'admin' or 'sales'
    # Admin can see everything, Sales can only see their own data
    role = db.Column(db.String(20), nullable=False, default='sales')
    
    # Is this user account active? (can they log in?)
    is_active = db.Column(db.Boolean, default=True)
    
    # When was this user account created?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # When was this user account last updated?
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # When did this user last log in?
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """
        This function returns a simple text description of the user
        It's like a name tag for the user
        """
        return f'<User {self.username} ({self.role})>'

    def set_password(self, password):
        """
        This function safely stores a user's password
        It encrypts the password so no one can see the actual password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        This function checks if a password is correct
        It compares the encrypted stored password with what the user typed
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """
        This function converts the user information into a dictionary
        This makes it easy to send user info to our website or mobile app
        Note: We never send the password, even encrypted!
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def is_admin(self):
        """
        This function checks if the user is an administrator
        Admins have special permissions to see and do everything
        """
        return self.role == 'admin'

    def is_sales(self):
        """
        This function checks if the user is a sales representative
        Sales users can only see their own orders and limited data
        """
        return self.role == 'sales'

    def update_last_login(self):
        """
        This function records when the user last logged in
        It's like a timestamp showing when they visited our system
        """
        self.last_login = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def create_sample_users():
        """
        This function creates some example users for testing
        It's like adding sample employees to our system so we can test everything works
        """
        sample_users = [
            {
                'username': 'admin',
                'email': 'admin@pentagon.com',
                'full_name': 'System Administrator',
                'phone': '+880171111111',
                'role': 'admin',
                'password': 'admin123'  # In real life, this should be much stronger!
            },
            {
                'username': 'sales1',
                'email': 'sales1@pentagon.com',
                'full_name': 'Ahmed Hassan',
                'phone': '+880172222222',
                'role': 'sales',
                'password': 'sales123'
            },
            {
                'username': 'sales2',
                'email': 'sales2@pentagon.com',
                'full_name': 'Fatima Rahman',
                'phone': '+880173333333',
                'role': 'sales',
                'password': 'sales123'
            },
            {
                'username': 'manager',
                'email': 'manager@pentagon.com',
                'full_name': 'Mohammad Ali',
                'phone': '+880174444444',
                'role': 'admin',
                'password': 'manager123'
            }
        ]
        
        # Add each sample user to our database
        for user_data in sample_users:
            # Check if this user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                # Create a new user if they don't exist
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    phone=user_data['phone'],
                    role=user_data['role']
                )
                # Set their password securely
                user.set_password(user_data['password'])
                db.session.add(user)
        
        # Save all the new users to the database
        try:
            db.session.commit()
            print("✅ Sample users created successfully!")
            print("📝 Login credentials:")
            print("   Admin: username='admin', password='admin123'")
            print("   Sales: username='sales1', password='sales123'")
            print("   Sales: username='sales2', password='sales123'")
            print("   Manager: username='manager', password='manager123'")
        except Exception as e:
            print(f"❌ Error creating sample users: {e}")
            db.session.rollback()

