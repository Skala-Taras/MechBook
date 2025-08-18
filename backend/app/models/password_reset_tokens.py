from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class PasswordResetTokens(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
