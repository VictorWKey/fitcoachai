from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..base import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True)
    exp = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TokenBlacklist {self.jti}>" 