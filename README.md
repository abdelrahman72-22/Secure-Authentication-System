# Authentication System (Flask + SQLite)

Complete authentication system implementing:
- Registration with `name`, `email or username`, `password`, `role`
- Password hashing using `bcrypt`
- 2FA (TOTP) setup with QR code for authenticator apps
- JWT token-based authentication
- RBAC with exactly 3 roles: `Admin`, `Manager`, `User`
- Protected routes requiring token + role checks
- Required pages: register, login, 2FA verify, dashboard, profile, admin, manager, user

## Tech Stack
- Python 3.12+
- Flask
- SQLite
- bcrypt
- pyotp
- pyjwt
- qrcode

## Setup
1. Create and activate a virtual environment (already created in this workspace as `.venv`).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
```

4. Run the app:

```bash
python run.py
```

Server runs on `http://localhost:5000`.

## Flow
1. Open `/register`
2. Register user (`Admin` or `Manager` or `User`)
3. Scan QR code in Google/Microsoft Authenticator/Authy
4. Open `/login` and submit identifier + password
5. Open `/verify-2fa` and submit 6-digit code
6. Token is issued and stored client-side
7. Access protected pages/routes based on role

## API Endpoints
### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/verify-2fa`

### Protected (JWT required)
- `GET /api/dashboard` (any authenticated user)
- `GET /api/profile` (any authenticated user)
- `GET /api/admin` (Admin only)
- `GET /api/manager` (Manager only)
- `GET /api/user` (User only)

Use header:

```http
Authorization: Bearer <access_token>
```

## Project Structure
- `run.py` - app entry point
- `app/__init__.py` - Flask app factory
- `app/config.py` - configuration
- `app/db.py` - SQLite connection + schema init
- `app/user_model.py` - user data access
- `app/auth.py` - register/login/2FA APIs
- `app/security.py` - JWT + auth + role decorators
- `app/protected.py` - protected/RBAC APIs
- `app/pages.py` - page routes
- `app/templates/` - required pages
- `app/static/js/` - frontend flow scripts
- `app/static/css/styles.css` - styling
