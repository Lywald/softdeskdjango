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
python manage.py migrate
```

5. Create superuser:
```bash
poetry run python manage.py createsuperuser 
```

6. Start development server:
```bash
python manage.py runserver
```

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