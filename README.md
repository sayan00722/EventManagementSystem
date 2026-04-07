# Event Management System (Flask + MySQL)

A role-based Event Management System built with Flask, SQLAlchemy, MySQL, Jinja templates, and vanilla CSS/JS.

The app supports three roles:

- Admin: user/vendor maintenance, membership control, reports, transactions, order status updates
- User: browse vendors, add to cart, checkout, manage guest list, request items, track orders, view membership
- Vendor: manage items, view requests, view transactions, update order status

## Features

- Role-based login and protected routes
- Admin maintenance modules for users and vendors
- Membership lifecycle (add, update/extend, revoke)
- Vendor product management (add, update, delete)
- User cart and checkout flow
- Order + transaction generation on checkout
- Guest list management
- Product request workflow (user to vendor)
- User and admin reports pages
- Basic security:
  - Password hashing with bcrypt
  - CSRF protection via Flask-WTF
  - Session-based auth guards

## Tech Stack

- Python 3.10+
- Flask 3
- Flask-SQLAlchemy
- Flask-WTF
- Flask-Bcrypt
- PyMySQL
- MySQL 8+

## Project Structure

- app/
  - models/
  - routes/
  - services/
  - static/
  - templates/
- sql/
  - schema.sql
  - seed.sql
  - dummy_data.sql
- manage.py
- run.py

## Prerequisites

1. Python 3.10 or above installed
2. MySQL Server running locally
3. MySQL CLI available in PATH (required for manage.py apply-sql)
4. PowerShell (for Windows command examples)

## Environment Variables

Create a .env file in project root:

FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sayan_secret_event_2026
DATABASE_URL=mysql+pymysql://root:sayan1234@localhost:3306/event_management

You can also copy from .env.example and edit values if needed.

## Local Setup (Windows)

1. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Apply schema and base seed

```powershell
.\.venv\Scripts\python.exe manage.py apply-sql --db-user root --db-secret sayan1234 --db-host localhost --db-port 3306
```

4. Run the app

```powershell
flask run --port 5001
```

Open in browser:

- http://127.0.0.1:5001

## Demo Accounts (Base Seed)

- Admin:
  - Email: admin@event.com
  - Password: Admin@123
- Vendor:
  - Email: vendor@event.com
  - Password: Admin@123
- User:
  - Email: user@event.com
  - Password: Admin@123

## Add More Demo Data

Use extended data script (more vendors/products/users):

```powershell
mysql -u root -psayan1234 -e "source C:/Users/Sayan/Desktop/Event/sql/dummy_data.sql;"
```

Notes:

- This script inserts additional users/vendors/products.
- If you need fully fresh data, clear tables first or recreate database.

## Optional CLI Commands

Initialize tables via SQLAlchemy:

```powershell
.\.venv\Scripts\python.exe manage.py init-db
```

Seed minimal demo users via Python:

```powershell
.\.venv\Scripts\python.exe manage.py seed-demo
```

Create a custom admin:

```powershell
.\.venv\Scripts\python.exe manage.py create-admin --name "Owner" --email "owner@example.com" --password "StrongPass1"
```

## Role-Based Flow

### Admin

- Login: /login/admin
- Dashboard: /admin/dashboard
- Modules:
  - Maintenance User: add/update/delete users
  - Maintenance Vendor: add/update/delete vendors, sync sell_items to products
  - Membership: add/update/revoke user memberships
  - Reports: order and revenue summary
  - Transactions: payment records and status updates

### User

- Login: /login/user
- Dashboard: /user/dashboard
- Modules:
  - Vendors: browse by category and add products to cart
  - Cart: update/remove/clear items
  - Checkout: place order and create transaction
  - Guest List: add/update/delete guests
  - Request Item: request custom items from vendors
  - Order Status: track all placed orders
  - Membership: view and manage own membership extension/cancel
  - Reports and Transactions: personal summary and payment list

### Vendor

- Login: /login/vendor
- Dashboard: /vendor/dashboard
- Modules:
  - Items: add/update/delete products
  - Requests: view user product requests
  - Transactions: view transactions related to vendor products
  - Status: update order status for relevant orders

## Database Tables

The schema includes:

- users
- vendors
- products
- cart
- orders
- order_items
- membership
- transactions
- guest_list
- product_requests

See sql/schema.sql for full definitions and constraints.

## Common Troubleshooting

1. MySQL syntax issue for ADD COLUMN IF NOT EXISTS

- Already handled in sql/schema.sql using information_schema check + dynamic SQL.
- Re-run apply-sql after pulling latest code.

2. mysql command not found

- Add MySQL bin directory to PATH.
- Or run full path to mysql.exe.

3. Access denied for MySQL

- Verify username/password/host/port in .env and apply-sql arguments.

4. Port already in use

- Run on another port:

```powershell
flask run --port 5002
```

5. Login fails unexpectedly

- Ensure account role matches login path:
  - admin account on /login/admin
  - user account on /login/user
  - vendor account on /login/vendor

## Logs

Application logs are written to:

- logs/event_management.log

Tail logs:

```powershell
Get-Content .\logs\event_management.log -Wait
```

## Security Notes

- Passwords are hashed with bcrypt.
- CSRF tokens are required for POST forms.
- Session stores authenticated role and user identity.
- Route guards enforce role access.

## License

This project is for academic/demo use unless you add your own production license.
