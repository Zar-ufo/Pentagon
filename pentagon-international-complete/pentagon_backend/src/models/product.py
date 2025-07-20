# This file defines what a "Product" looks like in our database
# Think of this as a form that describes each product we sell

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db  # Import our database connection

class Product(db.Model):
    """
    This class represents a product in our store
    Each product has information like name, size, prices, etc.
    """
    
    # This is like giving each product a unique ID number (like a barcode)
    id = db.Column(db.Integer, primary_key=True)
    
    # The name of the product (like "Kodomo Dental Kids Set (0.5-3)")
    item_name = db.Column(db.String(200), nullable=False)
    
    # The size or packaging info (like "1 Set")
    size = db.Column(db.String(50), nullable=True)
    
    # Trade Price - the basic price of the product
    trade_price = db.Column(db.Float, nullable=False, default=0.0)
    
    # Return Price for Market - price when returned from market
    return_price_market = db.Column(db.Float, nullable=False, default=0.0)
    
    # Return Price for Office - price when returned to office
    return_price_office = db.Column(db.Float, nullable=False, default=0.0)
    
    # Product category (like "Dental Care", "Baby Products", etc.)
    category = db.Column(db.String(100), nullable=True)
    
    # Product description - more details about the product
    description = db.Column(db.Text, nullable=True)
    
    # Is this product currently active/available for sale?
    is_active = db.Column(db.Boolean, default=True)
    
    # When was this product added to our system?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # When was this product last updated?
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """
        This function returns a simple text description of the product
        It's like a name tag for the product
        """
        return f'<Product {self.item_name}>'

    def to_dict(self):
        """
        This function converts the product information into a dictionary
        This makes it easy to send product info to our website or mobile app
        """
        return {
            'id': self.id,
            'item_name': self.item_name,
            'size': self.size,
            'trade_price': self.trade_price,
            'return_price_market': self.return_price_market,
            'return_price_office': self.return_price_office,
            'category': self.category,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def create_sample_products():
        """
        This function creates some example products for testing
        It's like filling our store with sample items so we can test everything works
        """
        sample_products = [
            {
                'item_name': 'Kodomo Dental Kids Set (0.5-3)',
                'size': '1 Set',
                'trade_price': 140.0,
                'return_price_market': 120.0,
                'return_price_office': 120.0,
                'category': 'Dental Care',
                'description': 'Dental care set for children aged 0.5 to 3 years'
            },
            {
                'item_name': 'Kodomo Dental Kids Set (3-6)',
                'size': '1 Set',
                'trade_price': 140.0,
                'return_price_market': 130.0,
                'return_price_office': 140.0,
                'category': 'Dental Care',
                'description': 'Dental care set for children aged 3 to 6 years'
            },
            {
                'item_name': 'Kodomo Dental Kids Set (6+)',
                'size': '1 Set',
                'trade_price': 140.0,
                'return_price_market': 140.0,
                'return_price_office': 140.0,
                'category': 'Dental Care',
                'description': 'Dental care set for children aged 6 years and above'
            }
        ]
        
        # Add each sample product to our database
        for product_data in sample_products:
            # Check if this product already exists
            existing_product = Product.query.filter_by(item_name=product_data['item_name']).first()
            if not existing_product:
                # Create a new product if it doesn't exist
                product = Product(**product_data)
                db.session.add(product)
        
        # Save all the new products to the database
        try:
            db.session.commit()
            print("✅ Sample products created successfully!")
        except Exception as e:
            print(f"❌ Error creating sample products: {e}")
            db.session.rollback()

