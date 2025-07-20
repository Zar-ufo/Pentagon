# Pentagon International Web Application

A comprehensive web application for Pentagon International featuring separate Admin Panel and Sales Team interfaces with a robust backend API.

## 🏗️ Project Structure

This project consists of three main components:

```
pentagon-international/
├── pentagon_backend/          # Flask backend API
│   ├── src/
│   │   ├── main.py           # Main Flask application
│   │   ├── models/           # Database models
│   │   ├── routes/           # API endpoints
│   │   └── database/         # Database configuration
│   ├── requirements.txt      # Python dependencies
│   └── venv/                # Virtual environment
├── pentagon-admin/           # React Admin Panel
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── contexts/         # React contexts
│   │   └── App.jsx          # Main app component
│   └── package.json         # Node.js dependencies
└── pentagon-sales/           # React Sales Team Portal
    ├── src/
    │   ├── components/       # React components
    │   ├── contexts/         # React contexts
    │   └── App.jsx          # Main app component
    └── package.json         # Node.js dependencies
```

## 🚀 Features

### Admin Panel
- **Dashboard**: Overview of business metrics and analytics
- **Product Management**: Add, edit, and manage product catalog
- **Order Management**: View and manage all orders across the system
- **Inventory Tracking**: Monitor stock levels and inventory movements
- **User Management**: Manage admin and sales team accounts
- **Reports & Analytics**: Comprehensive business reporting

### Sales Team Portal
- **Sales Dashboard**: Personal performance metrics and quick actions
- **Order Creation**: Create new orders with customer and product selection
- **Customer Management**: Manage personal customer relationships
- **Product Catalog**: View products with pricing information
- **Sales Reports**: Personal sales performance and analytics

### Backend API
- **Authentication**: JWT-based secure authentication system
- **RESTful APIs**: Well-structured API endpoints for all operations
- **Database**: SQLite database with proper relationships
- **Security**: Password hashing, input validation, and CORS support
- **Documentation**: Clear API documentation with examples

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Security**: Werkzeug password hashing, Flask-CORS

### Frontend
- **Framework**: React.js with Vite
- **UI Library**: shadcn/ui components
- **Styling**: Tailwind CSS
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React icons
- **Routing**: React Router DOM

## 📋 Prerequisites

Before running this application, ensure you have the following installed:

- **Python 3.11+** - For the backend API
- **Node.js 18+** - For the frontend applications
- **npm or pnpm** - Package manager for Node.js

## 🔧 Installation & Setup

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd pentagon_backend

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python src/main.py
```

The backend will start on `http://localhost:5000`

### 2. Admin Panel Setup

```bash
# Navigate to the admin panel directory
cd pentagon-admin

# Install Node.js dependencies
npm install
# or if you prefer pnpm
pnpm install

# Start the development server
npm run dev
# or
pnpm run dev
```

The admin panel will start on `http://localhost:5174`

### 3. Sales Team Portal Setup

```bash
# Navigate to the sales portal directory
cd pentagon-sales

# Install Node.js dependencies
npm install
# or if you prefer pnpm
pnpm install

# Start the development server
npm run dev
# or
pnpm run dev
```

The sales portal will start on `http://localhost:5175`

## 🔐 Default Login Credentials

### Admin Panel
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator (full access)

### Sales Team Portal
- **Username**: `sales`
- **Password**: `sales123`
- **Role**: Sales Team Member

> ⚠️ **Important**: Change these default passwords in production!

## 🎯 Usage Guide

### For Administrators

1. **Login**: Access the admin panel at `http://localhost:5174`
2. **Dashboard**: View overall business metrics and system health
3. **Manage Products**: Add new products, update pricing, and manage inventory
4. **Monitor Orders**: Track all orders across the system
5. **User Management**: Create and manage user accounts for sales team
6. **Reports**: Generate and view comprehensive business reports

### For Sales Team

