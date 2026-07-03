                      MENUQR - DIGITAL MENU MANAGEMENT SYSTEM

A full-stack application for creating and managing digital restaurant menus 
with QR codes.

Backend: Django REST API  |  Frontend: React + Vite
Tests: 171 Passing  |  UI: Persian


                                QUICK START

BACKEND (Django API):
  cd backend/
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver
  -> API runs on http://localhost:8000/

FRONTEND (React):
  cd frontend/
  npm install
  npm run dev
  -> App runs on http://localhost:5173/

REDIS + CELERY:
  redis-server
  celery -A A worker -l info -B



                                FEATURES


AUTHENTICATION:
  - Custom User model (phone-based)
  - Password login (username or phone number)
  - OTP login with SMS verification
  - Registration with 2-step OTP verification
  - Token-based authentication
  - Profile management (username, phone change)
  - Rate-limited OTP resend (max 3 attempts)
  - Session cleanup utilities

MENU MANAGEMENT:
  - Full CRUD for menus
  - Bulk item creation
  - Category system for items
  - QR code auto-generation on menu creation
  - QR code download (PNG format)
  - Public menu endpoint (no auth required for QR scanning)
  - Toggle menu/item availability
  - Menu preview before publishing

SECURITY:
  - Timing attack protection on OTP endpoints
  - Rate limiting on OTP requests
  - Token authentication for all protected endpoints
  - Session management with Redis
  - Input validation at model, serializer, and view levels
  - Proper HTTP status codes

BACKGROUND TASKS:
  - Celery for async OTP cleanup
  - Redis as message broker and cache
  - Automatic expired OTP deletion every 2 minutes



                            PROJECT STRUCTURE

backend/
├── A/                          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── accounts/                   # Authentication app
│   ├── models.py               # Custom User, OTPCode
│   ├── managers.py             # Custom UserManager
│   ├── serializers.py
│   ├── views.py
│   ├── authentication.py       # Password auth backend
│   ├── otp_authentication.py   # OTP auth backend
│   ├── admin.py
│   ├── urls.py
│   └── tests/                  # 133 tests
├── menu/                       # Menu management app
│   ├── models.py               # QRMenu, MenuItem, Category
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   └── tests/                  # 38 tests
├── utils/
│   └── otp_service.py          # OTP generation & verification
├── media/                      # User uploads (QR codes)
├── manage.py
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── auth/               # Login, Register, OTP, ResendOTP
│   │   ├── menu/               # MenuList, MenuCreate, MenuDetail,
│   │   │                       # AddItems, EditItem, PublicMenu
│   │   ├── profile/            # Profile, ChangeUsername, ChangePhone
│   │   ├── Welcome.jsx         # Landing page
│   │   ├── Dashboard.jsx       # User dashboard
│   │   └── Navbar.jsx          # Navigation bar
│   ├── services/
│   │   └── api/                # API service layer (auth, menu, profile)
│   ├── App.jsx
│   └── main.jsx
├── public/
├── package.json
└── .env



                              API ENDPOINTS


AUTHENTICATION:
  POST   /accounts/register/                          [No Auth]
  POST   /accounts/verify/                            [No Auth]
  POST   /accounts/login/password/                    [No Auth]
  POST   /accounts/login/otp/send/                    [No Auth]
  POST   /accounts/login/otp/verify/                  [No Auth]
  POST   /accounts/otp/resend/                        [No Auth]
  POST   /accounts/logout/                            [Token]
  GET    /accounts/profile/                           [Token]
  PUT    /accounts/profile/username/                  [Token]
  POST   /accounts/profile/change_number/             [Token]
  POST   /accounts/profile/change_number/confirm/     [Token]
  POST   /accounts/profile/change_number/cancel/      [Token]

MENU MANAGEMENT:
  GET    /menu/                                       [Token]
  POST   /menu/create/                                [Token]
  GET    /menu/{id}/                                  [Token]
  PUT    /menu/{id}/                                  [Token]
  DELETE /menu/{id}/                                  [Token]
  POST   /menu/{id}/items/                            [Token]
  PUT    /menu/{id}/items/{item_id}/                  [Token]
  DELETE /menu/{id}/items/{item_id}/                  [Token]
  GET    /menu/public/{id}/                           [No Auth]



                                  TESTING


  cd backend/
  python manage.py test
  python manage.py test -v 2

  # Specific modules:
  python manage.py test accounts.tests.test_models
  python manage.py test accounts.tests.test_views
  python manage.py test menu.tests



                          ENVIRONMENT VARIABLES


BACKEND (.env):
  DEBUG=True
  SECRET_KEY=your-secret-key
  DATABASE_URL=sqlite:///db.sqlite3
  REDIS_URL=redis://localhost:6379/0
  ALLOWED_HOSTS=localhost,127.0.0.1

FRONTEND (.env):
  VITE_API_URL=http://localhost:8000



                              DOCKER (OPTIONAL)


  docker-compose up --build
  docker-compose exec web python manage.py migrate
  docker-compose exec web python manage.py createsuperuser



                              TECH STACK


  Django 6.0              Backend framework
  Django REST Framework   API framework
  React 19                Frontend framework
  Vite                    Build tool
  PostgreSQL/SQLite       Database
  Redis                   Cache + Celery broker
  Celery                  Background tasks
  Pillow                  Image processing
  qrcode                  QR code generation



                          AUTHENTICATION FLOW


  1. Register: Send phone -> Get OTP -> Verify -> Get token
  2. Login (Password): Send identifier + password -> Get token
  3. Login (OTP): Send phone -> Get OTP -> Verify -> Get token
  4. Auth Requests: Include "Authorization: Token <token>" header



                            FRONTEND PAGES


  Landing           Hero section, features, CTA
  Login             Password login form
  OTP Login         Phone verification login
  Register          2-step registration with OTP
  Dashboard         Welcome message, quick actions, guide
  Profile           View user information
  Change Username   Update username form
  Change Phone      2-step phone number change
  Menu List         All user menus with actions
  Menu Create       New menu with optional items
  Menu Detail       View menu, QR code, items
  Add Items         Bulk item addition form
  Edit Item         Update single item form
  Public Menu       Customer QR code view
  Preview           Owner preview of public menu



                                LICENSE


  This project is built for educational and portfolio purposes.



                                AUTHOR


  Built with Django REST Framework + React

