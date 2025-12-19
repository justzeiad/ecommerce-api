# 🛒 E-Commerce API

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

A modern, full-featured RESTful E-Commerce backend API built with Django 5.2 and Django REST Framework. Features include shopping cart management, order processing, Stripe payment integration, product & category management, and secure JWT-based authentication with a custom email-based user model.

---

## 📑 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **🔐 User Authentication**
  - Email-based registration and login
  - JWT token authentication (access & refresh tokens)
  - User profile management
  - Secure account deletion

- **📦 Product Management**
  - Category organization
  - Product CRUD operations (admin only)
  - Product listing with filtering
  - Slug-based product retrieval
  - Image upload support

- **🛒 Shopping Cart**
  - Add/update/remove items
  - Real-time cart totals
  - User-specific cart management
  - Clear cart functionality

- **📋 Order Processing**
  - Checkout cart to create orders
  - Order history tracking
  - Order detail retrieval
  - Status management

- **💳 Payment Integration**
  - Stripe payment processing
  - Payment status tracking
  - Webhook support for payment events
  - Secure payment handling

- **🔒 Security & Permissions**
  - Role-based access control (RBAC)
  - Owner and admin permissions
  - JWT token security
  - CORS configuration

- **📚 API Documentation**
  - Interactive Swagger UI
  - ReDoc documentation
  - OpenAPI schema generation

---

## 🛠 Tech Stack

- **Backend Framework:** Django 5.2
- **API Framework:** Django REST Framework (DRF)
- **Authentication:** djangorestframework-simplejwt
- **Payment Processing:** Stripe
- **API Documentation:** drf-yasg (Swagger/OpenAPI)
- **Database:** SQLite (development) / PostgreSQL (production)
- **Image Processing:** Pillow
- **CORS:** django-cors-headers
- **Environment Management:** python-dotenv
- **Code Quality:** Black, isort

---

## 📦 Requirements

- **Python:** 3.13+
- **Django:** 5.2
- **Django REST Framework:** 3.14+

See [requirements.txt](requirements.txt) for a complete list of dependencies.

---

## 🔧 Installation

1. **Clone & enter directory**
   ```bash
   git clone https://github.com/justzeiad/dj-ecommerce.git
   cd dj-ecommerce
   ```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

