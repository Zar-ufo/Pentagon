# This file contains all the API routes for managing inventory
# Think of these as different ways our website/app can check and update stock levels

from flask import Blueprint, request, jsonify
from src.models.inventory import Inventory
from src.models.product import Product
from src.models.user import db
from src.routes.auth import token_required
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_

# Create a blueprint for inventory routes
inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
@token_required
def get_inventory(current_user):
    """
    This function gets inventory information
    Shows current stock levels for all products
    
    Example: GET /api/inventory?date=2024-07-20
    """
    try:
        # Get date parameter (default to today)
        date_str = request.args.get('date')
        if date_str:
            try:
                inventory_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        else:
            inventory_date = date.today()
        
        # Get inventory records for the specified date
        inventory_records = db.session.query(Inventory, Product)\
            .join(Product, Inventory.product_id == Product.id)\
            .filter(Inventory.date == inventory_date)\
            .filter(Product.is_active == True)\
            .all()
        
        # If no records for the specific date, get the latest records for each product
        if not inventory_records:
            # Get the latest inventory record for each product
            subquery = db.session.query(
                Inventory.product_id,
                func.max(Inventory.date).label('latest_date')
            ).group_by(Inventory.product_id).subquery()
            
            inventory_records = db.session.query(Inventory, Product)\
                .join(Product, Inventory.product_id == Product.id)\
                .join(subquery, and_(
                    Inventory.product_id == subquery.c.product_id,
                    Inventory.date == subquery.c.latest_date
                ))\
                .filter(Product.is_active == True)\
                .all()
        
        # Convert to list of dictionaries
        inventory_list = []
        for inventory, product in inventory_records:
            inventory_dict = inventory.to_dict()
            inventory_dict['product'] = product.to_dict()
            inventory_list.append(inventory_dict)
        
        # If still no records, show products with zero inventory
        if not inventory_list:
            products = Product.query.filter_by(is_active=True).all()
            for product in products:
                inventory_dict = {
                    'id': None,
                    'product_id': product.id,
                    'date': inventory_date.isoformat(),
                    'opening_pieces': 0,
                    'lifting_pieces': 0,
                    'lifting_price': 0.0,
                    'return_market_pieces': 0,
                    'return_market_price': 0.0,
                    'return_office_pieces': 0,
                    'return_office_price': 0.0,
                    'total_stock': 0,
                    'ims_pieces': 0,
                    'ims_value': 0.0,
                    'present_stock': 0,
                    'closing_value': 0.0,
                    'product': product.to_dict()
                }
                inventory_list.append(inventory_dict)
        
        return jsonify({
            'success': True,
            'message': 'Inventory retrieved successfully',
            'data': inventory_list,
            'count': len(inventory_list),
            'date': inventory_date.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving inventory: {str(e)}'
        }), 500

@inventory_bp.route('/inventory/product/<int:product_id>', methods=['GET'])
@token_required
def get_product_inventory(current_user, product_id):
    """
    This function gets inventory history for a specific product
    
    Example: GET /api/inventory/product/1?days=7
    """
    try:
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        # Get number of days to look back (default 7)
        days = request.args.get('days', 7, type=int)
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Get inventory records for this product in the date range
        inventory_records = Inventory.query\
            .filter_by(product_id=product_id)\
            .filter(Inventory.date >= start_date)\
            .filter(Inventory.date <= end_date)\
            .order_by(Inventory.date.desc())\
            .all()
        
        # Convert to list of dictionaries
        inventory_list = [record.to_dict() for record in inventory_records]
        
        # Get current stock level
        current_stock = Inventory.get_current_stock(product_id)
        
        return jsonify({
            'success': True,
            'message': 'Product inventory retrieved successfully',
            'data': {
                'product': product.to_dict(),
                'current_stock': current_stock,
                'inventory_history': inventory_list,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving product inventory: {str(e)}'
        }), 500

@inventory_bp.route('/inventory', methods=['POST'])
@token_required
def create_inventory_record(current_user):
    """
    This function creates a new inventory record
    Only admin users can create inventory records
    
    Example: POST /api/inventory
    Body: {
        "product_id": 1,
        "date": "2024-07-20",
        "opening_pieces": 20,
        "lifting_pieces": 5,
        "lifting_price": 700.0,
        "return_market_pieces": 2,
        "return_market_price": 240.0,
        "return_office_pieces": 1,
        "return_office_price": 120.0
    }
    """
    try:
        # Check if user is admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can create inventory records'
            }), 403
        
        # Get the data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Check required fields
        required_fields = ['product_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if product exists
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        # Parse date
        inventory_date = date.today()
        if 'date' in data:
            try:
                inventory_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # Check if inventory record already exists for this product and date
        existing_record = Inventory.query.filter_by(
            product_id=data['product_id'],
            date=inventory_date
        ).first()
        
        if existing_record:
            return jsonify({
                'success': False,
                'message': f'Inventory record already exists for this product on {inventory_date}'
            }), 400
        
        # Create new inventory record
        inventory = Inventory(
            product_id=data['product_id'],
            date=inventory_date,
            opening_pieces=data.get('opening_pieces', 0),
            lifting_pieces=data.get('lifting_pieces', 0),
            lifting_price=data.get('lifting_price', 0.0),
            return_market_pieces=data.get('return_market_pieces', 0),
            return_market_price=data.get('return_market_price', 0.0),
            return_office_pieces=data.get('return_office_pieces', 0),
            return_office_price=data.get('return_office_price', 0.0),
            ims_pieces=data.get('ims_pieces', 0),
            ims_value=data.get('ims_value', 0.0)
        )
        
        # Calculate totals
        inventory.calculate_totals()
        
        # Save to database
        db.session.add(inventory)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Inventory record created successfully',
            'data': inventory.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating inventory record: {str(e)}'
        }), 500

