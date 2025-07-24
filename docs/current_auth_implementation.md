# Current Authentication System Documentation

## Overview
The current authentication system implements a traditional username/password-based authentication using Flask-Login for session management. The system supports user registration, login, and logout functionality with password hashing for security.

## Features

### User Registration
- Supports creation of new user accounts
- Collects username, email, and password
- Performs duplicate checks for username and email
- Securely hashes passwords before storage
- Provides feedback through flash messages

### Login System
- Username and password authentication
- "Remember me" functionality for persistent sessions
- Invalid credential handling with user feedback
- Automatic redirection to home page after successful login
- Session management using Flask-Login

### Security Features
- Password hashing (implementation in User model)
- Protected routes using `@login_required` decorator
- Session-based authentication
- CSRF protection (via Flask-WTF)
- Automatic redirect of authenticated users from login/register pages

## API Routes

### Authentication Routes

#### Login Route (`/login`)
- **Methods**: GET, POST
- **Path**: `/login`
- **Authentication**: Public
- **Functionality**:
  - GET: Renders login form
  - POST: Processes login attempts
- **Form Fields**:
  - Username
  - Password
  - Remember Me (optional)
- **Responses**:
  - Success: Redirect to home page
  - Failure: Flash message with error

#### Registration Route (`/register`)
- **Methods**: GET, POST
- **Path**: `/register`
- **Authentication**: Public
- **Functionality**:
  - GET: Renders registration form
  - POST: Creates new user account
- **Form Fields**:
  - Username
  - Email
  - Password
- **Validation**:
  - Unique username check
  - Unique email check
- **Responses**:
  - Success: Redirect to login page
  - Failure: Flash message with specific error

#### Logout Route (`/logout`)
- **Methods**: GET
- **Path**: `/logout`
- **Authentication**: Required
- **Functionality**: Terminates user session
- **Response**: Redirects to login page

### Protected Routes

#### Home Route (`/`)
- **Methods**: GET
- **Authentication**: Required
- **Functionality**: Displays user dashboard
- **Data**: Lists all users

#### Users API Routes
- **GET `/users`**: List all users (authenticated)
- **POST `/users`**: Create new user (authenticated)
- **GET `/users/<user_id>`**: Get specific user details (authenticated)

## Database Schema

### User Model
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL
);
```

## Security Considerations

### Password Security
- Passwords are never stored in plain text
- Uses secure hashing algorithm (implementation in User.set_password())
- Password verification through User.check_password()

### Session Security
- Flask-Login manages user sessions
- Remember-me functionality for extended sessions
- Protected routes enforce authentication
- Automatic session management

### Data Validation
- Username uniqueness enforced
- Email uniqueness enforced
- Required field validation
- Form data sanitization

## Dependencies
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Werkzeug Security

## Limitations
1. No password strength requirements
2. No rate limiting on login attempts
3. No multi-factor authentication
4. No password reset functionality
5. No account lockout after failed attempts
6. No session timeout configuration
7. No IP-based security measures

## Recommended Improvements
1. Implement password strength requirements
2. Add rate limiting for login attempts
3. Add password reset functionality
4. Implement account lockout after failed attempts
5. Add IP-based rate limiting
6. Add session timeout settings
7. Implement security logging
8. Add email verification for new registrations

## Usage Examples

### Registration Flow
```python
# Example registration request
POST /register
Content-Type: application/x-www-form-urlencoded

username=newuser&email=user@example.com&password=secretpass
```

### Login Flow
```python
# Example login request
POST /login
Content-Type: application/x-www-form-urlencoded

username=existinguser&password=userpass&remember=on
```

## Error Handling
- Invalid credentials: Flash message + redirect
- Duplicate username: Flash message + redirect
- Duplicate email: Flash message + redirect
- Missing required fields: Form validation errors
- Unauthorized access: Redirect to login page 