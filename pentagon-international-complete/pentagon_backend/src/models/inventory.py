# This file defines how we track inventory (stock) for each product
# Think of this as a digital warehouse that keeps track of how many items we have

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db  # Import our database connection

class Inventory(db.Model):
    """
    This class represents the inventory/stock information for each product
    It tracks how many items we have, how many we've sold, returns, etc.
    """
    
    # Unique ID for each inventory record
    id = db.Column(db.Integer, primary_key=True)
    
    # Which product this inventory record is for (connects to Product table)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Date for this inventory record (like a daily snapshot)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    # How many items we started the day with
    opening_pieces = db.Column(db.Integer, nullable=False, default=0)
    
    # How many items we sold/lifted during the day
    lifting_pieces = db.Column(db.Integer, nullable=False, default=0)
    
    # Total value of items sold/lifted
    lifting_price = db.Column(db.Float, nullable=False, default=0.0)
    
    # How many items were returned from the market
    return_market_pieces = db.Column(db.Integer, nullable=False, default=0)
    
    # Total value of market returns
    return_market_price = db.Column(db.Float, nullable=False, default=0.0)
    
    # How many items were returned to the office
    return_office_pieces = db.Column(db.Integer, nullable=False, default=0)
    
    # Total value of office returns
    return_office_price = db.Column(db.Float, nullable=False, default=0.0)
    
    # Total stock after all movements (calculated field)
    total_stock = db.Column(db.Integer, nullable=False, default=0)
    
    # IMS (Inventory Management System) pieces - for tracking purposes
    ims_pieces = db.Column(db.Integer, nullable=False, default=0)
    
    # IMS value - total value of IMS pieces
    ims_value = db.Column(db.Float, nullable=False, default=0.0)
    
    # Current stock at the end of the day
    present_stock = db.Column(db.Integer, nullable=False, default=0)
    
    # Total value of current stock
    closing_value = db.Column(db.Float, nullable=False, default=0.0)
    
    # When was this record created?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # When was this record last updated?
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """
        This function returns a simple text description of the inventory record
        """
        return f'<Inventory Product:{self.product_id} Date:{self.date}>'

    def to_dict(self):
        """
        This function converts the inventory information into a dictionary
        This makes it easy to send inventory info to our website or mobile app
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'date': self.date.isoformat() if self.date else None,
            'opening_pieces': self.opening_pieces,
            'lifting_pieces': self.lifting_pieces,
            'lifting_price': self.lifting_price,
            'return_market_pieces': self.return_market_pieces,
            'return_market_price': self.return_market_price,
            'return_office_pieces': self.return_office_pieces,
            'return_office_price': self.return_office_price,
            'total_stock': self.total_stock,
            'ims_pieces': self.ims_pieces,
            'ims_value': self.ims_value,
            'present_stock': self.present_stock,
            'closing_value': self.closing_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def calculate_totals(self):
        """
        This function automatically calculates the total stock and closing value
        It's like a calculator that does the math for us
        """
        # Calculate total stock: opening + returns - lifting
        self.total_stock = (self.opening_pieces + 
                           self.return_market_pieces + 
                           self.return_office_pieces - 
                           self.lifting_pieces)
        
        # Present stock is usually the same as total stock
        self.present_stock = self.total_stock
        
        # Calculate closing value (this would need product price information)
        # For now, we'll use a simple calculation
        # In a real system, this would multiply by the current product price
        self.closing_value = self.present_stock * 140.0  # Using average price for now

    @staticmethod
    def create_sample_inventory():
        """
        This function creates some example inventory records for testing
        It's like filling our warehouse with sample stock data
        """
        from src.models.product import Product
        from datetime import date, timedelta
        
        # Get all products
        products = Product.query.all()
        
        if not products:
            print("❌ No products found. Please create products first.")
            return
        
        # Create inventory for the last 3 days
        for i in range(3):
            inventory_date = date.today() - timedelta(days=i)
            
            for product in products:
                # Check if inventory already exists for this product and date
                existing_inventory = Inventory.query.filter_by(
                    product_id=product.id, 
                    date=inventory_date
                ).first()
                
                if not existing_inventory:
                    # Create sample inventory data
                    inventory = Inventory(
                        product_id=product.id,
                        date=inventory_date,
                        opening_pieces=20 + (i * 5),  # Different opening stock for each day
                        lifting_pieces=5 + i,        # Different sales for each day
                        lifting_price=(5 + i) * product.trade_price,
                        return_market_pieces=2 if i > 0 else 3,
                        return_market_price=(2 if i > 0 else 3) * product.return_price_market,
                        return_office_pieces=1 if i > 0 else 2,
                        return_office_price=(1 if i > 0 else 2) * product.return_price_office,
                        ims_pieces=15 + i,
                        ims_value=(15 + i) * product.trade_price
                    )
                    
                    # Calculate the totals automatically
                    inventory.calculate_totals()
                    
                    # Add to database
                    db.session.add(inventory)
        
        # Save all the new inventory records to the database
        try:
            db.session.commit()
            print("✅ Sample inventory created successfully!")
        except Exception as e:
            print(f"❌ Error creating sample inventory: {e}")
            db.session.rollback()

    @staticmethod
    def get_current_stock(product_id):
        """
        This function gets the current stock level for a specific product
        It's like checking how many items we have left in the warehouse
        """
        latest_inventory = Inventory.query.filter_by(product_id=product_id)\
                                        .order_by(Inventory.date.desc())\
                                        .first()
        
        if latest_inventory:
            return latest_inventory.present_stock
        else:
            return 0  # No inventory record found, so stock is 0

