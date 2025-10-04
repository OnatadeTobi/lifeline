# Lifeline Blood Donation API

Backend API for connecting blood donors with urgent requests.

## Tech Stack
- Django 4.2
- Django REST Framework
- PostgreSQL
- JWT Authentication

## Quick Start (Development)

### 1. Clone & Setup
\`\`\`bash
git clone <repo-url>
cd lifeline_backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

### 2. Environment Variables
Copy `.env.example` to `.env` and configure.

### 3. Database Setup
\`\`\`bash
python manage.py migrate
python manage.py loaddata fixtures/lagos_locations.json
python manage.py createsuperuser
\`\`\`

### 4. Run Server
\`\`\`bash
python manage.py runserver
\`\`\`

### 5. API Documentation
Visit http://localhost:8000/api/docs/

## API Endpoints

### Authentication
- POST `/api/v1/auth/login/` - Login (get JWT)
- POST `/api/v1/auth/token/refresh/` - Refresh token

### Donors
- POST `/api/v1/donors/register/` - Register donor
- GET `/api/v1/donors/profile/` - Get profile
- PATCH `/api/v1/donors/profile/` - Update profile
- POST `/api/v1/donors/toggle-availability/` - Toggle availability

### Hospitals
- POST `/api/v1/hospitals/register/` - Register hospital
- GET `/api/v1/hospitals/profile/` - Get profile

### Blood Requests
- POST `/api/v1/requests/create/` - Create request (Hospital)
- GET `/api/v1/requests/` - List requests
- POST `/api/v1/requests/{id}/accept/` - Accept request (Donor)
- POST `/api/v1/requests/{id}/fulfill/` - Mark fulfilled (Hospital)

### Locations
- GET `/api/v1/locations/states/` - List states
- GET `/api/v1/locations/states/{id}/lgas/` - List LGAs

## Blood Type Compatibility
- O- : Universal donor (can donate to all)
- AB+ : Universal receiver (can receive from all)
- Full compatibility matrix implemented

## Deployment
See `docs/DEPLOYMENT.md` for production deployment guide.