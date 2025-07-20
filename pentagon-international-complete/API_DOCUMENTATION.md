# Pentagon International API Documentation

This document provides comprehensive documentation for the Pentagon International backend API.

## 🌐 Base URL

```
Development: http://localhost:5000/api
Production: https://api.pentagon.com/api
```

## 🔐 Authentication

The API uses JWT (JSON Web Token) based authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Token Expiration
- Access tokens expire after 24 hours
- Refresh tokens are not implemented (re-login required)

## 📋 API Endpoints

### Authentication Endpoints

#### POST /api/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string (required, 3-50 chars)",
  "password": "string (required, min 6 chars)",
  "email": "string (required, valid email)",
  "full_name": "string (required)",
  "role": "string (required: 'admin' or 'sales')",
  "phone": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@pentagon.com",
    "full_name": "John Doe",
    "role": "sales",
    "phone": "+1234567890",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000000",
    "updated_at": "2024-01-01T00:00:00.000000",
    "last_login": null
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Username already exists"
}
```

#### POST /api/login
Authenticate user and receive access token.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@pentagon.com",
      "full_name": "John Doe",
      "role": "sales",
      "phone": "+1234567890",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00.000000",
      "updated_at": "2024-01-01T00:00:00.000000",
      "last_login": "2024-01-01T12:00:00.000000"
    }
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

#### POST /api/logout
Logout user (invalidate token).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### GET /api/profile
Get current user profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@pentagon.com",
    "full_name": "John Doe",
    "role": "sales",
    "phone": "+1234567890",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000000",
    "updated_at": "2024-01-01T00:00:00.000000",
    "last_login": "2024-01-01T12:00:00.000000"
  }
}
```

#### PUT /api/profile
Update current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "full_name": "string (optional)",
  "email": "string (optional, valid email)",
  "phone": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@pentagon.com",
    "full_name": "John Doe Updated",
    "role": "sales",
    "phone": "+1234567890",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000000",
    "updated_at": "2024-01-01T12:30:00.000000",
    "last_login": "2024-01-01T12:00:00.000000"
  }
}
```

#### POST /api/change-password
Change user password.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_password": "string (required)",
  "new_password": "string (required, min 6 chars)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### Product Endpoints

#### GET /api/products
Get all products.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `category` (optional): Filter by category
- `active_only` (optional): true/false, default: false

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "item_name": "Premium Widget",
      "category": "Electronics",
      "size": "Medium",
      "description": "High-quality electronic widget",
      "trade_price": 100.00,
      "return_price_market": 150.00,
      "return_price_office": 180.00,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00.000000",
      "updated_at": "2024-01-01T00:00:00.000000"
    }
  ]
}
```

#### GET /api/products/{id}
Get specific product by ID.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "item_name": "Premium Widget",
    "category": "Electronics",
    "size": "Medium",
    "description": "High-quality electronic widget",
    "trade_price": 100.00,
    "return_price_market": 150.00,
    "return_price_office": 180.00,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000000",
    "updated_at": "2024-01-01T00:00:00.000000"
  }
}
```

#### POST /api/products
Create new product (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "item_name": "string (required)",
  "category": "string (required)",
  "size": "string (optional)",
  "description": "string (optional)",
  "trade_price": "number (required, > 0)",
  "return_price_market": "number (required, > 0)",
  "return_price_office": "number (required, > 0)",
  "is_active": "boolean (optional, default: true)"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Product created successfully",
  "data": {
    "id": 2,
    "item_name": "New Product",
    "category": "Electronics",
    "size": "Large",
    "description": "Brand new product",
    "trade_price": 200.00,
    "return_price_market": 300.00,
    "return_price_office": 350.00,
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000000",
    "updated_at": "2024-01-01T12:00:00.000000"
  }
}
```

#### PUT /api/products/{id}
Update existing product (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "item_name": "string (optional)",
  "category": "string (optional)",
  "size": "string (optional)",
  "description": "string (optional)",
  "trade_price": "number (optional, > 0)",
  "return_price_market": "number (optional, > 0)",
  "return_price_office": "number (optional, > 0)",
  "is_active": "boolean (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Product updated successfully",
  "data": {
    "id": 1,
    "item_name": "Updated Product Name",
    "category": "Electronics",
    "size": "Medium",
    "description": "Updated description",
    "trade_price": 120.00,
    "return_price_market": 180.00,
    "return_price_office": 210.00,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00.000000",
    "updated_at": "2024-01-01T12:30:00.000000"
  }
}
```

#### DELETE /api/products/{id}
Delete product (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

#### GET /api/products/categories
Get all product categories.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports"
  ]
}
```

