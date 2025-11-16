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

## Testing

Test API endpoints using Postman, curl, or Django REST Framework's localhost server.

localhost:8000/admin/
localhost:8000/api


curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "Pierrot", "password": "theboss0"}'