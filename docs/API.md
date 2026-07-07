# Spending Tracker API Documentation

## Overview

This document describes the REST API used by the Spending Tracker application.

Base URL (Development)

```
http://localhost:8000/api/v1
```

Base URL (Production)

```
https://your-api-domain.com/api/v1
```

---

# Authentication

Authentication uses JSON Web Tokens (JWT).

Protected endpoints require:

```
Authorization: Bearer <access_token>
```

---

# API Modules

## Authentication

Status: ✅ Implemented

Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /auth/register | Register a new user |
| POST | /auth/login | Login user |
| POST | /auth/refresh | Refresh access token |
| POST | /auth/logout | Logout user |

---

## Dashboard

Status: ✅ Implemented

Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /dashboard | Dashboard summary |
| GET | /dashboard/stats | Statistics |
| GET | /dashboard/recent | Recent transactions |

---

## Income

Status: ✅ Implemented

Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /income | List income |
| POST | /income | Create income |
| GET | /income/{id} | Get income |
| PUT | /income/{id} | Update income |
| DELETE | /income/{id} | Delete income |

---

## Expenses

Status: ⏳ Pending

---

## Budgets

Status: ⏳ Pending

---

## Savings Goals

Status: ⏳ Pending

---

## Reports

Status: ⏳ Pending

---

## Notifications

Status: ⏳ Pending

---

## User Profile

Status: ⏳ Pending

---

# Standard Response Format

Successful Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

Error Response

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": []
}
```

---

# HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

# Authentication Flow

```
Register
    ↓
Login
    ↓
Access Token
    ↓
Protected APIs
    ↓
Refresh Token
    ↓
New Access Token
```

---

# Versioning

Current Version

```
v1
```

Future versions will follow semantic API versioning.

---

# OpenAPI

Interactive API documentation is available at:

```
/docs
```

ReDoc documentation:

```
/redoc
```

---

# Notes

- All timestamps use UTC.
- Monetary values use Decimal for precision.
- All protected resources are scoped to the authenticated user.
- Pagination, filtering, and sorting are supported where applicable.

---

# Changelog

## v1

- Authentication
- Dashboard
- Income

Pending:

- Expenses
- Budgets
- Savings Goals
- Reports
- Notifications
- User Profile