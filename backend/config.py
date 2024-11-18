import os
import logging
from pathlib import Path
from typing import Self, Any

from pydantic import BaseModel
from pymongo import MongoClient
from aiogram import Bot
from dotenv import load_dotenv
from pymongo.synchronous.collection import Collection
from redis.commands.search.aggregation import Cursor

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
        return DBController(
            cls.__name__
        ).table.insert_one(
            cls(**kwargs).dict()
        )

    @classmethod
    async def get(cls, **kwargs) -> Self | None :
        document = DBController(cls.__name__).table.find_one(kwargs)
        if document:
            data = document
            data.pop('_id')
            return cls(**data)
        return document

    @classmethod
    async def get_or_create(cls, **kwargs) -> tuple[Self, bool]:
        """Поиск или создание"""
        document = DBController(cls.__name__).table.find_one(kwargs)
        if document:
            data = document
            data.pop('_id')
            print(data)
            return cls(**data), False
        return DBController(cls.__name__).table.insert_one(cls(**kwargs).dict()), True

    @classmethod
    async def find(cls: BaseModel | Self, **kwargs) -> Cursor:
        """
        Поиск документов
        """
        return DBController(cls.__name__).table.find(kwargs)

    @classmethod
    def aggregate(cls: Self | BaseModel, param: Any) -> Collection:
        """
        Агрегирование данных
        """
        return DBController(cls.__name__).table.aggregate(param)

    @classmethod
    async def is_exists(cls, **kwargs) -> bool:
        """
        Существуетс ли документ
        """
        documents = DBController(cls.__name__).table.count_documents(kwargs)
        return documents > 0


class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': '\033[94m', 'INFO': '\033[92m', 'WARNING': '\033[93m',
              'ERROR': '\033[91m', 'CRITICAL': '\033[95m'}

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(message)s\033[0m"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)