from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class PrankType(str, Enum):
    moan = 'moan'
    photo = 'photo'
    video = 'video'

class PrankStatistic(BaseModel):
    telegram_id: str | int
    prank_type: PrankType
    date_create: datetime
