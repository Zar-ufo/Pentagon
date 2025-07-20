# Pentagon International - Production Deployment Guide

This guide provides step-by-step instructions for deploying the Pentagon International web application to a production environment.

## 🎯 Overview

The Pentagon International application consists of three components that need to be deployed:

1. **Backend API** (Flask) - Handles data and authentication
2. **Admin Panel** (React) - Administrative interface
3. **Sales Portal** (React) - Sales team interface

## 🏗️ Architecture Options

### Option 1: Single Server Deployment
- All components on one server
- Suitable for small to medium businesses
- Easier to manage and maintain

### Option 2: Microservices Deployment
- Backend on application server
- Frontend on CDN/static hosting
- Database on separate server
- Better scalability and performance

## 🔧 Prerequisites

### Server Requirements

**Minimum Specifications:**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+

**Recommended Specifications:**
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS

### Software Requirements

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx (web server)
sudo apt install nginx -y

# Install PM2 (process manager)
sudo npm install -g pm2

# Install SSL certificate tool
sudo apt install certbot python3-certbot-nginx -y
```

## 🚀 Backend Deployment

### 1. Prepare the Backend

```bash
# Create application directory
sudo mkdir -p /var/www/pentagon-backend
sudo chown $USER:$USER /var/www/pentagon-backend

# Copy backend files
cp -r pentagon_backend/* /var/www/pentagon-backend/

# Navigate to backend directory
cd /var/www/pentagon-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production server
pip install gunicorn
```

### 2. Configure Environment Variables

```bash
# Create environment file
sudo nano /var/www/pentagon-backend/.env
```

Add the following content:

```env
# Production Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security
JWT_SECRET_KEY=your-super-secure-secret-key-here-change-this
SECRET_KEY=another-secure-secret-key-for-flask

# Database
DATABASE_URL=sqlite:///var/www/pentagon-backend/src/database/app.db

# CORS Origins (update with your domain)
CORS_ORIGINS=https://admin.pentagon.com,https://sales.pentagon.com

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### 3. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/pentagon-backend.service
```

Add the following content:

```ini
[Unit]
Description=Pentagon International Backend API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/pentagon-backend
Environment=PATH=/var/www/pentagon-backend/venv/bin
EnvironmentFile=/var/www/pentagon-backend/.env
ExecStart=/var/www/pentagon-backend/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 --access-logfile /var/log/pentagon-backend-access.log --error-logfile /var/log/pentagon-backend-error.log src.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Start Backend Service

```bash
# Set proper permissions
sudo chown -R www-data:www-data /var/www/pentagon-backend
sudo chmod -R 755 /var/www/pentagon-backend

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable pentagon-backend
sudo systemctl start pentagon-backend

# Check status
sudo systemctl status pentagon-backend
```

## 🌐 Frontend Deployment

### 1. Build Frontend Applications

```bash
# Build Admin Panel
cd pentagon-admin
npm install
npm run build

# Build Sales Portal
cd ../pentagon-sales
npm install
npm run build
```

### 2. Deploy to Web Server

```bash
# Create web directories
sudo mkdir -p /var/www/pentagon-admin
sudo mkdir -p /var/www/pentagon-sales

# Copy built files
sudo cp -r pentagon-admin/dist/* /var/www/pentagon-admin/
sudo cp -r pentagon-sales/dist/* /var/www/pentagon-sales/

# Set permissions
sudo chown -R www-data:www-data /var/www/pentagon-admin
sudo chown -R www-data:www-data /var/www/pentagon-sales
sudo chmod -R 755 /var/www/pentagon-admin
sudo chmod -R 755 /var/www/pentagon-sales
```

## 🔧 Nginx Configuration

### 1. Create Nginx Configuration

```bash
# Remove default configuration
sudo rm /etc/nginx/sites-enabled/default

# Create admin panel configuration
sudo nano /etc/nginx/sites-available/pentagon-admin
```

Add the following content:

```nginx
server {
    listen 80;
    server_name admin.pentagon.com;  # Replace with your domain
    
    root /var/www/pentagon-admin;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Create sales portal configuration
sudo nano /etc/nginx/sites-available/pentagon-sales
```

Add similar content for sales portal:

```nginx
server {
    listen 80;
    server_name sales.pentagon.com;  # Replace with your domain
    
    root /var/www/pentagon-sales;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Enable Sites and Restart Nginx

```bash
# Enable sites
sudo ln -s /etc/nginx/sites-available/pentagon-admin /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/pentagon-sales /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔒 SSL Certificate Setup

### 1. Install SSL Certificates

```bash
# Install certificates for both domains
sudo certbot --nginx -d admin.pentagon.com -d sales.pentagon.com

# Set up automatic renewal
sudo crontab -e
```

Add the following line to crontab:

```bash
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🗄️ Database Setup

### 1. Initialize Production Database

```bash
# Navigate to backend directory
cd /var/www/pentagon-backend

# Activate virtual environment
source venv/bin/activate

# Initialize database
python src/main.py

# Create admin user
python -c "
from src.models.user import User
from src.database.config import db
from werkzeug.security import generate_password_hash

# Create admin user
admin = User(
    username='admin',
    password_hash=generate_password_hash('your-secure-admin-password'),
    email='admin@pentagon.com',
    full_name='System Administrator',
    role='admin'
)

db.session.add(admin)
db.session.commit()
print('Admin user created successfully')
"
```

### 2. Database Backup Script

```bash
# Create backup script
sudo nano /usr/local/bin/backup-pentagon-db.sh
```

Add the following content:

```bash
#!/bin/bash

# Pentagon International Database Backup Script
BACKUP_DIR="/var/backups/pentagon"
DB_PATH="/var/www/pentagon-backend/src/database/app.db"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
cp $DB_PATH $BACKUP_DIR/pentagon_db_$DATE.db

# Keep only last 30 days of backups
find $BACKUP_DIR -name "pentagon_db_*.db" -mtime +30 -delete

echo "Database backup completed: pentagon_db_$DATE.db"
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/backup-pentagon-db.sh

# Add to crontab for daily backups
sudo crontab -e
```

Add the following line:

```bash
0 2 * * * /usr/local/bin/backup-pentagon-db.sh
```

## 📊 Monitoring and Logging

### 1. Log Configuration

```bash
# Create log directories
sudo mkdir -p /var/log/pentagon
sudo chown www-data:www-data /var/log/pentagon

# Configure log rotation
sudo nano /etc/logrotate.d/pentagon
```

Add the following content:

```
/var/log/pentagon-backend-*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload pentagon-backend
    endscript
}
```

### 2. Health Check Script

```bash
# Create health check script
sudo nano /usr/local/bin/pentagon-health-check.sh
```

Add the following content:

```bash
#!/bin/bash

# Pentagon International Health Check Script
API_URL="http://localhost:5000/api/health"
ADMIN_URL="http://admin.pentagon.com"
SALES_URL="http://sales.pentagon.com"

# Check API health
if curl -f -s $API_URL > /dev/null; then
    echo "$(date): API is healthy"
else
    echo "$(date): API is down - restarting service"
    sudo systemctl restart pentagon-backend
fi

# Check frontend availability
if curl -f -s $ADMIN_URL > /dev/null; then
    echo "$(date): Admin panel is accessible"
else
    echo "$(date): Admin panel is not accessible"
fi

if curl -f -s $SALES_URL > /dev/null; then
    echo "$(date): Sales portal is accessible"
else
    echo "$(date): Sales portal is not accessible"
fi
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/pentagon-health-check.sh

# Add to crontab for monitoring
sudo crontab -e
```

Add the following line:

```bash
*/5 * * * * /usr/local/bin/pentagon-health-check.sh >> /var/log/pentagon/health-check.log 2>&1
```

## 🔧 Performance Optimization

### 1. Backend Optimization

```bash
# Update gunicorn configuration for better performance
sudo nano /etc/systemd/system/pentagon-backend.service
```

Update the ExecStart line:

```ini
ExecStart=/var/www/pentagon-backend/venv/bin/gunicorn --workers 4 --worker-class gevent --worker-connections 1000 --bind 0.0.0.0:5000 --timeout 120 --keepalive 2 --max-requests 1000 --max-requests-jitter 100 --access-logfile /var/log/pentagon-backend-access.log --error-logfile /var/log/pentagon-backend-error.log src.main:app
```

### 2. Nginx Optimization

```bash
# Update Nginx configuration
sudo nano /etc/nginx/nginx.conf
```

Add performance optimizations:

```nginx
worker_processes auto;
worker_connections 1024;