### Order Endpoints

#### GET /api/orders
Get all orders (Admin) or user's orders (Sales).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional): Filter by status (pending, processing, delivered, cancelled)
- `customer_name` (optional): Filter by customer name
- `start_date` (optional): Filter orders from date (YYYY-MM-DD)
- `end_date` (optional): Filter orders to date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "customer_name": "John Customer",
      "customer_phone": "+1234567890",
      "customer_address": "123 Main St, City",
      "delivery_area": "Downtown",
      "total_value": 450.00,
      "status": "pending",
      "notes": "Urgent delivery required",
      "order_date": "2024-01-01T12:00:00.000000",
      "created_by": 1,
      "created_by_name": "Sales User",
      "items": [
        {
          "id": 1,
          "product_id": 1,
          "product_name": "Premium Widget",
          "quantity": 3,
          "unit_price": 150.00,
          "total_price": 450.00
        }
      ]
    }
  ]
}
```

#### GET /api/orders/{id}
Get specific order by ID.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "customer_name": "John Customer",
    "customer_phone": "+1234567890",
    "customer_address": "123 Main St, City",
    "delivery_area": "Downtown",
    "total_value": 450.00,
    "status": "pending",
    "notes": "Urgent delivery required",
    "order_date": "2024-01-01T12:00:00.000000",
    "created_by": 1,
    "created_by_name": "Sales User",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product": {
          "id": 1,
          "item_name": "Premium Widget",
          "category": "Electronics",
          "size": "Medium"
        },
        "quantity": 3,
        "unit_price": 150.00,
        "total_price": 450.00
      }
    ]
  }
}
```

#### POST /api/orders
Create new order.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "customer_name": "string (required)",
  "customer_phone": "string (optional)",
  "customer_address": "string (optional)",
  "delivery_area": "string (required)",
  "notes": "string (optional)",
  "items": [
    {
      "product_id": "number (required)",
      "quantity": "number (required, > 0)",
      "unit_price": "number (required, > 0)"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "id": 2,
    "customer_name": "Jane Customer",
    "customer_phone": "+0987654321",
    "customer_address": "456 Oak Ave, City",
    "delivery_area": "Uptown",
    "total_value": 300.00,
    "status": "pending",
    "notes": "Handle with care",
    "order_date": "2024-01-01T14:00:00.000000",
    "created_by": 1,
    "created_by_name": "Sales User",
    "items": [
      {
        "id": 2,
        "product_id": 2,
        "product_name": "Standard Widget",
        "quantity": 2,
        "unit_price": 150.00,
        "total_price": 300.00
      }
    ]
  }
}
```

#### PUT /api/orders/{id}/status
Update order status (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "status": "string (required: 'pending', 'processing', 'delivered', 'cancelled')"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Order status updated successfully",
  "data": {
    "id": 1,
    "status": "processing"
  }
}
```

#### GET /api/orders/my-orders
Get current user's orders (Sales team).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "customer_name": "John Customer",
      "delivery_area": "Downtown",
      "total_value": 450.00,
      "status": "pending",
      "order_date": "2024-01-01T12:00:00.000000"
    }
  ]
}
```

#### GET /api/orders/my-summary
Get current user's order summary (Sales team).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total": 25,
    "today": 3,
    "thisMonth": 15,
    "pending": 5
  }
}
```

### Customer Endpoints

#### GET /api/customers
Get all customers (Admin) or user's customers (Sales).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `search` (optional): Search by name, phone, or area

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "John Customer",
      "phone": "+1234567890",
      "email": "john@customer.com",
      "address": "123 Main St, City",
      "area": "Downtown",
      "notes": "VIP customer",
      "total_orders": 5,
      "total_spent": 2250.00,
      "last_order_date": "2024-01-01T12:00:00.000000",
      "created_by": 1,
      "created_at": "2023-12-01T00:00:00.000000",
      "updated_at": "2024-01-01T12:00:00.000000"
    }
  ]
}
```

#### GET /api/customers/{id}
Get specific customer by ID.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Customer",
    "phone": "+1234567890",
    "email": "john@customer.com",
    "address": "123 Main St, City",
    "area": "Downtown",
    "notes": "VIP customer",
    "total_orders": 5,
    "total_spent": 2250.00,
    "last_order_date": "2024-01-01T12:00:00.000000",
    "created_by": 1,
    "created_at": "2023-12-01T00:00:00.000000",
    "updated_at": "2024-01-01T12:00:00.000000"
  }
}
```

