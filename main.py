from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import router as auth_router
from routes.tasks import router as tasks_router
from routes.chat import router as chat_router
from database import create_db_and_tables
import logging

app = FastAPI(title="Todo API")

# CORS configuration - Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000",
                     "http://localhost:3001",
                     "https://todo-app-one-gamma-91.vercel.app/login"
    ],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to create tables
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logging.info("Database tables created successfully")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
def root():
    return {"message": "Todo API is running"}

@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running"""
    return {
        "status": "healthy",
        "message": "Todo API is running and database is connected"
    }