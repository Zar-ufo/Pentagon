# This file contains all the API routes for managing products
# Think of these as different doors that our website/app can knock on to get product information

from flask import Blueprint, request, jsonify
from src.models.product import Product
from src.models.user import db
from src.routes.auth import token_required
from datetime import datetime

# Create a blueprint - this is like a section of our API dedicated to products
product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
@token_required
def get_all_products(current_user):
    """
    This function gets a list of all products
    Anyone can see all products (both admin and sales)
    
    Example: GET /api/products
    """
    try:
        # Get all active products from the database
        products = Product.query.filter_by(is_active=True).all()
        
        # Convert each product to a dictionary so we can send it as JSON
        products_list = [product.to_dict() for product in products]
        
        return jsonify({
            'success': True,
            'message': 'Products retrieved successfully',
            'data': products_list,
            'count': len(products_list)
        }), 200
        
    except Exception as e:
        # If something goes wrong, tell the user what happened
        return jsonify({
            'success': False,
            'message': f'Error retrieving products: {str(e)}'
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
@token_required
def get_product(current_user, product_id):
    """
    This function gets information about one specific product
    
    Example: GET /api/products/1
    """
    try:
        # Find the product with the given ID
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Product retrieved successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving product: {str(e)}'
        }), 500

@product_bp.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    """
    This function creates a new product
    Only admin users can create products
    
    Example: POST /api/products
    Body: {
        "item_name": "New Product",
        "size": "1 Set",
        "trade_price": 150.0,
        "return_price_market": 130.0,
        "return_price_office": 130.0,
        "category": "Health Care",
        "description": "A new health care product"
    }
    """
    try:
        # Check if the user is an admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can create products'
            }), 403
        
        # Get the data sent by the user
        data = request.get_json()
        
        # Check if required fields are provided
        required_fields = ['item_name', 'trade_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if a product with this name already exists
        existing_product = Product.query.filter_by(item_name=data['item_name']).first()
        if existing_product:
            return jsonify({
                'success': False,
                'message': 'A product with this name already exists'
            }), 400
        
        # Create a new product
        product = Product(
            item_name=data['item_name'],
            size=data.get('size', ''),
            trade_price=float(data['trade_price']),
            return_price_market=float(data.get('return_price_market', 0.0)),
            return_price_office=float(data.get('return_price_office', 0.0)),
            category=data.get('category', ''),
            description=data.get('description', '')
        )
        
        # Save the product to the database
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'data': product.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': 'Invalid price format. Please provide valid numbers.'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating product: {str(e)}'
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    """
    This function updates an existing product
    Only admin users can update products
    
    Example: PUT /api/products/1
    Body: {
        "item_name": "Updated Product Name",
        "trade_price": 160.0
    }
    """
    try:
        # Check if the user is an admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can update products'
            }), 403
        
        # Find the product to update
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        # Get the data sent by the user
        data = request.get_json()
        
        # Update the product fields if they are provided
        if 'item_name' in data:
            # Check if another product already has this name
            existing_product = Product.query.filter(
                Product.item_name == data['item_name'],
                Product.id != product_id
            ).first()
            if existing_product:
                return jsonify({
                    'success': False,
                    'message': 'Another product with this name already exists'
                }), 400
            product.item_name = data['item_name']
        
        if 'size' in data:
            product.size = data['size']
        
        if 'trade_price' in data:
            product.trade_price = float(data['trade_price'])
        
        if 'return_price_market' in data:
            product.return_price_market = float(data['return_price_market'])
        
        if 'return_price_office' in data:
            product.return_price_office = float(data['return_price_office'])
        
        if 'category' in data:
            product.category = data['category']
        
        if 'description' in data:
            product.description = data['description']
        
        if 'is_active' in data:
            product.is_active = bool(data['is_active'])
        
        # Update the timestamp
        product.updated_at = datetime.utcnow()
        
        # Save the changes to the database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'data': product.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': 'Invalid price format. Please provide valid numbers.'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating product: {str(e)}'
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    """
    This function deletes a product (actually just marks it as inactive)
    Only admin users can delete products
    
    Example: DELETE /api/products/1
    """
    try:
        # Check if the user is an admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can delete products'
            }), 403
        
        # Find the product to delete
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        # Instead of actually deleting, we mark it as inactive
        # This is safer because we keep the history
        product.is_active = False
        product.updated_at = datetime.utcnow()
        
        # Save the changes to the database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting product: {str(e)}'
        }), 500

@product_bp.route('/products/search', methods=['GET'])
@token_required
def search_products(current_user):
    """
    This function searches for products by name or category
    
    Example: GET /api/products/search?q=dental&category=health
    """
    try:
        # Get search parameters from the URL
        search_query = request.args.get('q', '')  # Search term
        category = request.args.get('category', '')  # Category filter
        
        # Start with all active products
        query = Product.query.filter_by(is_active=True)
        
        # Add search filters if provided
        if search_query:
            # Search in product name (case-insensitive)
            query = query.filter(Product.item_name.ilike(f'%{search_query}%'))
        
        if category:
            # Filter by category (case-insensitive)
            query = query.filter(Product.category.ilike(f'%{category}%'))
        
        # Get the results
        products = query.all()
        
        # Convert to list of dictionaries
        products_list = [product.to_dict() for product in products]
        
        return jsonify({
            'success': True,
            'message': 'Search completed successfully',
            'data': products_list,
            'count': len(products_list),
            'search_query': search_query,
            'category_filter': category
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching products: {str(e)}'
        }), 500

@product_bp.route('/products/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    """
    This function gets a list of all product categories
    
    Example: GET /api/products/categories
    """
    try:
        # Get all unique categories from active products
        categories = db.session.query(Product.category)\
                              .filter(Product.is_active == True)\
                              .filter(Product.category != '')\
                              .filter(Product.category.isnot(None))\
                              .distinct().all()
        
        # Convert to a simple list
        category_list = [category[0] for category in categories]
        
        return jsonify({
            'success': True,
            'message': 'Categories retrieved successfully',
            'data': category_list,
            'count': len(category_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving categories: {str(e)}'
        }), 500

