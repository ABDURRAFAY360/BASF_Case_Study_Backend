# =========================
# Base image
# =========================
FROM python:3.9-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (build-essential helps wheels that need compiling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project (we keep it simple & robust for setuptools build)
# If your repo is large, prefer a two-step copy of only needed files.
COPY pyproject.toml ./
COPY app ./app
COPY tests ./tests
COPY .env.example ./.env.example
# (Optional) if you seed from files:
# COPY data ./data

# Install project & runtime deps from pyproject
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install .

# =========================
# Test stage
# =========================
FROM base AS test

# Install test deps only here to keep runtime image smaller
RUN pip install pytest pytest-asyncio

# Default env for tests (in-memory SQLite + a throwaway secret)
ENV DATABASE_URL="sqlite+aiosqlite://" \
    SECRET_KEY="dev-only-secret-change-me" \
    ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="60"

# Run tests by default in this stage
CMD ["pytest", "-q"]

# =========================
# Runtime stage
# =========================
FROM base AS app

# If your pyproject did not include uvicorn runtime, ensure it here:
RUN pip install "uvicorn[standard]"

# Expose port and run the API
ENV HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

# In-memory SQLite uses StaticPool in your app; no external DB needed.
# Use .env at runtime via docker-compose (recommended).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
