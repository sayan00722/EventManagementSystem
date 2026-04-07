<<<<<<< HEAD
# Event Management System

Simple role-based Event Management web app built with Flask and MySQL.

## Live Site

https://eventmanagementsystem-1-jjdk.onrender.com/
<br>Wait for sometimes for the webapp to load

## Roles

- Admin
- User
- Vendor

## Main Features

- Role-based login and dashboard
- Admin maintenance for users, vendors, memberships
- Vendor product management
- User cart, checkout, order status
- Reports and transactions

## Tech Stack

- Python (Flask)
- MySQL
- SQLAlchemy
- HTML/CSS/JavaScript

## Local Run

1. Create and activate virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:

- FLASK_APP=run.py
- FLASK_ENV=development
- SECRET_KEY=your_secret_key
- DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DB_NAME

4. Apply schema and seed:

```powershell
.\.venv\Scripts\python.exe manage.py apply-sql --db-user root --db-secret your_password --db-host localhost --db-port 3306
```

5. Run app:

```powershell
flask run --port 5001
```

Open: http://127.0.0.1:5001

## Demo Accounts (from seed)

- Admin: admin@event.com / Admin@123
- Vendor: vendor@event.com / Admin@123
- User: user@event.com / Admin@123

## Deploy

- Hosted on Render
- Uses external MySQL database (Aiven)
=======
Hosted Website Link : https://eventmanagementsystem-1-jjdk.onrender.com/
>>>>>>> 2928a42703b8da22883bf331783d86463933748e
