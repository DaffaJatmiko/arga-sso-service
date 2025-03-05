# Arga SSO Service

A Simple Single Sign-On (SSO) service built with FastAPI following clean architecture principles.

## Features

- User authentication and authorization
- JWT-based token management
- User management
- Redis-based session management
- PostgreSQL database

## Project Structure

```
src/
├── api/                    # API layer
│   └── v1/
│       ├── endpoints/      # API endpoints
│       └── router.py       # API router
├── application/           # Application layer (use cases)
│   └── auth/
│       └── service.py
├── domain/               # Domain layer
│   ├── models/          # Domain models
│   └── repositories/    # Repository interfaces
├── infrastructure/      # Infrastructure layer
│   ├── database/       # Database configurations
│   └── redis/          # Redis configurations
├── config.py           # Application configuration
└── main.py            # Application entry point
```

## Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and update the values
5. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Documentation

Once the application is running, you can access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

To run the development server with hot reload:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
