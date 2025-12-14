# Accounts App README

## Overview

The Accounts app provides user management functionality for the Social Media App, including user registration, authentication, and profile management. It uses Django REST Framework for API endpoints and token-based authentication.

## User Model

The custom `User` model extends Django's `AbstractUser` and includes the following additional fields:

- `bio`: A text field for the user's biography (optional)
- `profile_picture`: An image field for the user's profile picture (optional, uploaded to 'profiles/' directory)
- `followers`: A many-to-many relationship to track user followers (symmetrical=False for directed following)

The model also includes a signal that automatically creates an authentication token when a new user is created.

## Setup Process

1. **Install Dependencies**:
   Ensure you have Django and Django REST Framework installed. If using a virtual environment, activate it first:
   ```
   pip install django djangorestframework
   ```

2. **Database Migration**:
   Run the following commands to create and apply database migrations:
   ```
   python manage.py makemigrations accounts
   python manage.py migrate
   ```

3. **Create Superuser** (optional, for admin access):
   ```
   python manage.py createsuperuser
   ```

4. **Run the Development Server**:
   ```
   python manage.py runserver
   ```

## API Endpoints

### Registration
- **URL**: `/api/accounts/register`
- **Method**: POST
- **Data**: 
  ```json
  {
    "username": "exampleuser",
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**: User data with ID

### Authentication (Login)
- **URL**: `/api/accounts/login`
- **Method**: POST
- **Data**:
  ```json
  {
    "username": "exampleuser",
    "password": "securepassword"
  }
  ```
- **Response**:
  ```json
  {
    "token": "your-authentication-token"
  }
  ```

### Get Current User Profile
- **URL**: `/api/accounts/me`
- **Method**: GET
- **Headers**: `Authorization: Token your-authentication-token`
- **Response**: User profile data including followers and following counts

## Usage

1. Register a new user by sending a POST request to `/api/accounts/register`.
2. Login to obtain an authentication token via POST to `/api/accounts/login`.
3. Include the token in the `Authorization` header for authenticated requests: `Authorization: Token <token>`.
4. Access user profile information via GET to `/api/accounts/me`.

## Notes

- Authentication is token-based using Django REST Framework's TokenAuthentication.
- The app uses Django's built-in user model fields (username, email, password) plus the custom fields mentioned above.
- Profile pictures are uploaded to the 'profiles/' directory within MEDIA_ROOT.
