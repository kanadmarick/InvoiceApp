# API Refactor — Comprehensive Change Notes

> **Date:** June 2025  
> **Scope:** Converted the Django Invoices project from a server-rendered (template-based) architecture to a fully API-driven architecture with a React SPA frontend.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Backend — New Files Created](#2-backend--new-files-created)
3. [Backend — Serializers](#3-backend--serializers)
4. [Backend — API Views](#4-backend--api-views)
5. [Backend — URL Routing](#5-backend--url-routing)
6. [Backend — Settings & Configuration](#6-backend--settings--configuration)
7. [Frontend — React SPA](#7-frontend--react-spa)
8. [Authentication Flow](#8-authentication-flow)
9. [Key Fixes During Refactor](#9-key-fixes-during-refactor)
10. [Known Remaining Items](#10-known-remaining-items)

---

## 1. Architecture Overview

### Before (Template-Based)

```
Browser → Django URLs → Django CBVs (TemplateView / FormView)
                          ↓
                    Django Templates (HTML + Tailwind)
                          ↓
                    Server-rendered HTML response
```

- All views were Django class-based views (CBVs): `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`.
- Authentication used Django's built-in `LoginView` / `LogoutView` with session cookies.
- URLs returned rendered HTML pages.
- Forms used Django's `{% csrf_token %}` and server-side form validation.

### After (API-Driven)

```
Browser → React SPA (Vite @ :3000)  →  Axios API Client  →  Django REST Framework (@ :8000)
              ↓                                                      ↓
     React Router (client-side)                              JSON responses
     Tailwind CSS v4                                         JWT authentication
     AuthContext (localStorage)                               drf-spectacular (OpenAPI)
```

- Django serves **only JSON API endpoints** — no HTML templates are rendered.
- The root URL (`/`) serves the **Swagger UI** (OpenAPI documentation).
- A standalone **React SPA** (Vite + React 19 + Tailwind v4) handles all UI.
- Authentication uses **SimpleJWT** (access + refresh tokens stored in `localStorage`).
- CORS is configured to allow the React dev server at `localhost:3000`.

---

## 2. Backend — New Files Created

| File | Purpose |
|------|---------|
| `accounts/serializers.py` | DRF serializers for user profiles and authentication |
| `businesses/serializers.py` | DRF serializers for business CRUD |
| `billings/serializers.py` | DRF serializers for invoices, clients, items, milestones |

---

## 3. Backend — Serializers

### `accounts/serializers.py`

| Serializer | Purpose | Key Fields |
|------------|---------|------------|
| `UserSerializer` | Full user profile (read) | `id`, `username`, `email`, `first_name`, `last_name`, `phone`, `address`, `city`, `state`, `zip_code`, `is_premium`, `date_joined` |
| `UserListSerializer` | Compact user listing | `id`, `username`, `email`, `first_name`, `last_name`, `is_premium` |
| `RegisterSerializer` | User registration (write) | `username`, `email`, `password`, `password2`, `first_name`, `last_name` — validates password match, calls `create_user()` |
| `LoginSerializer` | Login credentials (write) | `username`, `password` — calls `authenticate()`, attaches `user` to validated data |
| `PasswordResetRequestSerializer` | Request password reset | `email` |
| `PasswordResetConfirmSerializer` | Confirm password reset | `token`, `new_password`, `new_password2` |

### `businesses/serializers.py`

| Serializer | Purpose | Key Fields |
|------------|---------|------------|
| `BusinessSerializer` | Full business CRUD | All model fields; `owner` is `ReadOnlyField(source='owner.username')`; includes `logo_url_safe` SerializerMethodField |
| `BusinessListSerializer` | Compact business listing | `id`, `name`, `email`, `phone`, `brand_color`, `logo_url_safe` |

### `billings/serializers.py`

| Serializer | Purpose | Key Details |
|------------|---------|-------------|
| `ClientSerializer` | Client read/write | All model fields |
| `InvoiceItemSerializer` | Line item read/write | Includes `line_total` (SerializerMethodField: `quantity × unit_price`) |
| `MilestoneSerializer` | Milestone read/write | All model fields |
| `InvoiceSerializer` | **Read-only** nested invoice detail | Nests `ClientSerializer`, `InvoiceItemSerializer` (many), `MilestoneSerializer` (many); adds `status`, `total` as SerializerMethodFields |
| `InvoiceListSerializer` | Flat invoice listing | `client_name`, `business_name` (SerializerMethodFields), `status`, `total` |
| `InvoiceCreateUpdateSerializer` | **Writable nested** create/update | Accepts `client`, `items[]`, `milestones[]` inline; auto-increments `invoice_number` via `_next_invoice_number()`; `create()` builds Client + InvoiceItems + Milestones in one transaction; `update()` replaces items/milestones with delete-and-recreate |
| `DraftItemSerializer` | Draft line items | For saving invoice drafts |

---

## 4. Backend — API Views

### `accounts/views.py` — API Views Added

| View | Endpoint | Methods | Permissions | Description |
|------|----------|---------|-------------|-------------|
| `AccountListAPIView` | `/accounts/users/` | GET | `IsAdminUser` | List all users (admin only) |
| `AccountDetailAPIView` | `/accounts/users/<uuid>/` | GET, PUT, PATCH | `IsAuthenticated` | View/edit user profile; non-admins can only see own profile |
| `RegisterAPIView` | `/accounts/register/` | POST | `AllowAny` | Register new user; returns JWT tokens + user data |
| `LoginAPIView` | `/accounts/login/` | POST | `AllowAny` | Authenticate with username/password; creates session + returns JWT |
| `LogoutAPIView` | `/accounts/logout/` | POST | `IsAuthenticated` | Blacklists refresh token |
| `GuestLoginAPIView` | `/accounts/guest-login/` | POST | `AllowAny` | Login with env-var guest credentials; creates guest user if needed |

**Auth response format** (login, register, guest-login):
```json
{
  "message": "Login successful.",
  "user": { /* UserSerializer fields */ },
  "tokens": {
    "refresh": "eyJ...",
    "access": "eyJ..."
  }
}
```

### `businesses/views.py` — API Views Added

| View | Endpoint | Methods | Permissions | Description |
|------|----------|---------|-------------|-------------|
| `BusinessListCreateAPIView` | `/businesses/` | GET, POST | `IsAuthenticated` | List user's businesses / create new (auto-sets `owner`) |
| `BusinessDetailAPIView` | `/businesses/<uuid>/` | GET, PUT, PATCH, DELETE | `IsAuthenticated` | CRUD on single business; queryset scoped to owner |

### `billings/views.py` — API Views Added

| View | Endpoint | Methods | Permissions | Description |
|------|----------|---------|-------------|-------------|
| `InvoiceListCreateAPIView` | `/billings/invoices/` | GET, POST | `IsAuthenticated` | List/create invoices; supports `?status=`, `?client=`, `?search=` query params with SQL-level annotations for status filtering |
| `InvoiceDetailAPIView` | `/billings/invoices/<uuid>/` | GET, PUT, PATCH, DELETE | `IsAuthenticated` | Uses `InvoiceSerializer` (read-only) for GET, `InvoiceCreateUpdateSerializer` (writable) for PUT/PATCH; ownership enforced |

**Invoice status filtering** (`?status=` query param):
- `PAID` — all milestones have status PAID
- `OVERDUE` — has at least one milestone with status OVERDUE
- `PARTIALLY_PAID` — some milestones PAID but not all
- `PENDING` — has milestones, none are PAID or OVERDUE
- `DRAFT` — has zero milestones

### `config/views.py` — API View Added

| View | Endpoint | Methods | Permissions | Description |
|------|----------|---------|-------------|-------------|
| `DashboardAPIView` | `/api/dashboard/` | GET | `IsAuthenticated` | Returns aggregated stats: `total_invoices`, `paid_amount`, `pending_amount`, `overdue_amount`, `pending_count`, `overdue_count`, `recent_activity[]` |

---

## 5. Backend — URL Routing

### Before
All URL routes pointed to Django template-based CBVs. Example:
```python
# businesses/urls.py (BEFORE)
path('', BusinessListView.as_view(), name='business_list'),
path('<uuid:pk>/', BusinessDetailView.as_view(), name='business_detail'),
path('create/', BusinessCreateView.as_view(), name='business_create'),
path('<uuid:pk>/edit/', BusinessUpdateView.as_view(), name='business_update'),
path('<uuid:pk>/delete/', BusinessDeleteView.as_view(), name='business_delete'),
```

### After
All URL routes point to DRF API views. Each app also gets its own OpenAPI schema + Swagger UI endpoints.

**`config/urls.py`** (root):
```python
path('', SpectacularSwaggerView.as_view(url_name='schema'), name='home'),    # Swagger UI at root
path('api/schema/', SpectacularJSONAPIView.as_view(), name='schema'),          # OpenAPI JSON schema
path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard-api'),
path('accounts/', include('accounts.urls', namespace='accounts')),
path('businesses/', include('businesses.urls', namespace='businesses')),
path('billings/', include('billings.urls', namespace='billings')),
```

**`accounts/urls.py`**:
```python
path('users/', views.AccountListAPIView.as_view(), name='account_list'),
path('users/<uuid:pk>/', views.AccountDetailAPIView.as_view(), name='account_detail'),
path('login/', views.LoginAPIView.as_view(), name='login'),
path('guest-login/', views.GuestLoginAPIView.as_view(), name='guest_login'),
path('register/', views.RegisterAPIView.as_view(), name='register'),
path('logout/', views.LogoutAPIView.as_view(), name='logout'),
```

**`businesses/urls.py`**:
```python
path('', views.BusinessListCreateAPIView.as_view(), name='business_list'),
path('<uuid:pk>/', views.BusinessDetailAPIView.as_view(), name='business_detail'),
```

**`billings/urls.py`**:
```python
path('', views.InvoiceListCreateAPIView.as_view(), name='billing_list'),
path('invoices/', views.InvoiceListCreateAPIView.as_view(), name='invoice_list'),
path('invoices/<uuid:pk>/', views.InvoiceDetailAPIView.as_view(), name='invoice_detail'),
```

---

## 6. Backend — Settings & Configuration

### New Dependencies Added

| Package | Version | Purpose |
|---------|---------|---------|
| `djangorestframework` | 3.16.1 | API views, serializers, permissions |
| `djangorestframework-simplejwt` | 5.5.1 | JWT access/refresh token authentication |
| `django-cors-headers` | latest | CORS support for cross-origin React requests |
| `drf-spectacular` | 0.29.0 | OpenAPI 3.0 schema generation + Swagger UI |
| `whitenoise` | 6.9.0 | Serve static files via Gunicorn/WSGI in production |

### `INSTALLED_APPS` additions
```python
'rest_framework',
'rest_framework_simplejwt',
'corsheaders',
'drf_spectacular',
```

### `MIDDLEWARE` additions
```python
'whitenoise.middleware.WhiteNoiseMiddleware',  # Right after SecurityMiddleware — serves static files
'corsheaders.middleware.CorsMiddleware',       # Must be before CommonMiddleware
```

### `REST_FRAMEWORK` configuration
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

### `SIMPLE_JWT` configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### `CORS` configuration
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True
```

### `STATIC_URL` fix
```python
# Changed from 'static/' (relative) to '/static/' (absolute)
# The relative path caused browsers to resolve CSS URLs relative to the current page
# (e.g. /admin/static/... instead of /static/...), breaking admin panel styling
STATIC_URL = '/static/'
```

### `STATICFILES_STORAGE` (WhiteNoise)
```python
# Enables WhiteNoise to compress and cache-bust static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Dockerfile — `collectstatic`
```dockerfile
# Added before EXPOSE — gathers admin CSS/JS, DRF assets into staticfiles/
RUN python manage.py collectstatic --noinput 2>/dev/null || true
```

---

## 7. Frontend — React SPA

### Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2+ | UI framework |
| Vite | 7.3.1 | Build tool and dev server |
| Tailwind CSS | v4 | Utility-first CSS (using `@tailwindcss/vite` plugin) |
| React Router | v7 (v6 API) | Client-side routing |
| Axios | 1.13+ | HTTP client with JWT interceptors |
| Lucide React | 0.577+ | Icon library |

### New Files Created

```
frontend/
├── vite.config.js          # Vite config (React + Tailwind plugins, port 3000)
├── index.html              # SPA entry HTML
├── package.json            # Dependencies and scripts
├── .gitignore              # Ignores node_modules, dist
└── src/
    ├── main.jsx            # React entry point (BrowserRouter + AuthProvider)
    ├── App.jsx             # Route definitions (protected + guest routes)
    ├── api.js              # Axios instance with JWT interceptor
    ├── index.css           # Tailwind v4 import (@import "tailwindcss")
    ├── context/
    │   └── AuthContext.jsx # Auth state management (login/logout/register/guestLogin)
    ├── components/
    │   └── Layout.jsx      # Sidebar + topbar layout (matches original Django design)
    └── pages/
        ├── Login.jsx       # Login form + guest login button + password toggle
        ├── Register.jsx    # Registration form with field-level error display
        ├── Dashboard.jsx   # Summary cards + quick actions + recent activity
        ├── BusinessList.jsx    # Business card grid with search
        ├── BusinessDetail.jsx  # Full business info with edit/delete
        ├── BusinessForm.jsx    # Create/edit business with color picker
        ├── InvoiceList.jsx     # Invoice table with status badges + search + filter
        ├── InvoiceDetail.jsx   # Invoice detail with items table + milestones
        ├── InvoiceForm.jsx     # Create/edit with dynamic line items + milestones
        ├── AccountList.jsx     # User cards with avatar + premium badge
        └── AccountDetail.jsx   # Profile view with inline edit capability
```

### Route Map

| React Route | Page Component | Django API Endpoint |
|-------------|---------------|---------------------|
| `/login` | `Login` | `POST /accounts/login/` |
| `/register` | `Register` | `POST /accounts/register/` |
| `/` | `Dashboard` | `GET /api/dashboard/` |
| `/businesses` | `BusinessList` | `GET /businesses/` |
| `/businesses/new` | `BusinessForm` | `POST /businesses/` |
| `/businesses/:id` | `BusinessDetail` | `GET /businesses/<uuid>/` |
| `/businesses/:id/edit` | `BusinessForm` | `PUT /businesses/<uuid>/` |
| `/invoices` | `InvoiceList` | `GET /billings/invoices/` |
| `/invoices/new` | `InvoiceForm` | `POST /billings/invoices/` |
| `/invoices/:id` | `InvoiceDetail` | `GET /billings/invoices/<uuid>/` |
| `/invoices/:id/edit` | `InvoiceForm` | `PUT /billings/invoices/<uuid>/` |
| `/accounts` | `AccountList` | `GET /accounts/users/` |
| `/accounts/:id` | `AccountDetail` | `GET /accounts/users/<uuid>/` |

### API Client (`api.js`)

- Base URL: `http://localhost:8000` (configurable via `VITE_API_URL` env var)
- **Request interceptor:** Attaches `Authorization: Bearer <access_token>` from `localStorage`
- **Response interceptor:** On 401, attempts one token refresh via `/accounts/token/refresh/`; on failure, clears tokens and redirects to `/login`
- `withCredentials: true` for CORS cookie support

### Auth Context (`AuthContext.jsx`)

Provides app-wide auth state via React Context:
- **State:** `user` object (from `localStorage`), `isAuthenticated` boolean
- **Methods:** `login()`, `guestLogin()`, `register()`, `logout()`, `updateUser()`
- All auth methods store JWT tokens + user data in `localStorage`

---

## 8. Authentication Flow

### Login Flow
```
1. User submits username + password on React Login page
2. React calls POST /accounts/login/ with JSON body
3. Django LoginAPIView authenticates credentials
4. Returns { message, user: {...}, tokens: { access, refresh } }
5. React stores tokens + user in localStorage
6. AuthContext updates state → ProtectedRoute grants access
7. All subsequent API calls include Authorization: Bearer <access_token>
```

### Token Refresh Flow
```
1. API call returns 401 Unauthorized
2. Axios interceptor catches the error
3. Sends POST /accounts/token/refresh/ with refresh token
4. Receives new access token (+ rotated refresh token)
5. Retries the original failed request with new token
6. If refresh fails → clears localStorage → redirects to /login
```

### Guest Login Flow
```
1. User clicks "Guest Login" button
2. React calls POST /accounts/guest-login/
3. GuestLoginAPIView reads GUEST_USERNAME + GUEST_PASSWORD from env vars
4. Creates guest user if not exists, then authenticates
5. Returns same response format as regular login
```

---

## 9. Key Fixes During Refactor

### 1. Vite Proxy Conflict (Critical)

**Problem:** The Vite dev server was configured with a proxy that forwarded browser navigation requests (e.g., `/businesses`, `/accounts`) to Django, which returned JSON instead of letting React Router handle client-side routing.

**Fix:** Removed all proxy configuration from `vite.config.js`. Set the Axios `baseURL` directly to `http://localhost:8000`. CORS handles cross-origin requests.

### 2. NoReverseMatch Errors

**Problem:** After removing template-based URL routes, Django templates (still referenced in some views) threw `NoReverseMatch` errors for removed route names.

**Fix:** Went fully API-only — removed all template rendering. Root URL serves Swagger UI.

### 3. 406 Not Acceptable Errors

**Problem:** DRF returned 406 errors when browsable API renderer was not configured and browser sent `Accept: text/html`.

**Fix:** Ensured `DEFAULT_RENDERER_CLASSES` includes both `JSONRenderer` and `BrowsableAPIRenderer`.

### 4. Admin Panel Link in React SPA

**Problem:** The sidebar "Admin Panel" link used a relative path (`/admin/`), which React Router intercepted and redirected to `/` (catch-all route) instead of navigating to Django's admin.

**Fix:** Changed the link to an absolute URL (`http://localhost:8000/admin/`) with `target="_blank"` and `rel="noopener noreferrer"` so it opens the Django admin in a new tab.

### 5. Admin Panel Broken CSS (Static Files 404)

**Problem:** Django was running via **Gunicorn in Docker**, which does not serve static files (unlike `runserver`). All `/static/` requests returned 404, leaving the admin panel unstyled.

**Fix:**
1. Added **WhiteNoise** (`whitenoise==6.9.0`) to `requirements.txt`
2. Added `whitenoise.middleware.WhiteNoiseMiddleware` right after `SecurityMiddleware`
3. Set `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
4. Added `RUN python manage.py collectstatic --noinput` to the Dockerfile
5. Fixed `STATIC_URL` from `'static/'` (relative) to `'/static/'` (absolute)

---

## 10. Known Remaining Items

### Dead Code Cleanup

The following view files still contain **legacy HTML-based class-based views** that are no longer routed. They can be safely removed:

| File | Dead Code |
|------|-----------|
| `accounts/views.py` | `AccountListView`, `AccountDetailView`, `CustomLoginView`, `CustomLogoutView`, `GuestLoginView`, `RegisterView` |
| `businesses/views.py` | `BusinessListView`, `BusinessDetailView`, `BusinessCreateView`, `BusinessUpdateView`, `BusinessDeleteView` |
| `billings/views.py` | `InvoiceListView`, `InvoiceDetailView`, `InvoiceCreateView`, `InvoiceUpdateView`, `InvoiceDeleteView` |
| `config/views.py` | `index()` function view |

### Test File Updates

`test/test_accounts.py` still tests the old HTML form-based login flow:
- Uses `self.client.post('/accounts/login/', {...})` (Django test client)
- Asserts on `response.context['user']` (template context — doesn't exist in API responses)
- Checks for `'Log out'` text in HTML (no HTML is returned now)
- Checks for `"Please enter a correct username and password."` error message

These tests need to be rewritten to use DRF's `APIClient` and assert on JSON responses:
```python
# Example of what the updated test should look like:
def test_guest_login_api_success(self):
    User.objects.create_user(username='mockguest', password='mockpassword')
    response = self.api_client.post('/accounts/guest-login/', format='json')
    self.assertEqual(response.status_code, 200)
    self.assertIn('tokens', response.data)
    self.assertIn('access', response.data['tokens'])
    self.assertEqual(response.data['user']['username'], 'mockguest')
```

### Template Files

The Django HTML templates in `templates/` and app-level `templates/` directories are no longer used by any routed views. They can be archived or removed:
- `templates/base.html`, `templates/index.html`
- `accounts/templates/accounts/`
- `businesses/templates/businesses/`
- `billings/templates/billings/`

---

## Summary of Changes

| Category | Before | After |
|----------|--------|-------|
| **Views** | Django CBVs (ListView, CreateView, etc.) | DRF APIView / generics (ListCreateAPIView, etc.) |
| **Responses** | Server-rendered HTML | JSON |
| **Authentication** | Django sessions + `LoginView` | SimpleJWT (access + refresh tokens) |
| **Frontend** | Django templates + Tailwind | React SPA (Vite + React 19 + Tailwind v4) |
| **Root URL** | Dashboard HTML page | Swagger UI (OpenAPI docs) |
| **Form validation** | Django forms (server-side) | DRF serializer validation (server) + React form handling (client) |
| **CSRF** | `{% csrf_token %}` in templates | Not needed — JWT auth via `Authorization` header |
| **API documentation** | None | drf-spectacular (OpenAPI 3.0 + Swagger UI) |
| **State management** | Django sessions | React Context + localStorage |
| **Routing** | Server-side (Django URL dispatcher) | Client-side (React Router) + Server-side (DRF for API) |
| **Static files** | Django `runserver` auto-serve | WhiteNoise via Gunicorn (production-ready) |
