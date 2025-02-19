from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserCountBase(BaseModel):
    count: int
    timestamp: datetime

class UserCountCreate(UserCountBase):
    pass

class UserCount(UserCountBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserCountResponse(BaseModel):
    current_count: int
    last_updated: datetime

class UserCountHistory(BaseModel):
    history: List[UserCount]
    total_records: int
