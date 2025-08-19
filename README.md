# Store Management System / Inventory Management System

A full-featured **Inventory Management System** built with **Django REST Framework** (backend) and **React.js** (frontend). The system supports **role-based authentication** for Admin and Cashier users, inventory tracking, and secure operations.  

This repository contains the **Django REST Framework backend**, including APIs, authentication, and deployment setup.  

---

## 🛠 Features

### Backend (Django REST Framework)
- **Role-based authentication**: Separate Admin and Cashier accounts using **Djoser**.
- **User management**: Admin can create, edit, and delete cashier accounts.
- **Inventory management**: CRUD operations for products, stock, and categories.
- **Sales management**: Cashiers can create sales orders with product selection and quantity.
- **Reporting**: Admin can view sales reports, stock levels, and product activity.
- **Token-based authentication**: Secure JWT token authentication for all API endpoints.
- **API documentation**: Swagger / DRF browsable API support.
- **Deployment-ready**: Configured for production deployment.

### Frontend (React.js)
> *Frontend code not included in this repo — communicates with backend via REST APIs.*

- Dashboard for Admin and Cashier roles.
- Product and inventory management UI.
- Sales entry forms for Cashiers.
- Reports visualization.

---

## ⚡ Tech Stack

- **Backend**: Python, Django, Django REST Framework, Djoser, PostgreSQL (or SQLite for dev)
- **Frontend**: React.js, Axios
- **Authentication**: Djoser + JWT
- **Deployment**: Docker / Gunicorn / Nginx (optional), Heroku/AWS compatible

---

## 🚀 Getting Started (Backend)

### Prerequisites
- Python 3.10+
- Pipenv or virtualenv
- PostgreSQL (or SQLite for development)
- Node.js & npm (for frontend if testing locally)

### Installation
```bash
# Clone the repo
git clone https://github.com/yourusername/store-management-system.git
cd store-management-system

# Create virtual environment and activate
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (Admin)
python manage.py createsuperuser
```


# Start the development server
python manage.py runserver