#### POST /api/customers
Create new customer.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "string (required)",
  "phone": "string (required)",
  "email": "string (optional, valid email)",
  "address": "string (optional)",
  "area": "string (optional)",
  "notes": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Customer created successfully",
  "data": {
    "id": 2,
    "name": "Jane Customer",
    "phone": "+0987654321",
    "email": "jane@customer.com",
    "address": "456 Oak Ave, City",
    "area": "Uptown",
    "notes": "Prefers morning delivery",
    "total_orders": 0,
    "total_spent": 0.00,
    "last_order_date": null,
    "created_by": 1,
    "created_at": "2024-01-01T14:00:00.000000",
    "updated_at": "2024-01-01T14:00:00.000000"
  }
}
```

#### PUT /api/customers/{id}
Update existing customer.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "string (optional)",
  "phone": "string (optional)",
  "email": "string (optional, valid email)",
  "address": "string (optional)",
  "area": "string (optional)",
  "notes": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Customer updated successfully",
  "data": {
    "id": 1,
    "name": "John Customer Updated",
    "phone": "+1234567890",
    "email": "john.updated@customer.com",
    "address": "123 Main St, City",
    "area": "Downtown",
    "notes": "VIP customer - updated",
    "total_orders": 5,
    "total_spent": 2250.00,
    "last_order_date": "2024-01-01T12:00:00.000000",
    "created_by": 1,
    "created_at": "2023-12-01T00:00:00.000000",
    "updated_at": "2024-01-01T14:30:00.000000"
  }
}
```

#### GET /api/customers/my-customers
Get current user's customers (Sales team).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "John Customer",
      "phone": "+1234567890",
      "area": "Downtown",
      "total_orders": 5,
      "total_spent": 2250.00,
      "last_order_date": "2024-01-01T12:00:00.000000"
    }
  ]
}
```

#### GET /api/customers/my-summary
Get current user's customer summary (Sales team).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total": 15,
    "active": 12
  }
}
```

### User Management Endpoints (Admin Only)

#### GET /api/users
Get all users (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `role` (optional): Filter by role (admin, sales)
- `active_only` (optional): true/false, default: false

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@pentagon.com",
      "full_name": "System Administrator",
      "role": "admin",
      "phone": "+1111111111",
      "is_active": true,
      "last_login": "2024-01-01T08:00:00.000000",
      "created_at": "2023-01-01T00:00:00.000000",
      "updated_at": "2024-01-01T08:00:00.000000"
    }
  ]
}
```

#### PUT /api/users/{id}
Update user (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "full_name": "string (optional)",
  "email": "string (optional, valid email)",
  "phone": "string (optional)",
  "role": "string (optional: 'admin' or 'sales')",
  "is_active": "boolean (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "id": 2,
    "username": "sales_user",
    "email": "sales.updated@pentagon.com",
    "full_name": "Sales User Updated",
    "role": "sales",
    "phone": "+2222222222",
    "is_active": true,
    "last_login": "2024-01-01T10:00:00.000000",
    "created_at": "2023-06-01T00:00:00.000000",
    "updated_at": "2024-01-01T14:45:00.000000"
  }
}
```

#### DELETE /api/users/{id}
Delete user (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

### Inventory Endpoints

#### GET /api/inventory
Get inventory levels for all products.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Premium Widget",
      "current_stock": 150,
      "minimum_stock": 20,
      "maximum_stock": 500,
      "last_updated": "2024-01-01T12:00:00.000000"
    }
  ]
}
```

#### PUT /api/inventory/{product_id}
Update inventory levels (Admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_stock": "number (required, >= 0)",
  "minimum_stock": "number (optional, >= 0)",
  "maximum_stock": "number (optional, >= 0)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Inventory updated successfully",
  "data": {
    "id": 1,
    "product_id": 1,
    "product_name": "Premium Widget",
    "current_stock": 200,
    "minimum_stock": 25,
    "maximum_stock": 600,
    "last_updated": "2024-01-01T15:00:00.000000"
  }
}
```

