# SoftDesk Support

A REST API for issue tracking and project management built with Django REST Framework.

## Overview

SoftDesk Support is a collaborative issue tracking system that allows teams to manage projects, track issues, and facilitate communication through comments. The application supports GDPR compliance and implements JWT authentication.

### Core Features

- **User Management**: JWT authentication with GDPR-compliant privacy controls
- **Project Management**: Create and manage projects (back-end, front-end, iOS, Android)
- **Issue Tracking**: Create and track issues with priority levels, tags, and status
- **Collaboration**: Contributors can comment on issues and participate in projects
- **Privacy**: GDPR-compliant data handling with user consent management

### Data Models

- **User**: Age verification, privacy preferences, authentication
- **Contributor**: Links users to projects with specific permissions
- **Project**: Main resource for client applications with type classification
- **Issue**: Project-specific problems with priority, status, and assignment
- **Comment**: Issue-specific communication with UUID referencing

### Key Requirements

- Users must be 15+ for data collection (GDPR compliance)
- Only project contributors can access project resources
- Author-based permissions for resource modification
- Pagination for resource listings
- Comprehensive API testing with Postman

## Installation

### Prerequisites

- Python 3.8+
- Poetry

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Lywald/softdeskdjango.git
cd softdeskdjango
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Activate virtual environment:
```bash
poetry env activate
```

4. Run migrations:
```bash
poetry run python manage.py makemigrations users
poetry run python manage.py makemigrations projects
poetry run python manage.py migrate
```

5. Create superuser:
```bash
poetry run python manage.py createsuperuser 
```

6. Start development server:
```bash
poetry run python manage.py runserver
```

## Security Configuration

### SECRET_KEY - Important Notice

**WARNING**: This repository contains a development SECRET_KEY in `softdesksupport/settings.py`. This is ONLY safe for development and learning purposes.

**For Production Deployment**, you MUST:

1. **Generate a new SECRET_KEY**:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

2. **Create a `.env` file** in the project root:
   ```bash
   SECRET_KEY=your-new-generated-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

3. **Install python-decouple**:
   ```bash
   poetry add python-decouple
   ```

4. **Update `settings.py`** to use environment variables:
   ```python
   from decouple import config

   SECRET_KEY = config('SECRET_KEY')
   DEBUG = config('DEBUG', default=False, cast=bool)
   ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
   ```

5. **Add `.env` to `.gitignore`** (already done in this project)

### Why This Matters

- The SECRET_KEY is used to sign JWT tokens and session data
- If exposed, attackers could forge authentication tokens
- The current key is prefixed with "django-insecure-" indicating it's for development only
- Never commit production secrets to version control

## API Testing

### Prerequisites for Testing

Before testing the API, make sure you have created a superuser (if not already done):

```bash
poetry run python manage.py createsuperuser
# Example: username: admin, password: admin123
```

### Using Postman (Recommended)

This project includes a comprehensive Postman collection for testing all API endpoints.

**Collection File**: `Softdesk API - Projects, Contributors, Issues, Comments.postman_collection.json`

#### Download Postman
[Get Postman](https://www.postman.com/downloads/)

#### Import the Collection
1. Open Postman
2. Click "Import" in the top left
3. Select the file: `Softdesk API - Projects, Contributors, Issues, Comments.postman_collection.json`
4. The collection will appear in your Collections sidebar

#### What's Included
- JWT authentication (token generation and refresh)
- Projects CRUD operations
- Contributors management
- Issues tracking
- Comments functionality
- Permission-based access control tests

### API Endpoints

```
Admin Panel:     http://localhost:8000/admin/
API Root:        http://localhost:8000/api/
JWT Token:       http://localhost:8000/api/token/
Token Refresh:   http://localhost:8000/api/token/refresh/
```

### Getting Your JWT Token

Use the credentials you created during superuser setup:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Replace `admin` and `admin123` with your actual superuser credentials.

This request will return a JSON response with an `access` token and a `refresh` token:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Configure Postman with Your Token

1. Copy the `access` token from the response
2. In Postman, go to your collection settings:
   - Right-click the "Softdesk API" collection
   - Select "Edit"
   - Go to the "Authorization" tab
   - Type: Select "Bearer Token"
   - Token: Paste your `access` token
3. All requests in the collection will now use this token automatically