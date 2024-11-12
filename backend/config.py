import os

from pymongo import MongoClient
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DB_URL = os.getenv('DB_URL')

client = MongoClient(
    DB_URL
)

db = client['Statistic']
pranks = db['Pranks']



drive = Bot(TOKEN)
