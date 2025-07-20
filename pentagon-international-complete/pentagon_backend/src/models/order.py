# This file defines how we handle orders in our system
# Think of this as a digital order form that tracks what customers want to buy

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db  # Import our database connection

class Order(db.Model):
    """
    This class represents a customer order
    Each order contains information about what was ordered, by whom, and when
    """
    
    # Unique ID for each order (like an order number)
    id = db.Column(db.Integer, primary_key=True)
    
    # Which sales person created this order (connects to User table)
    sales_person_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Customer information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=True)
    customer_address = db.Column(db.Text, nullable=True)
    
    # Delivery area (like "lalbag", "Dhanmondi", "Newmarket")
    delivery_area = db.Column(db.String(100), nullable=False)
    
    # Order status: 'pending', 'processing', 'delivered', 'cancelled', 'due'
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # Total value of the order
    total_value = db.Column(db.Float, nullable=False, default=0.0)
    
    # When was this order created?
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # When was this order delivered (if delivered)?
    delivery_date = db.Column(db.DateTime, nullable=True)
    
    # Any special notes about the order
    notes = db.Column(db.Text, nullable=True)
    
    # When was this order record created in our system?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # When was this order last updated?
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """
        This function returns a simple text description of the order
        """
        return f'<Order {self.id} - {self.customer_name}>'

    def to_dict(self):
        """
        This function converts the order information into a dictionary
        This makes it easy to send order info to our website or mobile app
        """
        return {
            'id': self.id,
            'sales_person_id': self.sales_person_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_address': self.customer_address,
            'delivery_area': self.delivery_area,
            'status': self.status,
            'total_value': self.total_value,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderItem(db.Model):
    """
    This class represents individual items within an order
    Each order can have multiple items (like 5 toothbrushes + 3 toothpastes)
    """
    
    # Unique ID for each order item
    id = db.Column(db.Integer, primary_key=True)
    
    # Which order this item belongs to (connects to Order table)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    
    # Which product this item is (connects to Product table)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # How many of this product were ordered
    quantity = db.Column(db.Integer, nullable=False)
    
    # Price per unit at the time of order (prices might change over time)
    unit_price = db.Column(db.Float, nullable=False)
    
    # Total price for this item (quantity × unit_price)
    total_price = db.Column(db.Float, nullable=False)
    
    # When was this order item created?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """
        This function returns a simple text description of the order item
        """
        return f'<OrderItem Order:{self.order_id} Product:{self.product_id}>'

    def to_dict(self):
        """
        This function converts the order item information into a dictionary
        """
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def calculate_total_price(self):
        """
        This function calculates the total price for this order item
        It's like a calculator that multiplies quantity by price
        """
        self.total_price = self.quantity * self.unit_price

# Helper functions for creating sample data and managing orders

def create_sample_orders():
    """
    This function creates some example orders for testing
    It's like filling our system with sample orders so we can test everything works
    """
    from src.models.user import User
    from src.models.product import Product
    from datetime import date, timedelta
    
    # Get a sales person (user with role 'sales')
    sales_person = User.query.filter_by(role='sales').first()
    if not sales_person:
        print("❌ No sales person found. Please create a sales user first.")
        return
    
    # Get some products
    products = Product.query.limit(3).all()
    if not products:
        print("❌ No products found. Please create products first.")
        return
    
    # Sample order data
    sample_orders = [
        {
            'customer_name': 'Ahmed Rahman',
            'customer_phone': '+880171234567',
            'customer_address': 'House 123, Road 5, Dhanmondi, Dhaka',
            'delivery_area': 'Dhanmondi',
            'status': 'delivered',
            'order_date': datetime.now() - timedelta(days=2)
        },
        {
            'customer_name': 'Fatima Khatun',
            'customer_phone': '+880181234567',
            'customer_address': 'Flat 4B, Building 7, Lalmatia, Dhaka',
            'delivery_area': 'lalbag',
            'status': 'pending',
            'order_date': datetime.now() - timedelta(days=1)
        },
        {
            'customer_name': 'Mohammad Ali',
            'customer_phone': '+880191234567',
            'customer_address': 'Shop 15, New Market, Dhaka',
            'delivery_area': 'Newmarket',
            'status': 'processing',
            'order_date': datetime.now()
        }
    ]
    
    # Create each sample order
    for order_data in sample_orders:
        # Check if this order already exists (by customer name and date)
        existing_order = Order.query.filter_by(
            customer_name=order_data['customer_name'],
            order_date=order_data['order_date']
        ).first()
        
        if not existing_order:
            # Create a new order
            order = Order(
                sales_person_id=sales_person.id,
                **order_data
            )
            
            # Add the order to the database first so we get an ID
            db.session.add(order)
            db.session.flush()  # This gives us the order ID without committing
            
            # Add some items to this order
            total_value = 0
            for i, product in enumerate(products[:2]):  # Add 2 products per order
                quantity = 2 + i  # Different quantities for variety
                unit_price = product.trade_price
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price
                )
                order_item.calculate_total_price()
                
                total_value += order_item.total_price
                db.session.add(order_item)
            
            # Update the order's total value
            order.total_value = total_value
    
    # Save all the new orders to the database
    try:
        db.session.commit()
        print("✅ Sample orders created successfully!")
    except Exception as e:
        print(f"❌ Error creating sample orders: {e}")
        db.session.rollback()

def get_order_summary():
    """
    This function provides a summary of all orders
    It's like a report that shows how many orders we have in each status
    """
    from sqlalchemy import func
    
    # Count orders by status
    status_counts = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()
    
    # Calculate total order value
    total_value = db.session.query(func.sum(Order.total_value)).scalar() or 0
    
    # Count total orders
    total_orders = Order.query.count()
    
    return {
        'total_orders': total_orders,
        'total_value': total_value,
        'status_breakdown': {status: count for status, count in status_counts}
    }

