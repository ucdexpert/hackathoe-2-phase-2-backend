# Todo App Backend

This is the backend for the Todo application, built with FastAPI.

## Deploying to Hugging Face Spaces

This repository is configured for deployment on Hugging Face Spaces using the `app_file` method.

### Configuration

- `app.py` - Entry point for the application
- `requirements.txt` - Python dependencies
- `space.yaml` - Hugging Face Space configuration
- `Dockerfile` - Container configuration

### Environment Variables

The application requires the following environment variables:

- `DATABASE_URL` - PostgreSQL database connection string

### Local Development

To run locally:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### API Endpoints

- `/` - Root endpoint
- `/api/auth/*` - Authentication endpoints
- `/api/tasks/*` - Task management endpoints
- `/api/chat/*` - Chat endpoints