# This file contains all the API routes for managing orders
# Think of these as different ways our website/app can create, view, and update orders

from flask import Blueprint, request, jsonify
from src.models.order import Order, OrderItem, get_order_summary
from src.models.product import Product
from src.models.inventory import Inventory
from src.models.user import db
from src.routes.auth import token_required
from datetime import datetime, date
from sqlalchemy import func, and_

# Create a blueprint for order routes
order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    """
    This function gets a list of orders
    Admin can see all orders, Sales can only see their own orders
    
    Example: GET /api/orders?status=pending&limit=10
    """
    try:
        # Get query parameters
        status = request.args.get('status')  # Filter by status
        limit = request.args.get('limit', type=int)  # Limit number of results
        page = request.args.get('page', 1, type=int)  # Page number for pagination
        
        # Start building the query
        query = Order.query
        
        # If user is sales, only show their orders
        if current_user.is_sales():
            query = query.filter_by(sales_person_id=current_user.id)
        
        # Apply status filter if provided
        if status:
            query = query.filter_by(status=status)
        
        # Order by most recent first
        query = query.order_by(Order.created_at.desc())
        
        # Apply pagination
        if limit:
            orders = query.limit(limit).all()
        else:
            # Use pagination for better performance
            per_page = 20  # 20 orders per page
            orders_pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            orders = orders_pagination.items
        
        # Convert orders to dictionaries and include order items
        orders_list = []
        for order in orders:
            order_dict = order.to_dict()
            
            # Get order items for this order
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            order_dict['items'] = []
            
            for item in order_items:
                item_dict = item.to_dict()
                # Also include product information
                product = Product.query.get(item.product_id)
                if product:
                    item_dict['product'] = product.to_dict()
                order_dict['items'].append(item_dict)
            
            orders_list.append(order_dict)
        
        return jsonify({
            'success': True,
            'message': 'Orders retrieved successfully',
            'data': orders_list,
            'count': len(orders_list),
            'filters': {
                'status': status,
                'page': page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving orders: {str(e)}'
        }), 500

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    """
    This function gets details of a specific order
    
    Example: GET /api/orders/1
    """
    try:
        # Find the order
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        # Check if user has permission to view this order
        if current_user.is_sales() and order.sales_person_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You can only view your own orders'
            }), 403
        
        # Get order details
        order_dict = order.to_dict()
        
        # Get order items
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        order_dict['items'] = []
        
        for item in order_items:
            item_dict = item.to_dict()
            # Include product information
            product = Product.query.get(item.product_id)
            if product:
                item_dict['product'] = product.to_dict()
            order_dict['items'].append(item_dict)
        
        # Include sales person information
        from src.models.user import User
        sales_person = User.query.get(order.sales_person_id)
        if sales_person:
            order_dict['sales_person'] = {
                'id': sales_person.id,
                'username': sales_person.username,
                'full_name': sales_person.full_name
            }
        
        return jsonify({
            'success': True,
            'message': 'Order retrieved successfully',
            'data': order_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving order: {str(e)}'
        }), 500

@order_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    """
    This function creates a new order
    
    Example: POST /api/orders
    Body: {
        "customer_name": "John Doe",
        "customer_phone": "+880171234567",
        "customer_address": "123 Main St, Dhaka",
        "delivery_area": "Dhanmondi",
        "notes": "Deliver in the morning",
        "items": [
            {
                "product_id": 1,
                "quantity": 2
            },
            {
                "product_id": 2,
                "quantity": 1
            }
        ]
    }
    """
    try:
        # Get the order data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Check required fields
        required_fields = ['customer_name', 'delivery_area', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate items
        if not data['items'] or len(data['items']) == 0:
            return jsonify({
                'success': False,
                'message': 'Order must contain at least one item'
            }), 400
        
        # Create the order
        order = Order(
            sales_person_id=current_user.id,
            customer_name=data['customer_name'],
            customer_phone=data.get('customer_phone', ''),
            customer_address=data.get('customer_address', ''),
            delivery_area=data['delivery_area'],
            notes=data.get('notes', ''),
            status='pending'
        )
        
        # Add order to database to get an ID
        db.session.add(order)
        db.session.flush()  # This gives us the order ID without committing
        
        # Process order items
        total_value = 0
        order_items = []
        
        for item_data in data['items']:
            # Validate item data
            if 'product_id' not in item_data or 'quantity' not in item_data:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': 'Each item must have product_id and quantity'
                }), 400
            
            # Get the product
            product = Product.query.get(item_data['product_id'])
            if not product or not product.is_active:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Product with ID {item_data["product_id"]} not found or inactive'
                }), 400
            
            # Check stock availability
            current_stock = Inventory.get_current_stock(product.id)
            if current_stock < item_data['quantity']:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Insufficient stock for {product.item_name}. Available: {current_stock}, Requested: {item_data["quantity"]}'
                }), 400
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data['quantity'],
                unit_price=product.trade_price
            )
            order_item.calculate_total_price()
            
            total_value += order_item.total_price
            order_items.append(order_item)
            db.session.add(order_item)
        
        # Update order total value
        order.total_value = total_value
        
        # Commit all changes
        db.session.commit()
        
        # Return the created order with items
        order_dict = order.to_dict()
        order_dict['items'] = [item.to_dict() for item in order_items]
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'data': order_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating order: {str(e)}'
        }), 500