### Reports Endpoints

#### GET /api/reports/sales-summary
Get sales summary report.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `period` (optional): week, month, quarter, year (default: month)
- `user_id` (optional, Admin only): Get report for specific user

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "totalSales": 45000.00,
      "totalOrders": 28,
      "avgOrderValue": 1607.14,
      "targetProgress": 90.0,
      "target": 50000.00
    },
    "salesTrend": [
      {
        "name": "Week 1",
        "sales": 8000.00,
        "orders": 5
      }
    ],
    "topProducts": [
      {
        "name": "Premium Widget",
        "sales": 15000.00,
        "orders": 12
      }
    ]
  }
}
```

### Health Check Endpoint

#### GET /api/health
Check API health status.

**Response (200 OK):**
```json
{
  "success": true,
  "message": "API is healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "1.0.0"
}
```

## 🚨 Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE (optional)",
  "details": "Additional error details (optional)"
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### Error Examples

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Validation failed",
  "details": {
    "username": ["Username is required"],
    "email": ["Invalid email format"]
  }
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "message": "Token has expired"
}
```

**403 Forbidden:**
```json
{
  "success": false,
  "message": "Admin access required"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "message": "Product not found"
}
```

## 📝 Usage Examples

### JavaScript/Fetch Examples

#### Login and Store Token
```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/api/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const loginData = await loginResponse.json();
if (loginData.success) {
  // Store token for future requests
  localStorage.setItem('token', loginData.data.access_token);
}
```

#### Make Authenticated Request
```javascript
// Get products
const token = localStorage.getItem('token');
const productsResponse = await fetch('http://localhost:5000/api/products', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const productsData = await productsResponse.json();
if (productsData.success) {
  console.log('Products:', productsData.data);
}
```

#### Create New Order
```javascript
const token = localStorage.getItem('token');
const orderResponse = await fetch('http://localhost:5000/api/orders', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    customer_name: 'John Doe',
    customer_phone: '+1234567890',
    delivery_area: 'Downtown',
    items: [
      {
        product_id: 1,
        quantity: 2,
        unit_price: 150.00
      }
    ]
  })
});

const orderData = await orderResponse.json();
if (orderData.success) {
  console.log('Order created:', orderData.data);
}
```

### Python/Requests Examples

#### Login and Get Token
```python
import requests

# Login
login_response = requests.post('http://localhost:5000/api/login', json={
    'username': 'admin',
    'password': 'admin123'
})

login_data = login_response.json()
if login_data['success']:
    token = login_data['data']['access_token']
    print(f'Token: {token}')
```

#### Make Authenticated Request
```python
# Get products
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

products_response = requests.get('http://localhost:5000/api/products', headers=headers)
products_data = products_response.json()

if products_data['success']:
    print('Products:', products_data['data'])
```

### cURL Examples

#### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### Get Products
```bash
curl -X GET http://localhost:5000/api/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### Create Product
```bash
curl -X POST http://localhost:5000/api/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "New Product",
    "category": "Electronics",
    "trade_price": 100.00,
    "return_price_market": 150.00,
    "return_price_office": 180.00
  }'
```

## 🔧 Rate Limiting

The API implements basic rate limiting:
- **Authentication endpoints**: 5 requests per minute per IP
- **Other endpoints**: 100 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 📊 Pagination

For endpoints that return lists, pagination is supported:

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🔍 Filtering and Searching

Many endpoints support filtering and searching:

**Common Query Parameters:**
- `search`: General search term
- `sort_by`: Field to sort by
- `sort_order`: asc or desc
- `created_after`: Filter by creation date
- `created_before`: Filter by creation date

**Example:**
```
GET /api/products?search=widget&sort_by=created_at&sort_order=desc&page=1&per_page=10
```

## 📚 Additional Resources

- **Postman Collection**: Available for import with all endpoints pre-configured
- **OpenAPI/Swagger**: Interactive API documentation available at `/api/docs`
- **SDK**: JavaScript and Python SDKs available for easier integration

---

**Pentagon International API Documentation**
*Version 1.0 - Complete reference for developers*

