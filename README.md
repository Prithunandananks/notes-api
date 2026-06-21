# Notes API

A secure FastAPI-based Notes Management API featuring JWT authentication, user-specific notes, file attachments, database migrations, rate limiting, and automated testing.

## Features

- JWT Authentication & Authorization
- User Registration and Login
- User-Specific Notes
- CRUD Operations for Notes
- File Attachments Upload
- Rate Limiting
- Database Migrations with Alembic
- Automated Testing with Pytest
- Docker Support

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- Pydantic
- JWT (python-jose)
- Pytest
- Docker

## Project Structure

```text
app/
├── routes/
├── services/
├── repositories/
├── models/
├── schemas/
├── core/

migrations/
tests/
```

## Installation

```bash
pip install -r requirements.txt
```

## Run Migrations

```bash
alembic upgrade head
```

## Run Application

```bash
uvicorn app.main:app --reload
```

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

```bash
python -m pytest
```

Current test status:

```text
14 passed
```

## Key Capabilities

- Secure JWT-based authentication
- Protected user resources
- File upload support
- Database version control
- Automated test coverage
- Docker-ready deployment

```

```