See [Environment Variables](#-environment-variables) section for details.

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

### 8. Access API Documentation

- **Swagger UI:** http://127.0.0.1:8000/swagger/
- **ReDoc:** http://127.0.0.1:8000/redoc/
- **OpenAPI Schema:** http://127.0.0.1:8000/swagger.json

---

## 🔐 Environment Variables

Create a `.env` file in the root directory with the following variables:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing | `your-secret-key-here` | ✅ |
| `DJANGO_DEBUG` | Debug mode (set to False in production) | `True` | ✅ |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` | ✅ |
| `STRIPE_SECRET_KEY` | Stripe API secret key | `sk_test_...` | ✅ |
| `DATABASE_URL` | Database connection URL | `sqlite:///db.sqlite3` | ⚠️ |

> **⚠️ Note:** Never commit your `.env` file to version control. Use `.env.example` as a template.

> **💡 Tip:** Generate a secure Django secret key using:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🌐 API Endpoints

All API endpoints are prefixed with `/api/v1/`.

### 🔑 Authentication (`/api/v1/accounts/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/accounts/register/` | Register a new user | ❌ |
| `POST` | `/api/v1/accounts/login/` | Login and obtain JWT tokens | ❌ |
| `POST` | `/api/v1/accounts/token/refresh/` | Refresh access token | ❌ |
| `GET` | `/api/v1/accounts/profile/` | Get current user profile | ✅ |
| `PUT` | `/api/v1/accounts/profile/` | Update user profile | ✅ |
| `PATCH` | `/api/v1/accounts/profile/` | Partially update user profile | ✅ |
| `DELETE` | `/api/v1/accounts/profile/delete/` | Delete user account | ✅ |

### 📦 Products & Categories (`/api/v1/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/categories/` | List all categories | ❌ |
| `GET` | `/api/v1/categories/{slug}/` | Get category details | ❌ |
| `GET` | `/api/v1/products/` | List all active products | ❌ |
| `POST` | `/api/v1/products/` | Create a new product | ✅ (Admin) |
| `GET` | `/api/v1/products/{slug}/` | Get product details | ❌ |
| `PUT` | `/api/v1/products/{slug}/` | Update product | ✅ (Admin) |
| `PATCH` | `/api/v1/products/{slug}/` | Partially update product | ✅ (Admin) |
| `DELETE` | `/api/v1/products/{slug}/` | Delete product | ✅ (Admin) |

### 🛒 Shopping Cart (`/api/v1/cart/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/cart/` | View current user's cart | ✅ |
| `POST` | `/api/v1/cart/add/` | Add item to cart | ✅ |
| `PUT` | `/api/v1/cart/update/{item_id}/` | Update cart item quantity | ✅ |
| `DELETE` | `/api/v1/cart/remove/{item_id}/` | Remove item from cart | ✅ |
| `POST` | `/api/v1/cart/clear/` | Clear all cart items | ✅ |

### 📋 Orders (`/api/v1/orders/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/orders/` | List user's orders | ✅ |
| `POST` | `/api/v1/orders/create/` | Create order from cart | ✅ |
| `GET` | `/api/v1/orders/{order_id}/` | Get order details | ✅ |

### 💳 Payments (`/api/v1/payments/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/payments/create/` | Initiate payment for order | ✅ |
| `GET` | `/api/v1/payments/status/{order_id}/` | Get payment status | ✅ |
| `POST` | `/api/v1/payments/webhook/` | Stripe webhook endpoint | ❌ |

---

## 📚 API Documentation

This project uses **drf-yasg** to provide interactive API documentation.

### Swagger UI

Access the interactive Swagger documentation at:
```
http://127.0.0.1:8000/swagger/
```

The Swagger UI allows you to:
- Browse all available endpoints
- Test API requests directly in the browser
- View request/response schemas
- Explore authentication requirements

### ReDoc

Alternative documentation interface available at:
```
http://127.0.0.1:8000/redoc/
```

### OpenAPI Schema

Raw OpenAPI/Swagger schema in JSON format:
```
http://127.0.0.1:8000/swagger.json
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test products

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage

To generate a detailed coverage report:

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage html
# Open htmlcov/index.html in your browser
```

---

## 🚀 Deployment

### Production Checklist

Before deploying to production:

1. **Environment Variables**
   - Set `DJANGO_DEBUG=False`
   - Update `DJANGO_ALLOWED_HOSTS` with your domain
   - Use a strong, unique `DJANGO_SECRET_KEY`
   - Configure production database (PostgreSQL recommended)
   - Set production `STRIPE_SECRET_KEY`

2. **Database**
   ```bash
   # Use PostgreSQL in production
   pip install psycopg2-binary
   # Update DATABASE_URL in .env
   ```

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

4. **Security Settings**
   - Enable HTTPS
   - Configure CORS settings for your frontend domain
   - Set up proper firewall rules
   - Enable security middleware

5. **Monitoring**
   - Set up error tracking (e.g., Sentry)
   - Configure logging
   - Monitor server performance

### Deployment Platforms

This application can be deployed to:

- **Heroku:** Use Heroku's PostgreSQL addon and configure buildpacks
- **AWS:** Deploy using Elastic Beanstalk or EC2 with RDS
- **DigitalOcean:** Use App Platform or Droplets
- **Railway:** Simple deployment with automatic PostgreSQL provisioning
- **Render:** Easy deployment with managed databases

---

## 📂 Project Structure

```
Ecommerce/
├── core/                   # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
│
├── users/                  # User authentication app
│   ├── models.py          # Custom User model
│   ├── serializers.py     # User serializers
│   ├── views.py           # Auth views
│   └── urls.py            # Auth endpoints
│
├── products/               # Products & categories app
│   ├── models.py          # Product and Category models
│   ├── serializers.py     # Product serializers
│   ├── views.py           # Product views
│   ├── urls.py            # Product endpoints
│   └── admin.py           # Admin interface
│
├── cart/                   # Shopping cart app
│   ├── models.py          # Cart and CartItem models
│   ├── serializers.py     # Cart serializers
│   ├── views.py           # Cart views
│   └── urls.py            # Cart endpoints
│
├── orders/                 # Order management app
│   ├── models.py          # Order and OrderItem models
│   ├── serializers.py     # Order serializers
│   ├── views.py           # Order views
│   └── urls.py            # Order endpoints
│
├── payments/               # Payment processing app
│   ├── models.py          # Payment model
│   ├── serializers.py     # Payment serializers
│   ├── views.py           # Payment views (Stripe integration)
│   └── urls.py            # Payment endpoints
│
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── postman_collection.json # Postman API collection
└── README.md             # This file
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Make your changes**
   - Write clean, documented code
   - Follow PEP 8 style guide
   - Format code with Black and isort
   - Add tests for new features

4. **Run tests and linting**
   ```bash
   python manage.py test
   black .
   isort .
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add new feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/new-feature
   ```

7. **Open a Pull Request**

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **PEP 8** for Python code style

```bash
# Format code
black .
isort .
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

For questions, issues, or feature requests:

- **Issues:** [GitHub Issues](https://github.com/justzeiad/dj-ecommerce/issues)

