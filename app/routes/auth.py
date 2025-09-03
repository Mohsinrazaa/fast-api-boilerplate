from fastapi import APIRouter, Depends, HTTPException, Request
import requests  # Import the correct requests library
from sqlalchemy.orm import Session
from app.database.db_config import get_db
from app.services.auth_service import AuthService
from app.services.google_auth_service import GoogleAuthService
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest, SignUpRequest, LoginRequest, GoogleAuthCallback
from dotenv import load_dotenv
import os
from app.utils.response import success_response, error_response
router = APIRouter(prefix="/auth", tags=["Auth"])



load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


@router.post("/signup")
def signup(data: SignUpRequest, db: Session = Depends(get_db)):
    """
    Register a new user with provided credentials.
    Returns a standardized success or error response.
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.signup(data)
        return success_response(message="Signup successful", data=result, status_code=201)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:  # Fallback error shape
        return error_response(message=str(exc), status_code=400)


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate an existing user using username/email/phone and password.
    Returns JWT tokens and user info in standardized format.
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.login(
            username_or_email_or_phone=data.username_or_email_or_phone,
            password=data.password,
        )
        return success_response(message="Login successful", data=result)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)


@router.get("/google")
def google_login():
    """
    Return Google OAuth2 authorization URL to initiate login/signup flow.
    """
    try:
        url = GoogleAuthService.get_google_auth_url()
        return success_response(message="Google auth URL generated", data={"auth_url": url})
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)


@router.post("/login_or_signup_with_google")
def login_or_signup_with_google(code: str, db: Session = Depends(get_db)):
    """
    Log in or sign up with Google OAuth code; exchanges code for tokens and returns user session.
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.login_or_signup_with_google(code, db)
        return success_response(message="Google auth successful", data=result)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)


@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Google OAuth2 callback; exchanges authorization code for tokens and authenticates or registers the user.
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.login_or_signup_with_google(code, db)
        return success_response(message="Google callback successful", data=result)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)







@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Initiate password reset by sending a reset link or OTP to the user.
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.forgot_password(email=request.email)
        return success_response(message="Password reset initiated", data=result)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Complete password reset using a valid token and new password values.
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.reset_password(
            token=request.token,
            new_password=request.new_password,
            confirm_password=request.confirm_password,
        )
        return success_response(message="Password reset successful", data=result)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)