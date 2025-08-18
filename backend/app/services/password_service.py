from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import mechanic as crud_mechanic
from app.core.security import create_password_reset_token, verify_password_reset_token, hash_password
from app.core.mailer import send_email_async
from app.dependencies.db import get_db

class PasswordService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def recover_password(self, email: str):
        """
        Handles the password recovery request.
        Generates a token and sends the recovery email.
        """

        token = create_password_reset_token(email=email)
        await send_email_async(
            subject="Password Reset Request",
            email_to=email,
            body={"token": token}
        )

    def reset_password(self, token: str, new_password: str):
        """
        Handles the password reset.
        Verifies the token and updates the password.
        """
        email = verify_password_reset_token(token)
        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        mechanic = crud_mechanic.get_mechanic_by_email(self.db, email)
        if not mechanic:
            raise HTTPException(status_code=404, detail="User not found")

        hashed_new_password = hash_password(new_password)
        crud_mechanic.update_mechanic_password(self.db, mechanic, hashed_new_password)
