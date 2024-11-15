from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from backend.config import DBAction


class PrankType(str, Enum):
    moan = 'moan'
    photo = 'photo'
    video = 'video'

class Prank(BaseModel, DBAction):
    telegram_id: str
    prank_type: PrankType | None = None
    date_create: datetime = datetime.now()

class User(BaseModel, DBAction):
    ip: str | None = None
    user_agent: str | None = None
    date_create: datetime = datetime.now()