from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db_config import get_db
from app.services.otp_service import OTPService
from app.schemas.otp import OTPCreate, OTPVerify
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post("/generate-manual")
def generate_manual_otp(user_id: int, db: Session = Depends(get_db)):
    """
    Manually generate an OTP for testing purposes.
    """
    otp_service = OTPService(db)
    try:
        contact = "example@test.com"
        contact_type = "email"
        result = otp_service.generate_and_send_otp(user_id=user_id, contact=contact, contact_type=contact_type)
        return success_response(message="OTP generated (manual)", data=result, status_code=201)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)


@router.post("/generate")
def generate_otp(data: OTPCreate, db: Session = Depends(get_db)):
    """
    Generate an OTP and send it to the user's contact.
    """
    otp_service = OTPService(db)
    try:
        result = otp_service.generate_and_send_otp(user_id=data.user_id, contact=data.contact, contact_type=data.contact_type)
        return success_response(message="OTP generated", data=result, status_code=201)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)



@router.post("/verify")
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify a submitted OTP for a user.
    """
    otp_service = OTPService(db)
    try:
        result = otp_service.verify_otp(encrypted_user_id=data.user_id, otp_code=data.otp_code)
        return success_response(message="OTP verified", data=result)
    except HTTPException as exc:
        return error_response(message=str(exc.detail), status_code=exc.status_code)
    except Exception as exc:
        return error_response(message=str(exc), status_code=400)