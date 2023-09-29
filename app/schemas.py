from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class VideoTimeUpdate(BaseModel):
    playback_time: Decimal = Field(decimal_places=2)
        
class Video(BaseModel):
    id:int
    user_id: int
    video_url: str
    playback_time: Optional[float] = None
    created_at:datetime

    class Config:
        from_attributes = True
