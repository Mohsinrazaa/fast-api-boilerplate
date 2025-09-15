import logging
from typing import List
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_all_users(db: Session) -> List[UserResponse]:
        """
        Retrieve all users from the database.

        :param db: Database session
        :return: List of UserResponse objects
        """
        users = db.query(User).all()
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                phone_number=user.phone_number,
                profile_picture_url=user.profile_picture_url,
                is_verified=user.is_verified,
            )
            for user in users
        ]
