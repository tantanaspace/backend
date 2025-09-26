# Tantana Backend

A Django-based backend application with user authentication and management.

## Setup

1. Clone the repository
2. Change directory to the root of the project
3. Create a virtual environment

   ```bash
   python -m venv .venv
   ```
4. Activate the virtual environment

   - Windows:

   ```
   venv\Scripts\activate
   ```

   - MacOs/Linux:

   ```bash
   source .venv/bin/activate
   ```
5. Install the requirements

   ```bash
   python -r requirements/base.txt
   python -r requirements/develop.txt
   ```
6. Migrate the Schema changes

   ```bash
   python manage.py migrate
   ```
7. Create admin user

   ```bash
   python manage.py createsuperuser
   ```

   and fill in your information
8. Run the server

   ```
   python manage.py runserver
   ```
9. Go to http://127.0.0.1:8000/admin/

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
