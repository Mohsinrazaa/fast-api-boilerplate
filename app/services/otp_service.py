from datetime import datetime
from app.models.otp import OTP
from app.models.user import User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils.sms_util import send_sms
from app.utils.email_util import send_email
from app.utils.crypto_util import decrypt_data
from app.utils.otp_util import generate_otp, otp_expiry
from app.utils.response import success_response, error_response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self, db: Session):
        self.db = db

    def generate_and_send_otp(self, user_id: int, contact: str, contact_type: str = "email"):
        print('contact_type xxxxx SERVICE', contact_type)

        if not user_id or not isinstance(user_id, int):
            return {"error": "Invalid user_id"}
        if not contact or not isinstance(contact, str):
            return {"error": "Invalid contact information"}
        if contact_type not in ["email", "phone"]:
            return {"error": "Invalid contact type"}

        existing_otp = self.db.query(OTP).filter(
            OTP.user_id == user_id,
            OTP.expires_at > datetime.utcnow()
        ).first()

        otp_code = generate_otp()
        expires_at = otp_expiry()
        if existing_otp:
            existing_otp.otp_code = otp_code
            existing_otp.expires_at = expires_at
            existing_otp.verified = False
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback() 
                logger.error(f"Database error: {str(e)}")
                return {"error": f"Database error: {str(e)}"}
        
        try:
            otp_entry = OTP(user_id=user_id, otp_code=otp_code, expires_at=expires_at)
            self.db.add(otp_entry)
            self.db.commit()
        except Exception as e:
            self.db.rollback()  
            logger.error(f"Database error: {str(e)}")
            return {"error": f"Database error: {str(e)}"}
    
        try:
            if contact_type == "email":
                send_email(
                    to=contact,
                    subject="Your OTP Code",
                    body=f"Your OTP code is: {otp_code}. It will expire in 5 minutes."
                )
            elif contact_type == "phone":
                send_sms(
                    to=contact,
                    message=f"Your OTP code is: {otp_code}. It will expire in 5 minutes."
                )
        except Exception as e:
            
            self.db.rollback()
            logger.error(f"Failed to send OTP: {str(e)}")
            return {"error": f"Failed to send OTP: {str(e)}"}

        return success_response(
            message="OTP sent successfully",
            data={
                "otp_sent_to": contact,
                "expires_at": expires_at.isoformat() + "Z"
            }
        )

    def verify_otp(self, encrypted_user_id: str, otp_code: str):

        try:
            user_id = int(decrypt_data(encrypted_user_id))
            print('USER ID',user_id)
        except Exception as e:
            logger.error(f"Failed to decrypt user ID: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid user ID")
        otp_entry = self.db.query(OTP).filter(OTP.user_id == user_id, OTP.otp_code == otp_code).first()

        if not otp_entry:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        if otp_entry.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP has expired")

        otp_entry.verified = True
        self.db.commit()
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_verified = True
            self.db.commit()

        return success_response(message="OTP verified successfully")
