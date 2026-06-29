# Job Application Tracker API

A REST API for tracking job applications, built with FastAPI. Users register, log in, and manage their own set of job applications — each user can only access their own data, enforced at the database query level.

## Features

- JWT-based authentication with bcrypt password hashing
- Full CRUD on job applications (create, list, retrieve, update, delete)
- Per-user data isolation — every application route is scoped to the authenticated user, so requests for another user's data return `404` rather than leaking ownership
- SQLite persistence via SQLModel (SQLAlchemy + Pydantic)
- Auto-generated interactive API docs (Swagger UI) at `/docs`

## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| ORM / validation | SQLModel |
| Database | SQLite |
| Auth | python-jose (JWT), Passlib (bcrypt) |
| Server | Uvicorn |

## Getting Started

### Prerequisites
- Python 3.10+

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/job-application-tracker-api.git
cd job-application-tracker-api
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
SECRET_KEY=your-own-random-secret-string-here
```

### Run

```bash
uvicorn main:app --reload
```

API: `http://127.0.0.1:8000` · Docs: `http://127.0.0.1:8000/docs`

## API Reference

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/register` | Create a new user account | — |
| POST | `/login` | Authenticate and receive a JWT | — |
| POST | `/applications` | Create a job application | Required |
| GET | `/applications` | List the current user's applications | Required |
| GET | `/applications/{id}` | Retrieve a single application | Required |
| PUT | `/applications/{id}` | Update an application | Required |
| DELETE | `/applications/{id}` | Delete an application | Required |

Authenticated requests pass the JWT as a bearer token:
```
Authorization: Bearer <token>
```

## Roadmap

- [ ] Automated tests with pytest
- [ ] PostgreSQL in place of SQLite