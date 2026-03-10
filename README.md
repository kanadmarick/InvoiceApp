# Invoice Pro — Full-Stack Invoice Management System

A production-ready invoice management application built with **Django REST Framework** and **React 19**, featuring JWT authentication, PDF generation, and one-click deployment to Oracle Cloud.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.2, Django REST Framework 3.16, Python 3.13 |
| **Frontend** | React 19, Vite 7, Tailwind CSS v4, React Router v7 |
| **Auth** | SimpleJWT (access + refresh tokens, rotation, blacklisting) |
| **Database** | PostgreSQL 15 |
| **API Docs** | drf-spectacular (OpenAPI 3 / Swagger UI) |
| **PDF** | Playwright (headless Chromium → HTML-to-PDF) |
| **Server** | Gunicorn + Nginx reverse proxy |
| **Static Files** | WhiteNoise (production) |
| **Containerization** | Docker & Docker Compose |
| **Deployment** | Oracle Cloud Always Free Tier (ARM Ampere A1) |

---

## Features

- **JWT Authentication** — Login, register, guest login, token refresh with automatic rotation
- **Multi-Business Support** — Users can manage multiple businesses with branding (logo, brand color)
- **Invoice Management** — Create, edit, delete invoices with nested line items and milestones
- **Smart Invoice Status** — Auto-computed from milestones: Draft → Pending → Partially Paid → Paid / Overdue
- **PDF Export** — Professional PDF invoices generated server-side with Playwright (headless Chromium)
- **Dashboard** — Aggregated stats (total revenue, outstanding, overdue, invoice counts)
- **Indian Rupee Formatting** — Custom template filter with proper Indian number grouping (₹ 1,23,456.78)
- **Guest Login** — One-click demo access with pre-configured credentials
- **Responsive Design** — Mobile-friendly sidebar layout with Tailwind CSS
- **API Documentation** — Auto-generated Swagger UI at `/api/docs/`

---

## Project Structure

```
├── config/                  # Django settings, root URLs, WSGI/ASGI
├── accounts/                # Custom user model (UUID PK), JWT auth endpoints
├── businesses/              # Business profiles (logo, GSTIN, brand color)
├── billings/                # Invoices, clients, line items, milestones, PDF generation
├── core/                    # Abstract base models (BaseModel, ContactInfoModel), template tags
├── frontend/                # React SPA (Vite + Tailwind + React Router)
│   └── src/
│       ├── components/      # Layout, ProtectedRoute
│       ├── context/         # AuthContext (JWT management)
│       ├── pages/           # 11 pages (Dashboard, Login, CRUD for all entities)
│       └── api.js           # Axios client with JWT interceptors
├── nginx/                   # Nginx config (HTTP + SSL), multi-stage Dockerfile
├── templates/               # Django base templates
├── docker-compose.yml       # Development (hot-reload)
├── docker-compose.prod.yml  # Production (Gunicorn + Nginx + PostgreSQL + Certbot)
├── Dockerfile               # Development image
├── Dockerfile.prod          # Production image (non-root user, auto-migrate)
└── DEPLOYMENT_GUIDE.md      # Step-by-step Oracle Cloud deployment
```

---

## Data Models

```
CustomUser (UUID)
  ├── phone_number, bio, profile_image, is_premium
  └── owns → Business[]
               ├── name, gstin, logo, brand_color, email, address fields
               ├── has → Client[]
               │           └── name, email, address fields
               └── has → DraftItem[]
                           └── description, unit_price

Invoice (UUID)
  ├── client → Client
  ├── invoice_number (unique), notes
  ├── status (computed: DRAFT | PENDING | PARTIALLY_PAID | PAID | OVERDUE)
  ├── total_amount (computed from items)
  ├── has → InvoiceItem[]
  │           └── description, quantity, unit_price, line_total
  └── has → Milestone[]
              └── description, amount, due_date, status
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/login/` | Login (returns JWT tokens) |
| POST | `/accounts/register/` | Register new user |
| POST | `/accounts/guest-login/` | One-click guest login |
| POST | `/accounts/logout/` | Logout (blacklist refresh token) |
| POST | `/accounts/token/refresh/` | Refresh access token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/accounts/users/` | List all users (admin only) |
| GET/PUT/PATCH | `/accounts/users/<uuid>/` | User profile detail |

### Businesses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/businesses/` | List / create businesses |
| GET/PUT/PATCH/DELETE | `/businesses/<uuid>/` | Business detail |

### Invoices
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/billings/invoices/` | List / create invoices (nested items + milestones) |
| GET/PUT/PATCH/DELETE | `/billings/invoices/<uuid>/` | Invoice detail |
| GET | `/billings/invoices/<uuid>/pdf/` | Download invoice as PDF |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/` | Dashboard stats (revenue, counts) |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/schema/` | OpenAPI 3 JSON schema |

---

## Quick Start — Development

### Prerequisites
- Python 3.13+
- Node.js 22+
- PostgreSQL 15+ (or Docker)

### Option A: Docker (recommended)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/Invoices.git
cd Invoices

# Create environment file
cp .env.example .env
# Edit .env with your database credentials

# Start all services
docker compose up --build

# In another terminal, run migrations and create superuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

React SPA 	http://152.70.79.182/	
Swagger API Docs	http://152.70.79.182/api/docs/
Django Admin	http://152.70.79.182/admin/	

### Option B: Local setup

```bash
# Backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Edit with your PostgreSQL credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Load demo data (optional)

```bash
python manage.py populate_dummy_data
```

---

## Production Deployment (Oracle Cloud)

Full guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

```bash
# On the OCI VM:
git clone <repo-url> /opt/invoices && cd /opt/invoices
cp .env.prod.example .env.prod   # Edit with production values
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

Architecture: **Nginx** (serves React SPA + reverse proxies API) → **Gunicorn** (Django) → **PostgreSQL** — all in Docker with optional Let's Encrypt SSL via Certbot.

---

## Environment Variables

See [.env.example](.env.example) (development) and [.env.prod.example](.env.prod.example) (production) for all available options.

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | *required* |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `localhost` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | PostgreSQL credentials | — |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `GUEST_USERNAME` / `GUEST_PASSWORD` | Demo login credentials | — |
| `VITE_API_URL` | Frontend API base URL | `http://localhost:8000` |

---

## License

This project is for portfolio/educational purposes.
