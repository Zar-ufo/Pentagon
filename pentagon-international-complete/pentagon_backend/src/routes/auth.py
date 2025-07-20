# This file handles user authentication (login/logout) and security
# Think of this as the security guard that checks if users are allowed to enter

from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from src.models.user import User, db
from datetime import timedelta
from functools import wraps

# Create a blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# JWT configuration will be done in main.py

def token_required(f):
    """
    This is a decorator function that checks if a user is logged in
    It's like a bouncer at a club - only people with valid tickets can enter
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # This will automatically check if the user has a valid token
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request()
            
            # Get the user ID from the token
            current_user_id = get_jwt_identity()
            
            # Find the user in our database
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.is_active:
                return jsonify({
                    'success': False,
                    'message': 'User not found or account is inactive'
                }), 401
            
            # Pass the current user to the function
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    This function handles user login
    Users send their username/email and password, and we give them a token if correct
    
    Example: POST /api/login
    Body: {
        "username": "admin",
        "password": "admin123"
    }
    """
    try:
        # Get the login data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Get username/email and password
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({
                'success': False,
                'message': 'Username/email and password are required'
            }), 400
        
        # Find the user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid username/email or password'
            }), 401
        
        # Check if user account is active
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is inactive. Please contact administrator.'
            }), 401
        
        # Create a token that expires in 24 hours
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        # Update the user's last login time
        user.update_last_login()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'access_token': access_token,
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    This function handles user registration (creating new accounts)
    Only for creating new sales representatives (admin accounts should be created manually)
    
    Example: POST /api/register
    Body: {
        "username": "newsales",
        "email": "newsales@pentagon.com",
        "password": "password123",
        "full_name": "New Sales Person",
        "phone": "+880171234567"
    }
    """
    try:
        # Get the registration data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Check required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=data['username'].strip()).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=data['email'].strip()).first()
        if existing_email:
            return jsonify({
                'success': False,
                'message': 'Email already exists'
            }), 400
        
        # Create new user (always as sales role for security)
        user = User(
            username=data['username'].strip(),
            email=data['email'].strip(),
            full_name=data['full_name'].strip(),
            phone=data.get('phone', '').strip(),
            role='sales'  # New registrations are always sales users
        )
        
        # Set the password securely
        user.set_password(data['password'])
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    This function gets the current user's profile information
    
    Example: GET /api/profile
    Headers: Authorization: Bearer <token>
    """
    try:
        return jsonify({
            'success': True,
            'message': 'Profile retrieved successfully',
            'data': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving profile: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    This function allows users to update their own profile
    
    Example: PUT /api/profile
    Headers: Authorization: Bearer <token>
    Body: {
        "full_name": "Updated Name",
        "phone": "+880171234567"
    }
    """
    try:
        # Get the update data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Update allowed fields
        if 'full_name' in data and data['full_name'].strip():
            current_user.full_name = data['full_name'].strip()
        
        if 'phone' in data:
            current_user.phone = data['phone'].strip()
        
        if 'email' in data and data['email'].strip():
            # Check if email is already used by another user
            existing_email = User.query.filter(
                User.email == data['email'].strip(),
                User.id != current_user.id
            ).first()
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': 'Email already exists'
                }), 400
            current_user.email = data['email'].strip()
        
        # Update timestamp
        current_user.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating profile: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """
    This function allows users to change their password
    
    Example: POST /api/change-password
    Headers: Authorization: Bearer <token>
    Body: {
        "current_password": "oldpassword",
        "new_password": "newpassword"
    }
    """
    try:
        # Get the password data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Current password and new password are required'
            }), 400
        
        # Check if current password is correct
        if not current_user.check_password(current_password):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 400
        
        # Check if new password is strong enough (basic check)
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'New password must be at least 6 characters long'
            }), 400
        
        # Set the new password
        current_user.set_password(new_password)
        current_user.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error changing password: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    This function handles user logout
    In JWT, we can't really "logout" a token, but we can acknowledge the logout
    
    Example: POST /api/logout
    Headers: Authorization: Bearer <token>
    """
    try:
        # In a more advanced system, we would add this token to a blacklist
        # For now, we just acknowledge the logout
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout error: {str(e)}'
        }), 500

