# Stage 1: Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Setup virtual environment and dependencies
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production runtime stage
FROM python:3.12-slim AS runner

WORKDIR /app

# Install curl for healthcheck validation
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source codes and configurations
COPY app/ app/
COPY migrations/ migrations/
COPY alembic.ini .
COPY .env.example .env

# Create persistent directories for SQLite database and uploaded attachments
RUN mkdir -p /app/uploads /app/data

# Create a non-root user and assign permissions
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser && \
    chown -R appuser:appgroup /app

# Set system environment parameters
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL="sqlite+aiosqlite:////app/data/notes.db"
ENV UPLOAD_DIR="/app/uploads"

# Switch to non-root user
USER appuser

EXPOSE 8000

# Apply migrations first, then run FastAPI application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