@inventory_bp.route('/inventory/<int:inventory_id>', methods=['PUT'])
@token_required
def update_inventory_record(current_user, inventory_id):
    """
    This function updates an existing inventory record
    Only admin users can update inventory records
    
    Example: PUT /api/inventory/1
    Body: {
        "lifting_pieces": 7,
        "lifting_price": 980.0
    }
    """
    try:
        # Check if user is admin
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only admin users can update inventory records'
            }), 403
        
        # Find the inventory record
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return jsonify({
                'success': False,
                'message': 'Inventory record not found'
            }), 404
        
        # Get the data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Update fields if provided
        if 'opening_pieces' in data:
            inventory.opening_pieces = int(data['opening_pieces'])
        
        if 'lifting_pieces' in data:
            inventory.lifting_pieces = int(data['lifting_pieces'])
        
        if 'lifting_price' in data:
            inventory.lifting_price = float(data['lifting_price'])
        
        if 'return_market_pieces' in data:
            inventory.return_market_pieces = int(data['return_market_pieces'])
        
        if 'return_market_price' in data:
            inventory.return_market_price = float(data['return_market_price'])
        
        if 'return_office_pieces' in data:
            inventory.return_office_pieces = int(data['return_office_pieces'])
        
        if 'return_office_price' in data:
            inventory.return_office_price = float(data['return_office_price'])
        
        if 'ims_pieces' in data:
            inventory.ims_pieces = int(data['ims_pieces'])
        
        if 'ims_value' in data:
            inventory.ims_value = float(data['ims_value'])
        
        # Recalculate totals
        inventory.calculate_totals()
        
        # Update timestamp
        inventory.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Inventory record updated successfully',
            'data': inventory.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': 'Invalid number format in request data'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating inventory record: {str(e)}'
        }), 500

@inventory_bp.route('/inventory/stock-levels', methods=['GET'])
@token_required
def get_stock_levels(current_user):
    """
    This function gets current stock levels for all products
    Similar to the "Products all Summary" Excel sheet
    
    Example: GET /api/inventory/stock-levels
    """
    try:
        # Get all active products
        products = Product.query.filter_by(is_active=True).all()
        
        stock_levels = []
        total_value = 0
        
        for product in products:
            # Get current stock for this product
            current_stock = Inventory.get_current_stock(product.id)
            
            # Calculate current value
            current_value = current_stock * product.trade_price
            total_value += current_value
            
            stock_info = {
                'product_id': product.id,
                'item_name': product.item_name,
                'size': product.size,
                'category': product.category,
                'trade_price': product.trade_price,
                'current_stock': current_stock,
                'current_value': current_value,
                'stock_status': 'low' if current_stock < 10 else 'normal'  # Simple low stock indicator
            }
            
            stock_levels.append(stock_info)
        
        # Sort by stock level (lowest first) to highlight low stock items
        stock_levels.sort(key=lambda x: x['current_stock'])
        
        return jsonify({
            'success': True,
            'message': 'Stock levels retrieved successfully',
            'data': {
                'products': stock_levels,
                'summary': {
                    'total_products': len(stock_levels),
                    'total_inventory_value': total_value,
                    'low_stock_items': len([item for item in stock_levels if item['stock_status'] == 'low'])
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving stock levels: {str(e)}'
        }), 500

@inventory_bp.route('/inventory/low-stock', methods=['GET'])
@token_required
def get_low_stock_items(current_user):
    """
    This function gets products with low stock levels
    Helps identify items that need restocking
    
    Example: GET /api/inventory/low-stock?threshold=10
    """
    try:
        # Get threshold parameter (default 10)
        threshold = request.args.get('threshold', 10, type=int)
        
        # Get all active products
        products = Product.query.filter_by(is_active=True).all()
        
        low_stock_items = []
        
        for product in products:
            # Get current stock for this product
            current_stock = Inventory.get_current_stock(product.id)
            
            # Check if stock is below threshold
            if current_stock <= threshold:
                stock_info = {
                    'product_id': product.id,
                    'item_name': product.item_name,
                    'size': product.size,
                    'category': product.category,
                    'current_stock': current_stock,
                    'threshold': threshold,
                    'urgency': 'critical' if current_stock == 0 else 'low'
                }
                
                low_stock_items.append(stock_info)
        
        # Sort by stock level (lowest first)
        low_stock_items.sort(key=lambda x: x['current_stock'])
        
        return jsonify({
            'success': True,
            'message': 'Low stock items retrieved successfully',
            'data': {
                'low_stock_items': low_stock_items,
                'threshold': threshold,
                'count': len(low_stock_items),
                'critical_items': len([item for item in low_stock_items if item['urgency'] == 'critical'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving low stock items: {str(e)}'
        }), 500

