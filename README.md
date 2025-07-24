# Pershing - LLM Tools Portal

A Flask-based portal that provides authenticated users access to various LLM-based tools and services.

## Features

- User authentication and registration
- Secure login system with session management
- Protected routes for authenticated users
- **Admin-only dashboard access**
- **Role-based access control**
- Ready for LLM tool integration

## Admin Functionality

The application now includes role-based access control:

- **Admin Users**: Have access to the dashboard and all administrative features
- **Regular Users**: Have access to basic features but cannot access the dashboard
- Dashboard is hidden from non-admin users in the navigation
- Admin routes are protected with `@admin_required` decorator

### Creating Admin Users

Use the provided script to create admin users:

```bash
python create_admin.py
```

This creates an admin user with:
- Email: `admin@example.com`
- Username: `admin`
- Password: `admin123`

### Creating Regular Users

Use the provided script to create regular users:

```bash
python create_user.py
```

This creates a regular user with:
- Email: `user@example.com`
- Username: `user`
- Password: `user123`

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment configuration:
- Copy `.env.example` to create environment-specific files:
  ```bash
  cp .env.example .env.development  # For development
  cp .env.example .env.testing      # For testing
  cp .env.example .env.production   # For production
  ```
- Edit each file with appropriate values for that environment
- Set FLASK_ENV to control which configuration is loaded:
  ```bash
  export FLASK_ENV=development  # For development (default)
  export FLASK_ENV=testing     # For testing
  export FLASK_ENV=production  # For production
  ```

4. Set up PostgreSQL:
- Make sure PostgreSQL is installed and running
- Create databases for each environment:
  ```bash
  createdb flask_app_dev      # For development
  createdb flask_app_test     # For testing
  createdb flask_app_prod     # For production
  ```
- Update the DATABASE_URL in each .env file if needed

5. Initialize the database:
```bash
python app.py
```

6. Create test users (optional):
```bash
python create_admin.py  # Creates admin user
python create_user.py   # Creates regular user
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Register a new account at `/register` or use the test accounts:
   - **Admin**: `admin@example.com` / `admin123`
   - **Regular User**: `user@example.com` / `user123`

3. Login at `/login`

4. Access the portal:
   - **Admin users**: Can access dashboard at `/dashboard`
   - **Regular users**: Can access home page at `/` and other features

## Access Control

### Admin-Only Routes
- `/dashboard` - User dashboard with session management and statistics

### Protected Routes (All Authenticated Users)
- `/` - Home page
- `/intent-collection` - Intent collection feature
- `/logout` - Logout functionality

### Public Routes
- `/login` - Login page
- `/register` - Registration page

## Development

The application runs in debug mode by default. All routes except login and register require authentication. Admin routes require additional admin privileges.

### Database Schema Updates

The User model has been updated to include:
- `is_admin` field (Boolean, default: False)
- Admin status is included in user serialization

### Security Features

- Role-based access control with `@admin_required` decorator
- Dashboard access restricted to admin users only
- Navigation automatically hides dashboard link for non-admin users
- Flash messages for access denied scenarios 