# Spending Tracker Architecture

## Overview

The Spending Tracker is a production-grade full-stack web application built using a modular, scalable architecture.

The project is divided into independent layers to maximize maintainability, testability, and scalability.

---

# Technology Stack

## Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod
- Axios

---

## Backend

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT Authentication
- Repository Pattern
- Service Layer

---

## Database

- PostgreSQL

---

## Deployment

Frontend:
- Vercel

Backend:
- Render

Database:
- Supabase PostgreSQL

---

# Project Structure

```
spending-tracker/

backend/
frontend/
docs/
database/
.github/

README.md
LICENSE
docker-compose.yml
```

---

# Backend Architecture

```
API Layer
      │
      ▼
Service Layer
      │
      ▼
Repository Layer
      │
      ▼
Database
```

---

# Frontend Architecture

```
Pages

↓

Components

↓

Hooks

↓

API Client

↓

FastAPI Backend
```

---

# Authentication Flow

```
User Login

↓

JWT Access Token

↓

Protected API

↓

Refresh Token

↓

New Access Token
```

---

# AI Responsibilities

## Project Architect

- Architecture review
- Code review
- Integration review
- Technical decisions

---

## Claude

Responsible for:

- Backend
- Authentication
- APIs
- Database logic

---

## DeepSeek

Responsible for:

- Frontend
- Components
- State Management
- API Integration

---

## v0

Responsible for:

- UI Design
- UX
- Layout
- Design System

---

## Gemini

Responsible for:

- QA
- Testing
- Code Review
- Bug Detection

---

# Architectural Principles

- Clean Architecture
- SOLID
- Repository Pattern
- Service Layer
- Modular Design
- Feature-based Organization
- RESTful APIs
- Strong Typing
- Production-ready Code

---

# Development Workflow

1. Architect approves implementation.
2. Specialized AI generates module.
3. Module is reviewed.
4. Code is integrated.
5. Changes are committed.
6. Changes are pushed to GitHub.
7. Repeat for next sprint.

---

# Current Progress

Backend

- ✅ Authentication
- ✅ Dashboard
- ✅ Income
- ⏳ Expenses
- ⏳ Budgets
- ⏳ Savings Goals
- ⏳ Reports

Frontend

- ⏳ Pending Integration

Deployment

- ⏳ Pending

Testing

- ⏳ Pending