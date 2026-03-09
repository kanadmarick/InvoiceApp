# Postman Collection for Django Invoices API

This directory contains Postman collection and environment files for testing the Django Invoices application.

## Files

- **Invoices_API.postman_collection.json** - Complete API collection with all endpoints
- **Invoices_API.postman_environment.json** - Environment variables for local development

## Setup Instructions

### 1. Import into Postman

1. Open Postman desktop app or web version
2. Click **Import** button in the top left
3. Drag and drop both JSON files or browse to select them
4. Click **Import** to add them to your workspace

### 2. Select Environment

After importing:
1. Click the environment dropdown in the top right (shows "No Environment")
2. Select **Django Invoices - Local**

### 3. Configure Environment Variables

Update these variables in the environment:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `base_url` | Base URL of your Django server | `http://localhost:8000` |
| `username` | Test user username | `testuser` |
| `password` | Test user password | `testpass123` |
| `business_id` | UUID of a business (filled after creating) | (empty) |
| `invoice_id` | UUID of an invoice (filled after creating) | (empty) |
| `jwt_token` | JWT access token (auto-filled after login) | (empty) |
| `csrf_token` | CSRF token for form submissions | (empty) |

### 4. Authentication

Before testing other endpoints:

1. **Start your Django development server:**
   ```bash
   python manage.py runserver
   ```

2. **Create a test user** (if not already created):
   ```bash
   python manage.py createsuperuser
   # Or use guest login endpoint (see below)
   ```

3. **Quick Start - Guest Login (Easiest):**
   - Run **Authentication > Guest Login** (simple GET request)
   - No CSRF token needed!
   - Automatically logs you in as demo user

4. **Alternative - Regular Login:**
   - First run **Authentication > Get CSRF Token**
   - Then run **Authentication > Login** with username/password
   - Cookie-based auth: Postman will automatically save session cookies

### 5. Testing Workflow

Recommended test order:

1. **Authentication > Guest Login** - Quick one-click authentication (GET request)
2. **Authentication > Get CSRF Token** - Get token for POST/PUT/DELETE requests
3. **Businesses > Create Business** - Create a business record
3. Copy the UUID from the response/URL and paste into `business_id` environment variable
4. **Businesses > Get Business Detail** - Test with the UUID
5. **Invoices > Create Invoice** - Create an invoice
6. Copy invoice UUID to `invoice_id` environment variable
7. **Invoices > Get Invoice Detail** - Test invoice retrieval
8. Run other CRUD operations as needed

## Collection Structure

### Authentication
- **Get CSRF Token (GET)** - Obtains CSRF token for POST requests
- **Login (POST)** - Username/password authentication (requires CSRF token)
- **Guest Login (GET)** - One-click demo login (no CSRF needed!)
- **Register (POST)** - New user registration (requires CSRF token)
- **Logout (POST)** - End user session

### Businesses
- List Businesses (GET) - View all businesses
- Create Business (POST) - Add new business
- Get Business Detail (GET) - View single business by UUID
- Update Business (POST) - Edit business details
- Delete Business (POST) - Remove business

### Invoices
- List Invoices (GET) - View all invoices
- Create Invoice (POST) - Generate new invoice
- Get Invoice Detail (GET) - View single invoice by UUID
- Update Invoice (POST) - Edit invoice
- Delete Invoice (POST) - Remove invoice

### General
- Home (GET) - Dashboard/homepage
- Accounts List (GET) - User account list (admin)

## Testing Features

### Pre-request Scripts
The collection includes global pre-request scripts that:
- Generate dynamic timestamps
- Create random UUIDs for testing

### Test Scripts
Individual requests include test scripts that verify:
- Status codes (200, 201, 302)
- Response times
- Authentication state (cookies/tokens)
- Response structure

### Test Assertions
Tests use Chai assertion library:
```javascript
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});
```

## Running Tests

### Single Request
Click **Send** on any request to execute it

### Folder/Collection
1. Click the (...) menu next to a folder or the collection
2. Select **Run folder** or **Run collection**
3. Configure run settings
4. Click **Run [Name]**

### Newman (CLI)
Run tests from command line:

```bash
# Install Newman
npm install -g newman

# Run collection
newman run Invoices_API.postman_collection.json \
  -e Invoices_API.postman_environment.json

# Run with detailed output
newman run Invoices_API.postman_collection.json \
  -e Invoices_API.postman_environment.json \
  --reporters cli,json
```

## Production Environment

To test against production:

1. Duplicate the environment (right-click > Duplicate)
2. Rename to "Django Invoices - Production"
3. Update `base_url` to your production URL
4. Update credentials as needed
5. Switch to the production environment before testing

## CSRF Token Handling

Django requires CSRF tokens for POST requests. The collection handles this automatically through:
- Session cookies (for authenticated requests)
- Forms include CSRF token in urlencoded body

If you encounter CSRF errors:
1. Make sure cookies are enabled in Postman
2. Run a GET request first to obtain CSRF cookie
3. Ensure session authentication is working

## JWT Authentication (API Endpoints)

If your app has REST API endpoints using JWT:

1. Add JWT token endpoint to collection
2. Extract token from response
3. Set as environment variable:
   ```javascript
   pm.environment.set('jwt_token', responseJson.access);
   ```
4. Use in Authorization header:
   ```
   Authorization: Bearer {{jwt_token}}
   ```

## Troubleshooting

### 403 Forbidden
- Check CSRF token handling
- Verify authentication state
- Ensure user has required permissions

### 404 Not Found
- Verify `base_url` is correct
- Check server is running
- Confirm endpoint URLs match Django routes

### Connection Refused
- Start Django development server
- Check port number (default 8000)
- Verify firewall settings

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Postman Learning Center](https://learning.postman.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## Notes

- All UUID parameters use the format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Dates should be in `YYYY-MM-DD` format
- This collection assumes Django's default session-based authentication
- Update request bodies to match your specific model fields