1. **Login**: Access the sales portal at `http://localhost:5175`
2. **Dashboard**: View personal sales metrics and quick actions
3. **Create Orders**: Process new customer orders with product selection
4. **Manage Customers**: Maintain customer relationships and contact information
5. **View Products**: Browse product catalog with current pricing
6. **Track Performance**: Monitor personal sales performance and targets

## 🔧 Configuration

### Backend Configuration

The backend uses environment variables for configuration. Key settings in `src/main.py`:

```python
# Database configuration
DATABASE_URL = 'sqlite:///src/database/app.db'

# JWT configuration
JWT_SECRET_KEY = 'your-secret-key-here'  # Change in production
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

# CORS configuration
CORS_ORIGINS = ['http://localhost:5174', 'http://localhost:5175']
```

### Frontend Configuration

Both frontend applications connect to the backend API. Update the API base URL in the auth contexts:

```javascript
// In src/contexts/AuthContext.jsx
const API_BASE_URL = 'http://localhost:5000/api'
```

## 📊 Database Schema

The application uses the following main database tables:

- **users**: User accounts (admin, sales team)
- **products**: Product catalog with pricing
- **orders**: Customer orders and order items
- **customers**: Customer information
- **inventory**: Stock tracking and movements

## 🔒 Security Features

- **Password Hashing**: All passwords are securely hashed using Werkzeug
- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configured to allow only specific origins
- **Input Validation**: Server-side validation for all API inputs
- **Role-based Access**: Different access levels for admin and sales users

## 🚀 Production Deployment

### Backend Deployment

1. **Environment Setup**:
   ```bash
   # Set production environment variables
   export FLASK_ENV=production
   export JWT_SECRET_KEY=your-secure-secret-key
   ```

2. **Database Migration**:
   ```bash
   # Initialize production database
   python src/main.py
   ```

3. **WSGI Server**:
   ```bash
   # Install production server
   pip install gunicorn
   
   # Run with gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

### Frontend Deployment

1. **Build for Production**:
   ```bash
   # Admin Panel
   cd pentagon-admin
   npm run build
   
   # Sales Portal
   cd pentagon-sales
   npm run build
   ```

2. **Serve Static Files**:
   - Deploy the `dist/` folders to your web server
   - Configure your web server to serve the React applications
   - Update API URLs to point to your production backend

## 🧪 Testing

### Backend Testing

```bash
# Test API endpoints
curl -X GET http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Frontend Testing

1. **Admin Panel**: Navigate to `http://localhost:5174` and test all features
2. **Sales Portal**: Navigate to `http://localhost:5175` and test all features
3. **Cross-browser Testing**: Test in Chrome, Firefox, Safari, and Edge

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**:
   - Check if Python 3.11+ is installed
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check if port 5000 is available

2. **Frontend won't start**:
   - Check if Node.js 18+ is installed
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check if ports 5174/5175 are available

3. **Login issues**:
   - Ensure backend is running on port 5000
   - Check browser console for CORS errors
   - Verify default credentials are correct

4. **Database issues**:
   - Delete `src/database/app.db` and restart backend to recreate
   - Check file permissions in the database directory

### Getting Help

If you encounter issues:

1. Check the browser console for JavaScript errors
2. Check the backend terminal for Python errors
3. Verify all services are running on correct ports
4. Ensure all dependencies are properly installed

## 📝 Development Notes

### Code Comments

All code files include comprehensive comments explaining:
- **What each function does** - Clear descriptions of functionality
- **How to use components** - Usage examples and parameters
- **Why certain decisions were made** - Architectural reasoning
- **Simple explanations** - Written so a 5-year-old could understand the logic

### Best Practices

- **Modular Architecture**: Clean separation of concerns
- **Error Handling**: Comprehensive error handling throughout
- **Security First**: Security considerations in every component
- **User Experience**: Intuitive interfaces with clear feedback
- **Performance**: Optimized for fast loading and smooth interactions

## 📄 License

This project is developed for Pentagon International. All rights reserved.

---

**Built with ❤️ for Pentagon International**

For technical support or questions, please contact the development team.

