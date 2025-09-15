from fastapi import FastAPI
from app.routes import auth, otp, user
from contextlib import asynccontextmanager
from app.core.settings import get_settings
from app.core.openapi import custom_openapi
from app.utils.response import success_response
from app.database.db_config import create_database
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.middlewares.auth_middleware import AuthMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import configure_logging, RequestIdLoggingMiddleware
from app.core.exceptions import http_exception_handler, validation_exception_handler, generic_exception_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()

    yield 
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

configure_logging()
app.add_middleware(RequestIdLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
app.add_middleware(AuthMiddleware)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(otp.router)

@app.get("/", tags=["Health Check"])
def health_check():
    return success_response(message="API is running successfully", data={"status": "ok"})

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.openapi = lambda: custom_openapi(app)

