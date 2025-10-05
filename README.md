# BASF Book Recommendation System Backend

This repository contains the backend service for a book recommendation system built with FastAPI. It provides a RESTful API for user authentication, book management, and user reviews. The system can be seeded with an initial set of books and periodically updates its catalog from the Google Books API using background tasks.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Application](#running-the-application)
  - [API Server](#api-server)
  - [Background Worker](#background-worker)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Makefile Commands](#makefile-commands)

## Features
- **JWT Authentication**: Secure user login and endpoint access using JSON Web Tokens.
- **Book Catalog**: List, search (by title or author), and view books with their average user ratings.
- **Review System**: Authenticated users can post and update reviews (rating and text) for any book.
- **Google Books Integration**: Dynamically fetches and seeds book data from the Google Books API.
- **Background Tasks**: Uses Celery and Celery Beat to schedule and run periodic tasks, such as refreshing the book catalog every 12 hours.
- **Asynchronous Operations**: Fully asynchronous application using FastAPI and SQLAlchemy's async support for high performance.
- **Database Seeding**: Automatically seeds the database with initial users and books on application startup.

## Tech Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (with async support)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (production), [SQLite](https://www.sqlite.org/) (testing)
- **Background Jobs**: [Celery](https://docs.celeryq.dev/en/stable/)
- **Message Broker**: [Redis](https://redis.io/)
- **Authentication**: `python-jose` for JWT, `passlib` for password hashing
- **API Client**: `httpx` for making async requests to external services
- **Testing**: `pytest` and `pytest-asyncio`
- **Linting & Formatting**: `Ruff`

## Project Structure
The project follows a modular structure to separate concerns and improve maintainability.

```
src/app/
├── api/            # FastAPI routers, endpoints, and dependencies
├── clients/        # Clients for external services (e.g., Google Books)
├── core/           # Core logic: configuration, security, logging
├── data/           # Seed data files (JSON)
├── db/             # Database session management and base models
├── models/         # SQLAlchemy ORM models
├── repositories/   # Data access layer (interacts with the database)
├── schemas/        # Pydantic schemas for data validation and serialization
├── services/       # Business logic layer
└── task/           # Celery background tasks
```

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- A code editor (like VSCode)

### Installation
1.  **Clone the repository:**
    ```sh
    git clone https://github.com/abdurrafay360/basf_case_study_backend.git
    cd basf_case_study_backend
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate
    # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    The project dependencies are listed in `pyproject.toml`. Install them using pip:
    ```sh
    pip install .
    ```

4.  **Configure environment variables:**
    Copy the example environment file and update it with your settings.
    ```sh
    cp .env.example .env
    ```
    Open the `.env` file and set the following variables, especially `DATABASE_URL` and `SECRET_KEY`.
    - `DATABASE_URL`: Your PostgreSQL connection string (e.g., `postgresql+asyncpg://user:password@host:port/dbname`).
    - `REDIS_URL`: Your Redis connection string.
    - `SECRET_KEY`: A strong, unique secret for JWT signing.

    The application will automatically create the database tables on startup.

## Running the Application

### API Server
You can run the FastAPI application using the provided Makefile command, which utilizes Uvicorn with hot-reloading.

```sh
make run
```
The API will be available at `http://127.0.0.1:8000`. Interactive API documentation (Swagger UI) can be accessed at the root URL (`http://127.0.0.1:8000/`).

### Background Worker
To process background tasks like refreshing the book list, you need to run a Celery worker and the Celery Beat scheduler in separate terminals.

1.  **Run the Celery Worker:**
    ```sh
    celery -A app.celery_app worker --loglevel=info
    ```

2.  **Run the Celery Beat Scheduler:**
    ```sh
    celery -A app.celery_app beat --loglevel=info
    ```

## API Endpoints
All endpoints are prefixed with `/api/v1`. Most endpoints require a valid JWT Bearer token in the `Authorization` header.

#### Authentication
- `POST /auth/login`
  - Authenticates a user with a username and password, returning a JWT access token.

#### Books
- `GET /books/`
  - Retrieves a list of books.
  - Query Parameters: `search` (string), `limit` (int), `offset` (int).
- `POST /books/refresh-books`
  - Triggers an asynchronous background task to refresh the book list from the Google Books API.

#### Reviews
- `POST /reviews/{book_id}/reviews`
  - Creates a new review or updates an existing one for a specific book by the authenticated user.
- `GET /reviews/{book_id}/reviews`
  - Retrieves all reviews for a specific book.

## Testing
The project uses `pytest` for testing. The test suite is configured to use an in-memory SQLite database to ensure tests are isolated and fast.

To run the full test suite, use the Makefile command:
```sh
make test
```

## Makefile Commands
The `Makefile` provides convenient shortcuts for common development tasks:

- `make run`: Starts the FastAPI application with Uvicorn.
- `make test`: Executes the test suite with pytest.
- `make fmt`: Formats the code using Ruff.
- `make lint`: Lints the code using Ruff to check for issues.