http {
    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Enable caching
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 10m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
}
```

## 🔐 Security Hardening

### 1. Firewall Configuration

```bash
# Install and configure UFW
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow necessary ports
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### 2. Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Create custom configuration
sudo nano /etc/fail2ban/jail.local
```

Add the following content:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
```

```bash
# Start and enable Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

## 🚀 Deployment Checklist

### Pre-Deployment

- [ ] Server meets minimum requirements
- [ ] Domain names are configured and pointing to server
- [ ] SSL certificates are ready
- [ ] Database backup strategy is in place
- [ ] Monitoring tools are configured

### Deployment Steps

- [ ] Backend deployed and running
- [ ] Frontend applications built and deployed
- [ ] Nginx configured and running
- [ ] SSL certificates installed
- [ ] Database initialized with admin user
- [ ] Health checks are working
- [ ] Logs are being generated
- [ ] Backups are scheduled

### Post-Deployment

- [ ] All services are running correctly
- [ ] Admin panel is accessible
- [ ] Sales portal is accessible
- [ ] API endpoints are responding
- [ ] SSL certificates are valid
- [ ] Performance is acceptable
- [ ] Security measures are in place

## 🆘 Troubleshooting

### Common Issues

1. **Backend not starting**:
   ```bash
   # Check service status
   sudo systemctl status pentagon-backend
   
   # Check logs
   sudo journalctl -u pentagon-backend -f
   ```

2. **Frontend not loading**:
   ```bash
   # Check Nginx status
   sudo systemctl status nginx
   
   # Check Nginx logs
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Database issues**:
   ```bash
   # Check database file permissions
   ls -la /var/www/pentagon-backend/src/database/
   
   # Recreate database if needed
   cd /var/www/pentagon-backend
   source venv/bin/activate
   python src/main.py
   ```

4. **SSL certificate issues**:
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificates
   sudo certbot renew
   ```

### Emergency Procedures

1. **Service Recovery**:
   ```bash
   # Restart all services
   sudo systemctl restart pentagon-backend
   sudo systemctl restart nginx
   ```

2. **Database Recovery**:
   ```bash
   # Restore from backup
   cp /var/backups/pentagon/pentagon_db_YYYYMMDD_HHMMSS.db /var/www/pentagon-backend/src/database/app.db
   sudo chown www-data:www-data /var/www/pentagon-backend/src/database/app.db
   ```

## 📞 Support

For deployment support or issues:

1. Check the application logs
2. Review this deployment guide
3. Contact the development team with specific error messages
4. Include server specifications and OS version in support requests

---

**Pentagon International Production Deployment Guide**
*Version 1.0 - Built for reliability and security*

