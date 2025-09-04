from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, otp, user
from app.middlewares.auth_middleware import AuthMiddleware
from app.database.db_config import create_database  # Import create_database function
from app.core.settings import get_settings
from app.core.logging import configure_logging, RequestIdLoggingMiddleware
from app.core.exceptions import http_exception_handler, validation_exception_handler, generic_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.openapi import custom_openapi
from app.utils.response import success_response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to execute during application startup
    print("Application is starting up...")
    create_database()  # Call the function to create the database and tables

    yield  # Application is running here
    # Code to execute during application shutdown
    print("Application is shutting down...")

settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    version="1.0.0",
    description="Secure and scalable FastAPI boilerplate with advanced features.",
    contact={"name": "API Support", "email": "support@example.com"},
    license_info={"name": "MIT"},
)
# Structured logging & request IDs
configure_logging()
app.add_middleware(RequestIdLoggingMiddleware)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
app.add_middleware(AuthMiddleware)

# Include route modules
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(otp.router)




# Health Check Route
@app.get("/", tags=["Health Check"])
def health_check():
    return success_response(message="API is running successfully", data={"status": "ok"})

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# OpenAPI security
app.openapi = lambda: custom_openapi(app)

