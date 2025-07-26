# E‑Commerce API

A RESTful E‑Commerce backend built with Django 5.2 and Django REST Framework (DRF).
Features shopping cart, orders, Stripe payments, product & category management, and JWT‑based authentication with a custom email‑based user model.

---

## 🚀 Features

- **User Accounts** via email/password (register, login, profile, token revoke)
- **Products & Categories**
  - CRUD by admin
  - Public listing & detail views
- **Shopping Cart**
  - Add, update, remove items
  - View current cart
- **Orders**
  - Checkout your cart
  - List & retrieve your orders
- **Payments**
  - Stripe integration (initiate, webhook/status)
- **Permissions**
  - Only owners & admins can modify resources
  - Public vs. private visibility enforced at object level
- **API Documentation** via Swagger (`drf-yasg`)

---

## 📦 Requirements

- Python 3.13+
- Django==5.2
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- python-decouple
- drf-yasg
- stripe
- psycopg2-binary (for PostgreSQL)
- Pillow

---

## 🔧 Installation

1. **Clone & enter directory**
   ```bash
   git clone https://github.com/justzeiad/ecommerce-api.git
   cd ecommerce-api
   ```

2. **Virtualenv & dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment**
   Copy `.env.example` → `.env` and configure:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   STRIPE_SECRET_KEY=sk_test_...
   ```

4. **Migrate & create superuser**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run server**
   ```bash
   python manage.py runserver
   ```

6. **View Swagger docs**
   Open http://127.0.0.1:8000/swagger/

---

## 🌐 API Endpoints

### Auth (/accounts/)
| Method | Endpoint                | Description                       |
| ------ | ----------------------- | --------------------------------- |
| POST   | `/accounts/register/`   | Register new user                 |
| POST   | `/accounts/login/`      | Obtain JWT access & refresh       |
| DELETE | `/accounts/logout/`     | Revoke refresh token (logout)     |
| GET    | `/accounts/profile/`    | Get own profile                   |
| PUT    | `/accounts/profile/`    | Update profile                    |

### Products & Categories
| Method | Endpoint                     | Description                          |
| ------ | ---------------------------- | ------------------------------------ |
| GET    | `/products/`                 | List all active products             |
| POST   | `/products/`                 | Create product (admin only)          |
| GET    | `/products/{slug}/`          | Retrieve product by slug             |
| PUT    | `/products/{slug}/`          | Update product (admin only)          |
| DELETE | `/products/{slug}/`          | Delete product (admin only)          |
| GET    | `/categories/`               | List all categories                  |

### Cart (/cart/)
| Method | Endpoint                      | Description                        |
| ------ | ----------------------------- | ---------------------------------- |
| GET    | `/cart/`                      | View current user’s cart           |
| POST   | `/cart/add/`                  | Add an item to cart                |
| PUT    | `/cart/update/{item_id}/`     | Update quantity of an item         |
| DELETE | `/cart/remove/{item_id}/`     | Remove an item                     |
| POST   | `/cart/clear/`                | Remove all items                   |

### Orders (/orders/)
| Method | Endpoint                    | Description                        |
| ------ | --------------------------- | ---------------------------------- |
| GET    | `/orders/`                  | List your orders                   |
| POST   | `/orders/`                  | Create an order (checkout cart)    |
| GET    | `/orders/{order_id}/`       | Retrieve a specific order          |

### Payments (/payments/)
| Method | Endpoint                    | Description                      |
| ------ | --------------------------- | -------------------------------- |
| POST   | `/payments/`                | Initiate payment (Stripe)        |
| GET    | `/payments/{order_id}/`     | Get payment status/details       |

---

## 📂 Project Structure

```
ecommerce/
├── accounts/        # Custom User model & auth views
├── products/        # Category & Product APIs
├── cart/            # Shopping cart logic
├── orders/          # Order processing & history
├── payments/        # Stripe integration & webhooks
├── ecommerce/       # Settings, root URLs, WSGI/ASGI
└── manage.py
```

---

## 🤝 Contributing

- Fork & create a feature branch
- Write tests & follow code style (Black, isort)
- Submit a pull request for review

---

*Happy coding & selling!*  
