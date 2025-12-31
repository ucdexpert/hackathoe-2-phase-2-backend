# Backend Development Guidelines

## Technology Stack
- Python 3.13+
- FastAPI for web framework
- SQLModel for ORM (combines SQLAlchemy and Pydantic)
- Neon PostgreSQL for database
- python-jose for JWT handling
- passlib[bcrypt] for password hashing
- python-multipart for file uploads
- uvicorn for ASGI server

## Project Structure
```
backend/
├── main.py                 # Application entry point and routing
├── models.py               # Database models using SQLModel
├── database.py             # Database connection and session management
├── auth.py                 # Authentication utilities and JWT handling
├── routes/                 # API route handlers
│   ├── __init__.py
│   ├── auth_routes.py      # Authentication endpoints
│   └── tasks.py            # Task management endpoints
├── pyproject.toml          # Project dependencies and configuration
├── .env                    # Environment variables (not committed)
├── .env.example            # Example environment variables
└── CLAUDE.md               # Backend development guidelines
```

## API Design Principles
- Follow RESTful API conventions
- Use kebab-case for URL endpoints
- Return consistent JSON response structure
- Use appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Implement JWT-based authentication for all protected endpoints
- Validate input using Pydantic models
- Use HTTP Bearer tokens for authentication

## Database Management
- Use SQLModel for all database operations (combines SQLAlchemy and Pydantic)
- Define models with proper relationships and constraints
- Use dependency injection for database sessions
- Implement proper transaction handling when needed
- Create database indexes for frequently queried fields

## Authentication & Security
- Implement JWT-based authentication with 7-day expiration
- Use bcrypt for password hashing with proper salt
- Validate JWT tokens on all protected endpoints
- Implement proper user isolation (users can only access their own data)
- Sanitize all user inputs to prevent injection attacks
- Use HTTPS in production environments

## Error Handling
- Return appropriate HTTP status codes for different error conditions
- Provide meaningful error messages in response body
- Log errors appropriately for debugging
- Implement global exception handlers where appropriate
- Never expose sensitive information in error responses

## Dependency Management
- Use UV for package management (as per constitution)
- Pin major and minor versions in pyproject.toml
- Separate runtime and development dependencies
- Keep dependencies up to date while maintaining compatibility

## Environment Configuration
- Use environment variables for configuration
- Store sensitive information (DB URLs, secrets) in environment variables
- Create .env.example with placeholder values
- Use python-dotenv for local development