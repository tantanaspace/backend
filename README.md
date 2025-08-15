# Tantana Backend

A Django-based backend application with user authentication and management.

## API Endpoints

### User Authentication

#### 1. Simple Login
**Endpoint:** `POST /api/v1/users/login/`

**Request Body:**
```json
{
    "phone_number": "+998901234567",
    "password": "your_password"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "phone_number": "+998901234567",
        "full_name": "John Doe",
        "username": "john_doe"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### 2. Check User Exists
**Endpoint:** `POST /api/v1/users/check-user/`

**Request Body:**
```json
{
    "phone_number": "+998901234567"
}
```

**Response:**
```json
{
    "success": true,
    "exists": true,
    "phone_number": "+998901234567"
}
```

**If user doesn't exist:**
```json
{
    "success": true,
    "exists": false,
    "phone_number": "+998901234567"
}
```

#### 3. User Registration
**Endpoint:** `POST /api/v1/users/register/`

**Prerequisites:** Phone number must be verified with OTP first using `send-otp/` and `verify-otp/` endpoints.

**Request Body:**
```json
{
    "phone_number": "+998901234567",
    "password": "your_password",
    "password2": "your_password",
    "full_name": "John Doe",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "language": "en",
    "session": "session_from_otp_verification"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "phone_number": "+998901234567",
        "full_name": "John Doe",
        "username": null,
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "language": "en"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### 4. Forgot Password
**Step 1: Send OTP**
**Endpoint:** `POST /api/v1/users/send-otp/` (uses existing OTP endpoint)

**Request Body:**
```json
{
    "type": "forgot_password",
    "phone_number": "+998901234567"
}
```

**Response:**
```json
{
    "type": "forgot_password",
    "phone_number": "+998901234567",
    "session": "uuid-session-string"
}
```

**Step 2: Verify OTP**
**Endpoint:** `POST /api/v1/users/verify-otp/` (uses existing OTP endpoint)

**Request Body:**
```json
{
    "type": "forgot_password",
    "phone_number": "+998901234567",
    "session": "uuid-session-string",
    "otp_code": "123456"
}
```

**Response:**
```json
{
    "type": "forgot_password",
    "phone_number": "+998901234567",
    "session": "uuid-session-string",
    "otp_code": "123456"
}
```

**Step 3: Reset Password**
**Endpoint:** `POST /api/v1/users/forgot-password/reset/`

**Request Body:**
```json
{
    "phone_number": "+998901234567",
    "password": "new_password",
    "password2": "new_password",
    "session": "uuid-session-string"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Password reset successfully",
    "user": {
        "id": 1,
        "phone_number": "+998901234567",
        "full_name": "John Doe"
    }
}
```

### Other Endpoints

- `POST /api/v1/users/send-otp/` - Send OTP via SMS
- `POST /api/v1/users/verify-otp/` - Verify OTP code
- `POST /api/v1/users/register/` - User registration with OTP verification
- `POST /api/v1/users/forgot-password/reset/` - Reset password after OTP verification
- `POST /api/v1/users/login/check/` - Login check endpoint
- `POST /api/v1/users/login/password/` - Password login endpoint
- `POST /api/v1/users/login/otp/` - OTP login endpoint
- `POST /api/v1/users/login/set-password/` - Set password endpoint

## Authentication

The application uses JWT (JSON Web Tokens) for authentication. After successful login, you'll receive:
- **Access Token**: Valid for 60 minutes, use in Authorization header as `Bearer <token>`
- **Refresh Token**: Valid for 1 day, use to get new access tokens

## Registration Flow

1. **Send OTP**: Use `POST /api/v1/users/send-otp/` with `type: "auth"` to send OTP to phone number
2. **Verify OTP**: Use `POST /api/v1/users/verify-otp/` with the OTP code and session
3. **Register User**: Use `POST /api/v1/users/register/` with the verified phone number and session

## Forgot Password Flow

1. **Send OTP**: Use `POST /api/v1/users/send-otp/` with `type: "forgot_password"` to send OTP for password reset
2. **Verify OTP**: Use `POST /api/v1/users/verify-otp/` with `type: "forgot_password"` to verify OTP
3. **Reset Password**: Use `POST /api/v1/users/forgot-password/reset/` with the verified phone number and session

## Setup

1. Install dependencies:
```bash
pip install -r requirements/develop.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser:
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file with the following variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to True for development
- `DB_ENGINE` - Database engine (e.g., django.db.backends.postgresql)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `REDIS_URL` - Redis connection URL
- `AES_KEY` - AES encryption key
- `RECAPTCHA_PUBLIC_KEY` - Google reCAPTCHA public key
- `RECAPTCHA_PRIVATE_KEY` - Google reCAPTCHA private key
