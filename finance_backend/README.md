# Finance Data Processing and Access Control Backend

## 1. Project Overview
This project provides a FastAPI backend for managing financial transactions with strict role-based access control. It supports authentication, user management, transaction CRUD with soft delete, and dashboard analytics.

## 2. Setup Instructions
1. Clone the repository and move into the project directory:
```bash
git clone <your-repo-url>
cd finance_backend
```
2. Create and activate a virtual environment (recommended).
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the API server:
```bash
uvicorn app.main:app --reload
```

## 3. Seed Data
Run:
```bash
python seed.py
```
This creates an initial admin user and 10 sample transactions if they do not already exist.

## 4. API Endpoints

### Auth
- `POST /api/auth/login` - Public - Login and receive JWT token.

### Users
- `GET /api/users/me` - Any authenticated role (`viewer`, `analyst`, `admin`)
- `GET /api/users` - `admin`
- `POST /api/users` - `admin`
- `PATCH /api/users/{id}` - `admin`
- `DELETE /api/users/{id}` - `admin` (deactivates user)

### Transactions
- `GET /api/transactions` - `analyst`, `admin`
- `POST /api/transactions` - `admin`
- `GET /api/transactions/{id}` - `analyst`, `admin`
- `PUT /api/transactions/{id}` - `admin`
- `DELETE /api/transactions/{id}` - `admin` (soft delete)

Query parameters for list endpoint:
- `category`
- `type` (`income` or `expense`)
- `from_date`
- `to_date`
- `page` (default `1`)
- `limit` (default `10`)

### Dashboard
- `GET /api/dashboard/summary` - Any authenticated role
- `GET /api/dashboard/by-category` - `analyst`, `admin`
- `GET /api/dashboard/trends` - `analyst`, `admin`
- `GET /api/dashboard/recent` - `analyst`, `admin`

## 5. Sample Requests

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@finance.local","password":"Admin@123"}'
```

### Create Transaction (admin)
```bash
curl -X POST http://127.0.0.1:8000/api/transactions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"amount":250.5,"type":"expense","category":"utilities","date":"2026-04-01","notes":"Water bill"}'
```

### Get Dashboard Summary
```bash
curl -X GET http://127.0.0.1:8000/api/dashboard/summary \
  -H "Authorization: Bearer <token>"
```

## 6. Assumptions Made
- All protected endpoints require a valid bearer token.
- `GET /api/dashboard/summary` is global summary data for all users (not user-specific transaction ownership filtering).
- User deactivation keeps the record but blocks further authentication.

## 7. Trade-offs Considered
- SQLite was chosen for simplicity and local development speed; PostgreSQL is preferred for production scale and concurrency.
- JWT auth is stateless and simple, but lacks built-in token revocation; production systems may require token blacklisting or shorter TTL with refresh tokens.
- Soft delete preserves audit history but requires query filtering discipline.
