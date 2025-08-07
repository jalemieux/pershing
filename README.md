# Pershing - LLM Tools Portal

A Flask-based portal that provides access to various LLM-based tools and services.

## Features

- **Intent Analysis**: Analyze user messages to understand their intent, extract entities, and determine the best response
- **Prompt Crafting**: Transform your ideas into effective prompts with AI assistance and generate multiple prompt variations
- **AI Chat**: Chat with AI assistants, upload files for analysis, and have intelligent conversations
- **Buddies**: Create and chat with custom AI assistants. Each buddy has its own personality, tools, and memory

## User Management

### Authentication Flow
New users or those with expired sessions will be redirected to a login flow that validates their email.



### Assigning Admin Role

To assign admin privileges to an existing user:

```bash
python assign_admin.py <user_email>
```

Example:
```bash
python assign_admin.py user@example.com
```
This will grant this user access to the admin dashboard.

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment configuration:
- Copy `env.development.example` to create environment-specific files:
  ```bash
  cp env.development.example env.development  # For development
  cp env.production.example env.production   # For production
  ```
- Edit each file with appropriate values for that environment
- Set FLASK_ENV to control which configuration is loaded:
  ```bash
  export FLASK_ENV=development  # For development (default)
  export FLASK_ENV=production  # For production
  ```

4. Set up the database:
- Create a PostgreSQL database
- Run the migration scripts in `migrations/` to create the required tables


5. Start the application:
```bash
python app.py
```


## Development

The application runs in debug mode by default. All routes except login and register require authentication. Admin routes require additional admin privileges.

