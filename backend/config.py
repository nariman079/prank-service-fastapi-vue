import os
from pathlib import Path
from typing import Self, Any

from pydantic import BaseModel
from pymongo import MongoClient
from aiogram import Bot
from dotenv import load_dotenv
from pymongo.synchronous.collection import Collection

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DB_URL = os.getenv('DB_URL')
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID', -4575472838)


path = Path('uploads')
drive = Bot(TOKEN)

last_chunk_time = dict()
active_tasks = dict()

INACTIVITY_TIMEOUT = 1
client = MongoClient(DB_URL)

class DBController:
    def __init__(self, table_name:str):
        self.db = client['Statistic']
        self.table: Collection = self.db[table_name]

class DBAction:
    @classmethod
    async def create(cls: BaseModel | Self, **kwargs) -> Self:
        """
        Создание документа
        """
        return DBController(cls.__name__).table.insert_one(
            cls(**kwargs).dict()
        )

    @classmethod
    def aggregate(cls: Self | BaseModel, param: Any):
        """Агрегирование данных"""
        return cls.connection.table.aggregate(param)
