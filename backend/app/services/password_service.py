from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import random
import string

from app.crud import mechanic as crud_mechanic
from app.core.security import create_password_reset_token, hash_password
from app.core.mailer import send_email_async
from app.dependencies.db import get_db
from app.models.password_reset_tokens import PasswordResetTokens
from app.core.security import verify_password

class PasswordService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    def _generate_verification_code(self) -> str:
        """Generate a random 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def change_password(self, current_password: str, new_password: str, mechanic_id: int):
        """
        Change the password of the current mechanic.
        """
        mechanic = crud_mechanic.get_mechanic_by_id(self.db, mechanic_id)
        if not mechanic:
            raise HTTPException(status_code=404, detail="Mechanic not found")
        if not verify_password(current_password, mechanic.hashed_password):
            raise HTTPException(status_code=400, detail="Obecne hasło jest nieprawidłowe")
        hashed_new_password = hash_password(new_password)
        crud_mechanic.update_mechanic_password(self.db, mechanic, hashed_new_password)
        return {"message": "Hasło zostało zmienione"}

    async def recover_password(self, email: str):
        """
        Handles the password recovery request.
        Generates a 6-digit verification code and sends it via email.
        Code expires in 15 minutes.
        """
        # Normalize email
        email = email.strip().lower()
        
        # Check if mechanic exists
        mechanic = crud_mechanic.get_mechanic_by_email(self.db, email)
        if not mechanic:
            return {"message": "Jeśli istnieje konto z tym email, kod do resetu hasła został wysłany"}

        # Generate verification code and token
        verification_code = self._generate_verification_code()
        token = create_password_reset_token(email=email)
        
        # Store token with verification code in database
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            expires_at = datetime.utcnow() + timedelta(minutes=15)
            
            db_token = PasswordResetTokens(
                token_hash=token_hash,
                verification_code=verification_code,
                email=email,
                expires_at=expires_at
            )
            self.db.add(db_token)
            self.db.commit()
            print(f"Stored verification code for email: {email}, expires at: {expires_at}")
        except Exception as e:
            print(f"Error: Could not store verification code: {e}")
            raise HTTPException(status_code=500, detail="Could not process request")
        
        # Send email with verification code
        try:
            await send_email_async(
                subject="Password Reset - Verification Code",
                email_to=email,
                body={"verification_code": verification_code}
            )
            return {"message": "Verification code sent to your email"}
        except Exception as e:
            print(f"Email sending failed: {e}")
            # For development - return code in response
            return {"message": "Email service unavailable."}

    def verify_code(self, email: str, code: str):
        """
        Verifies the 6-digit code sent to the user's email.
        Returns a session token if code is valid.
        """
        email = email.strip().lower()
        code = str(code).strip() 
        
        if not code.isdigit() or len(code) != 6:
            print(f"Invalid code format received: '{code}' (length: {len(code)})")
            raise HTTPException(status_code=400, detail="Invalid verification code format. Code must be exactly 6 digits.")
        
        print(f"Verifying code for email: {email}, code: '{code}' (type: {type(code).__name__})")
        
        # Find the most recent unused code for this email
        db_token = self.db.query(PasswordResetTokens).filter(
            PasswordResetTokens.email == email,
            PasswordResetTokens.verification_code == code,
            PasswordResetTokens.verified_at.is_(None),  
            PasswordResetTokens.used_at.is_(None)       
        ).order_by(PasswordResetTokens.created_at.desc()).first()
        
        if not db_token:
            all_codes = self.db.query(PasswordResetTokens).filter(
                PasswordResetTokens.email == email
            ).order_by(PasswordResetTokens.created_at.desc()).limit(5).all()
            
            print(f"No matching code found. Recent codes for {email}:")
            for token in all_codes:
                print(f"  - Code: '{token.verification_code}' (verified: {token.verified_at}, used: {token.used_at}, expires: {token.expires_at})")
            
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        # Check if code has expired (15 minutes)
        if datetime.utcnow() > db_token.expires_at:
            raise HTTPException(status_code=400, detail="Verification code has expired")
        
        # Mark code as verified
        db_token.verified_at = datetime.utcnow()
        self.db.commit()
        
        # Generate session token for password reset (valid for 5 minutes)
        reset_token = create_password_reset_token(email=email)
        
        return {
            "message": "Kod został zweryfikowany",
            "reset_token": reset_token
        }
    
    def reset_password(self, reset_token: str, new_password: str):
        """
        Resets the password using the token from verify_code.
        User must have verified their code first.
        """
        from app.core.security import verify_password_reset_token
        token_data = verify_password_reset_token(reset_token)
        if not token_data:
            print(f"ERROR: Invalid or expired reset token")
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Normalize email - MUST match what verify_code does
        email = token_data["email"].strip().lower()
        print(f"DEBUG reset_password: Looking for verified session for email: '{email}'")
        
        # Find most recent verified but unused token for this email
        db_token = self.db.query(PasswordResetTokens).filter(
            PasswordResetTokens.email == email,
            PasswordResetTokens.verified_at.isnot(None),
            PasswordResetTokens.used_at.is_(None)
        ).order_by(PasswordResetTokens.verified_at.desc()).first()
        
        if not db_token:
            # Debug: show all tokens for this email
            all_tokens = self.db.query(PasswordResetTokens).filter(
                PasswordResetTokens.email == email
            ).order_by(PasswordResetTokens.created_at.desc()).limit(5).all()
            
            print(f"ERROR: No verified session found for email: '{email}'")
            print(f"DEBUG: All recent tokens for this email:")
            for token in all_tokens:
                print(f"  - Email: '{token.email}', verified_at: {token.verified_at}, used_at: {token.used_at}, expires_at: {token.expires_at}")
            
            raise HTTPException(status_code=400, detail="No verified session found. Please verify your code first.")
        
        # Check if verification session has expired (5 minutes after verification)
        time_since_verification = datetime.utcnow() - db_token.verified_at
        print(f"DEBUG: Time since verification: {time_since_verification.total_seconds()} seconds")
        
        if datetime.utcnow() > db_token.verified_at + timedelta(minutes=5):
            print(f"ERROR: Reset session expired for email: '{email}'")
            raise HTTPException(status_code=400, detail="Reset session has expired. Please request a new code.")
        
        # Find mechanic
        mechanic = crud_mechanic.get_mechanic_by_email(self.db, email)
        if not mechanic:
            print(f"ERROR: Mechanic not found for email: '{email}'")
            raise HTTPException(status_code=404, detail="User not found")

        # Update password
        hashed_new_password = hash_password(new_password)
        crud_mechanic.update_mechanic_password(self.db, mechanic, hashed_new_password)
        
        # Mark token as used
        db_token.used_at = datetime.utcnow()
        self.db.commit()
        print(f"SUCCESS: Password reset for {email} at: {db_token.used_at}")
        
        return {"message": "Password successfully reset"}
