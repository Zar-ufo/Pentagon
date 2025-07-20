# This file contains all the API routes for managing users
# Think of these as different ways our website/app can manage user accounts

from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.routes.auth import token_required
from datetime import datetime

# Create a blueprint for user management routes
user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """
    This function gets a list of all users
    Only admin users can see all users
    
    Example: GET /api/users
    """
    try:
        # Check if user is admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can view all users'
            }), 403
        
        # Get all users
        users = User.query.all()
        
        # Convert to list of dictionaries (without passwords)
        users_list = [user.to_dict() for user in users]
        
        return jsonify({
            'success': True,
            'message': 'Users retrieved successfully',
            'data': users_list,
            'count': len(users_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving users: {str(e)}'
        }), 500

@user_bp.route('/users', methods=['POST'])
@token_required
def create_user(current_user):
    """
    This function creates a new user account
    Only admin users can create new accounts
    
    Example: POST /api/users
    Body: {
        "username": "newuser",
        "email": "newuser@pentagon.com",
        "password": "password123",
        "full_name": "New User",
        "phone": "+880171234567",
        "role": "sales"
    }
    """
    try:
        # Check if user is admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can create new accounts'
            }), 403
        
        # Get the data from request
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
        
        # Validate role
        role = data.get('role', 'sales').lower()
        if role not in ['admin', 'sales']:
            return jsonify({
                'success': False,
                'message': 'Role must be either "admin" or "sales"'
            }), 400
        
        # Create new user
        user = User(
            username=data['username'].strip(),
            email=data['email'].strip(),
            full_name=data['full_name'].strip(),
            phone=data.get('phone', '').strip(),
            role=role
        )
        
        # Set password securely
        user.set_password(data['password'])
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating user: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """
    This function gets information about a specific user
    Admin can see any user, Sales can only see their own profile
    
    Example: GET /api/users/1
    """
    try:
        # Find the user
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check permissions
        if not current_user.is_admin() and current_user.id != user_id:
            return jsonify({
                'success': False,
                'message': 'You can only view your own profile'
            }), 403
        
        return jsonify({
            'success': True,
            'message': 'User retrieved successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving user: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """
    This function updates a user's information
    Admin can update any user, Sales can only update their own profile
    
    Example: PUT /api/users/1
    Body: {
        "full_name": "Updated Name",
        "phone": "+880171234567",
        "is_active": true
    }
    """
    try:
        # Find the user to update
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check permissions
        if not current_user.is_admin() and current_user.id != user_id:
            return jsonify({
                'success': False,
                'message': 'You can only update your own profile'
            }), 403
        
        # Get the data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Update allowed fields
        if 'full_name' in data and data['full_name'].strip():
            user.full_name = data['full_name'].strip()
        
        if 'phone' in data:
            user.phone = data['phone'].strip()
        
        if 'email' in data and data['email'].strip():
            # Check if email is already used by another user
            existing_email = User.query.filter(
                User.email == data['email'].strip(),
                User.id != user_id
            ).first()
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': 'Email already exists'
                }), 400
            user.email = data['email'].strip()
        
        # Only admin can update these fields
        if current_user.is_admin():
            if 'role' in data:
                role = data['role'].lower()
                if role in ['admin', 'sales']:
                    user.role = role
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Role must be either "admin" or "sales"'
                    }), 400
            
            if 'is_active' in data:
                user.is_active = bool(data['is_active'])
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating user: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """
    This function deletes a user account (actually deactivates it)
    Only admin users can delete accounts
    
    Example: DELETE /api/users/1
    """
    try:
        # Check if user is admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can delete accounts'
            }), 403
        
        # Find the user to delete
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Don't allow admin to delete themselves
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'You cannot delete your own account'
            }), 400
        
        # Instead of actually deleting, we deactivate the account
        # This is safer because we keep the history
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User account deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting user: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@token_required
def reset_user_password(current_user, user_id):
    """
    This function resets a user's password
    Only admin users can reset passwords
    
    Example: POST /api/users/1/reset-password
    Body: {
        "new_password": "newpassword123"
    }
    """
    try:
        # Check if user is admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can reset passwords'
            }), 403
        
        # Find the user
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get the new password
        data = request.get_json()
        
        if not data or 'new_password' not in data:
            return jsonify({
                'success': False,
                'message': 'New password is required'
            }), 400
        
        new_password = data['new_password']
        
        # Check password strength (basic check)
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        # Set the new password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Password reset successfully for user {user.username}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error resetting password: {str(e)}'
        }), 500

@user_bp.route('/users/sales', methods=['GET'])
@token_required
def get_sales_users(current_user):
    """
    This function gets a list of all sales users
    Useful for assigning orders or viewing sales team
    
    Example: GET /api/users/sales
    """
    try:
        # Get all active sales users
        sales_users = User.query.filter_by(role='sales', is_active=True).all()
        
        # Convert to list of dictionaries
        sales_list = [user.to_dict() for user in sales_users]
        
        return jsonify({
            'success': True,
            'message': 'Sales users retrieved successfully',
            'data': sales_list,
            'count': len(sales_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving sales users: {str(e)}'
        }), 500

@user_bp.route('/users/stats', methods=['GET'])
@token_required
def get_user_stats(current_user):
    """
    This function provides statistics about users
    Only admin users can see user statistics
    
    Example: GET /api/users/stats
    """
    try:
        # Check if user is admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can view user statistics'
            }), 403
        
        # Count users by role
        total_users = User.query.count()
        admin_users = User.query.filter_by(role='admin').count()
        sales_users = User.query.filter_by(role='sales').count()
        active_users = User.query.filter_by(is_active=True).count()
        inactive_users = User.query.filter_by(is_active=False).count()
        
        # Get recent registrations (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        return jsonify({
            'success': True,
            'message': 'User statistics retrieved successfully',
            'data': {
                'total_users': total_users,
                'admin_users': admin_users,
                'sales_users': sales_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'recent_registrations': recent_registrations
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving user statistics: {str(e)}'
        }), 500

