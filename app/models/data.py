from sqlalchemy import Column, Integer, BigInteger, DateTime, func
from app.database import Base

class UserCount(Base):
    __tablename__ = "user_counts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime, nullable=False, default=func.now())

    class Config:
        orm_mode = True
