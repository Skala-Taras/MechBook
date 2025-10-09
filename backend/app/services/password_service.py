from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib

from app.crud import mechanic as crud_mechanic
from app.core.security import create_password_reset_token, verify_password_reset_token, hash_password
from app.core.mailer import send_email_async
from app.core.config import settings
from app.dependencies.db import get_db
from app.models.password_reset_tokens import PasswordResetTokens

class PasswordService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def recover_password(self, email: str):
        """
        Handles the password recovery request.
        Generates a token and sends the recovery email with clickable link.
        """
        # Check if mechanic exists
        mechanic = crud_mechanic.get_mechanic_by_email(self.db, email)
        if not mechanic:
            return {"message": "If the email exists, a reset link has been sent"}

        token = create_password_reset_token(email=email)
        
        # Store token hash in database for one-time use tracking
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            db_token = PasswordResetTokens(
                token_hash=token_hash,
                email=email
            )
            self.db.add(db_token)
            self.db.commit()
            print(f"Stored new reset token for email: {email}")
        except Exception as e:
            print(f"Warning: Could not store reset token in database: {e}")
            pass
        
        # Create reset link for frontend
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        await send_email_async(
            subject="Password Reset Request",
            email_to=email,
            body={"reset_link": reset_link}
        )
        
        return {"message": "Password reset link sent to your email"}

    def reset_password(self, token: str, new_password: str):
        """
        Handles the password reset with one-time use validation.
        Verifies the token and updates the password.
        """
        # Verify token format and extract email/token_id
        token_data = verify_password_reset_token(token)
        if not token_data:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        email = token_data["email"]
        #token_id = token_data["token_id"]
        
        # Check if token was already used (if database tracking is available)
        db_token = None
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            db_token = self.db.query(PasswordResetTokens).filter(
                PasswordResetTokens.token_hash == token_hash,
                PasswordResetTokens.email == email
            ).first()
            
            if db_token and db_token.used_at is not None:
                raise HTTPException(status_code=400, detail="This reset link has already been used")
                
        except HTTPException:
            # Re-raise HTTP exceptions (these are intended errors)
            raise
        except Exception as e:
            print(f"Warning: Could not check token usage in database: {e}")
            db_token = None

        # Find mechanic
        mechanic = crud_mechanic.get_mechanic_by_email(self.db, email)
        if not mechanic:
            raise HTTPException(status_code=404, detail="User not found")

        # Update password
        hashed_new_password = hash_password(new_password)
        crud_mechanic.update_mechanic_password(self.db, mechanic, hashed_new_password)
        
        # Mark token as used (if database tracking is available)
        try:
            if db_token:
                db_token.used_at = datetime.utcnow()
                self.db.commit()
                print(f"Token marked as used at: {db_token.used_at}")
        except Exception as e:
            print(f"Warning: Could not mark token as used: {e}")
            pass
        
        return {"message": "Password successfully reset"}
