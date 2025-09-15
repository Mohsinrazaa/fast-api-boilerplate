from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.database.db_config import get_db
from app.utils.response import success_response, error_response

router = APIRouter()

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Google login callback handler that receives the authorization code and authenticates the user.
    """
    auth_service = AuthService(db)
    try:
        result = auth_service.login_or_signup_with_google(code)
        return success_response(message="Google callback successful", data=result)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)
