from django.conf.global_settings import MIDDLEWARE

# SmoothGlue Django Core

# Overview

SmoothGlue Django Core provides a robust foundation for creating extendable and secure application features, optimized
for highly regulated environments. This project includes reusable Django apps designed to streamline development for
applications requiring stringent security and compliance measures.

## Key Features

- **Abstract Models:** Includes abstract models like `AuditModel` and `TimeAuditModel` for audit trail functionality in
  your models.
- **Reusable Serializers:** A set of base serializers for consistent API development.
- **Custom User Model:** Extensible user model adaptable to various authentication requirements.
- **Environment-specific Configuration:** Designed for easy configuration in different environments (development,
  staging, production).
- **Authentication Frameworks:** Authentication backends for JWT auth, and creating bootstrap superusers

## Installation

### Prerequisites

* Python 3.12+
* Django 4.2+
* Django REST Framework 3.15.2+

### Install SmoothGlue Django Core From PyPI (Official Use)

1. Use pip and the following command inside the Django project:

   ```bash
   pip install smoothglue_django_core
   ```

2. Enable Smoothglue Django Core's apps in your settings.py:

```python
INSTALLED_APPS = [
    # ... other installed apps ...
    'smoothglue.core',
    'smoothglue.authentication',
    'smoothglue.tracker',
    # ... other installed apps ...
]
```

3. **Database Migrations:**

Run the migrations to create the necessary database tables:

```bash
python manage.py migrate
```

4. **Optional: Enable bootstrap user:**

Update settings.py to enable the `RootAdminBackend`, and set the username and password

```python
AUTHENTICATION_BACKENDS = [
    # ...
    "smoothglue.authentication.auth.RootAdminBackend",
    # ...
]
ROOT_ADMIN_USERNAME = "my_admin_user"
ROOT_ADMIN_PASSWORD = "my_admin_password"
```

You will be able to authenticate with username `my_admin_user` and password `my_admin_password`.

5. **Optional: Enable JWT Authentication:**

Update settings.py to enable the JWT middleware. This allows users to authenticate with a JWT to all views.

```python
MIDDLEWARE = [
    # ...
    "smoothglue.authentication.auth.platform_authentication_middleware"
    # ...
]
```

6. Run the development server to confirm the project continues to work.

## API Usage

This package exposes several API endpoints to manage users, organizations, and other related data.

### Authentication

This package uses JWT-based authentication. The JWT is decoded from the Authorization or Jwt header of the request. In a
development environment, ENABLE_SINGLE_USER_MODE can be set to `True` to bypass JWT authentication and use a default "
UnknownUser".

### Endpoints

#### Users

- `GET /users/`: Retrieves a list of all users.

- `POST /users/`: Creates a new user.

- `GET /users/{id}/`: Retrieves a specific user by their ID.

- `PUT /users/{id}/`: Updates a specific user.

- `PATCH /users/{id}/`: Partially updates a user.

- `DELETE /users/{id}/`: Deletes a user.

#### Organizations

- `GET /organizations/`: Retrieves a list of all organizations.

- `POST /organizations/`: Creates a new organization.

- `GET /organizations/{id}/`: Retrieves a specific organization by its ID.

- `PUT /organizations/{id}/`: Updates an organization.

- `PATCH /organizations/{id}/`: Partially updates an organization.

- `DELETE /organizations/{id}/`: Deletes an organization.

#### Organization Members

- `GET /org-members/`: Retrieves a list of all organization members.

#### Organization Categories

- `GET /org-categories/`: Retrieves a list of all organization categories.

- `POST /org-categories/`: Creates a new organization category.

- `GET /org-categories/{id}/`: Retrieves a specific organization category by its ID.

- `PUT /org-categories/{id}/`: Updates an organization category.

- `PATCH /org-categories/{id}/`: Partially updates an organization category.

- `DELETE /org-categories/{id}/`: Deletes an organization category.

#### Active User

- `GET /active_user/`: Retrieves the currently authenticated user's information.

## License

This project is licensed under a Proprietary License. See the [LICENSE](./LICENSE) file for more details.
