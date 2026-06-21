# Notes API

A production-style Notes Management REST API built with FastAPI, JWT Authentication, SQLAlchemy, Alembic, Docker, and automated testing.

## Features

- User Registration & Authentication
- JWT Token-Based Authorization
- Secure Protected Routes
- Create, Read, Update, Delete Notes
- File Upload Support
- Database Migrations with Alembic
- Rate Limiting
- Centralized Exception Handling
- Docker Support
- Automated Testing with Pytest
- Interactive Swagger Documentation

## Tech Stack

### Backend

- FastAPI
- Python 3.14
- SQLAlchemy
- Pydantic

### Database

- SQLite
- Alembic

### Authentication

- JWT (JSON Web Tokens)
- Password Hashing

### Testing

- Pytest

### DevOps

- Docker
- Docker Compose

---

## Project Structure

```text
app/
├── core/
├── dependencies/
├── models/
├── repositories/
├── routes/
├── schemas/
├── services/
└── main.py

tests/
migrations/
Dockerfile
docker-compose.yml
requirements.txt
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Prithunandananks/notes-api.git
cd notes-api
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows:

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file based on `.env.example`.

### Run Application

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running Tests

```bash
python -m pytest
```

Current Test Status:

```text
14 Passed
```

---

## API Modules

### Authentication

- Register User
- Login User

### Users

- Get Current User Profile

### Notes

- Create Note
- List Notes
- Get Note
- Update Note
- Delete Note
- Upload Attachments

---

## Future Improvements

- PostgreSQL Support
- Refresh Tokens
- User Roles & Permissions
- Email Verification
- Cloud File Storage
- CI/CD Pipeline
- Custom API Documentation Portal

---

## Author

**Prithunandanan K S**

GitHub:
https://github.com/Prithunandananks

LinkedIn:
https://linkedin.com/in/prithunandanan-k-s-1787243a9