@order_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@token_required
def update_order_status(current_user, order_id):
    """
    This function updates the status of an order
    Admin can update any order, Sales can only update their own orders
    
    Example: PUT /api/orders/1/status
    Body: {
        "status": "delivered"
    }
    """
    try:
        # Find the order
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        # Check permissions
        if current_user.is_sales() and order.sales_person_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You can only update your own orders'
            }), 403
        
        # Get the new status
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        new_status = data['status']
        
        # Validate status
        valid_statuses = ['pending', 'processing', 'delivered', 'cancelled', 'due']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
            }), 400
        
        # Update the status
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # If status is delivered, set delivery date
        if new_status == 'delivered' and old_status != 'delivered':
            order.delivery_date = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Order status updated from {old_status} to {new_status}',
            'data': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating order status: {str(e)}'
        }), 500

@order_bp.route('/orders/summary', methods=['GET'])
@token_required
def get_orders_summary(current_user):
    """
    This function provides a summary of orders
    Admin sees all orders, Sales sees only their orders
    
    Example: GET /api/orders/summary
    """
    try:
        # Base query
        query = Order.query
        
        # If user is sales, filter to their orders only
        if current_user.is_sales():
            query = query.filter_by(sales_person_id=current_user.id)
        
        # Get status counts
        status_counts = db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        )
        
        if current_user.is_sales():
            status_counts = status_counts.filter_by(sales_person_id=current_user.id)
        
        status_counts = status_counts.group_by(Order.status).all()
        
        # Get total order value
        total_value_query = db.session.query(func.sum(Order.total_value))
        if current_user.is_sales():
            total_value_query = total_value_query.filter_by(sales_person_id=current_user.id)
        
        total_value = total_value_query.scalar() or 0
        
        # Get total order count
        total_orders = query.count()
        
        # Get today's orders
        today = date.today()
        today_orders = query.filter(
            func.date(Order.order_date) == today
        ).count()
        
        # Get this month's orders
        this_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_orders = query.filter(
            Order.order_date >= this_month
        ).count()
        
        return jsonify({
            'success': True,
            'message': 'Order summary retrieved successfully',
            'data': {
                'total_orders': total_orders,
                'total_value': total_value,
                'today_orders': today_orders,
                'month_orders': month_orders,
                'status_breakdown': {status: count for status, count in status_counts}
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving order summary: {str(e)}'
        }), 500

@order_bp.route('/orders/daily-summary', methods=['GET'])
@token_required
def get_daily_summary(current_user):
    """
    This function provides a daily summary similar to the "all things Summary" Excel sheet
    
    Example: GET /api/orders/daily-summary?date=2024-07-20
    """
    try:
        # Get date parameter (default to today)
        date_str = request.args.get('date')
        if date_str:
            try:
                summary_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        else:
            summary_date = date.today()
        
        # Base query for the specific date
        date_filter = func.date(Order.order_date) == summary_date
        
        # If user is sales, filter to their orders only
        if current_user.is_sales():
            base_query = Order.query.filter(
                and_(date_filter, Order.sales_person_id == current_user.id)
            )
        else:
            base_query = Order.query.filter(date_filter)
        
        # Calculate metrics
        total_orders = base_query.count()
        
        # Total sales value (delivered orders)
        sales_value = base_query.filter_by(status='delivered').with_entities(
            func.sum(Order.total_value)
        ).scalar() or 0
        
        # Count by status
        pending_orders = base_query.filter_by(status='pending').count()
        delivered_orders = base_query.filter_by(status='delivered').count()
        cancelled_orders = base_query.filter_by(status='cancelled').count()
        due_orders = base_query.filter_by(status='due').count()
        
        # Get delivery areas for this date
        delivery_areas = base_query.with_entities(Order.delivery_area).distinct().all()
        delivery_areas_list = [area[0] for area in delivery_areas]
        
        return jsonify({
            'success': True,
            'message': 'Daily summary retrieved successfully',
            'data': {
                'date': summary_date.isoformat(),
                'total_orders': total_orders,
                'sales_value': sales_value,
                'pending_orders': pending_orders,
                'delivered_orders': delivered_orders,
                'cancelled_orders': cancelled_orders,
                'due_orders': due_orders,
                'delivery_areas': delivery_areas_list
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving daily summary: {str(e)}'
        }), 500

