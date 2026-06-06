# Inventory Billing API

A Django REST API for managing products, stock movements, invoices, sales reports, and users. The project uses JWT-based authentication and includes generated OpenAPI documentation.

## Tech Stack

- Python 3.12
- Django 6
- Django REST Framework
- PostgreSQL
- Docker and Docker Compose
- drf-spectacular for OpenAPI/Swagger docs
- Simple JWT, dj-rest-auth, and django-allauth for authentication

## Main Endpoints

Base URL for local development:

```bash
http://localhost:8000
```

Notable routes:

- `GET /api/docs/` - Swagger API documentation
- `GET /api/schema/` - OpenAPI schema
- `/auth/` - login, logout, password reset, and auth endpoints
- `/auth/registration/` - user registration
- `/inventory/products/` - products
- `/inventory/stock-movements/` - stock movements
- `/invoices/list/` - invoices
- `/invoices/<id>/` - invoice detail
- `/invoices/<id>/pdf/` - invoice PDF download
- `/reports/sales-summary/` - sales summary report
- `/reports/top-selling-products/` - top-selling products report
- `/reports/sales-by-day/` - sales by day report
- `/users/list/` - users
- `/users/detail/<id>/` - user detail

## Running With Docker

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open `.env` and replace the placeholder values with real values:

```env
SECRET_KEY=your-secret-key-here
POSTGRES_USER=your-postgres-user
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=your-database-name
```

For local development, `DEBUG=True`, `ALLOWED_HOSTS=127.0.0.1,localhost`, `DB_HOST=postgres`, and `EMAIL_BACKEND=console` are usually fine.

Generate a random Django secret key with:

```bash
python - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
```

3. Build and start the containers:

```bash
docker compose up -d --build
```

Or use the Makefile:

```bash
make up
```

4. Run database migrations:

```bash
make migrate
```

5. Create an admin user if needed:

```bash
docker compose exec django_web python backend/manage.py createsuperuser
```

6. Visit the API docs:

```bash
http://localhost:8000/api/docs/
```

## Useful Commands

```bash
# Build and start containers
make up

# Stop containers
make down

# Run database migrations
make migrate

# Open Django shell
make shell

# Create an admin user
docker compose exec django_web python backend/manage.py createsuperuser

# Run tests
docker compose exec django_web python backend/manage.py test
```

## Notes

- Do not commit your real `.env` file.
- Use strong database credentials outside local development.
- Set `DEBUG=False`, configure production `ALLOWED_HOSTS`, and use HTTPS-secure JWT cookie settings before deploying.
