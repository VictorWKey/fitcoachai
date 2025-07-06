"""
ORM model for the JWT token blacklist.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..base import Base

class TokenBlacklist(Base):
    """
    Model for storing revoked JWT tokens.
    Allows identifying tokens that are no longer valid even if they haven't expired.
    
    Attributes:
        id: Unique identifier for the record
        jti: Unique identifier of the JWT token (JWT ID)
        exp: Token expiration date
        created_at: Date when the token was added to the blacklist
    """
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True)
    exp = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        """String representation of the blacklisted token."""
        return f"<TokenBlacklist {self.jti}>" 