import asyncio
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from aiogram.types import FSInputFile, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from celery import Celery
from dotenv import load_dotenv

from backend.config import drive, pranks, TELEGRAM_GROUP_ID
from backend.schemas import PrankStatistic, PrankType, PrankCreateStatistic
from backend.utils import  convert_video

load_dotenv()

app = Celery(__name__)
app.conf.broker_url = os.getenv("REDIS_HOST")
app.conf.result_backend = os.getenv("REDIS_HOST")

async def send_image(
    filepath: str,
    telegram_id: int | str
) -> None:
    await drive.send_photo(
        chat_id=telegram_id,
        photo=FSInputFile(filepath)
    )

async def send_images_media_group(
        image_path_list: list[str],
        telegram_id: int | str
) -> None:
    media_group_images = [InputMediaPhoto(type='photo',media = FSInputFile(i)) for i in image_path_list[:10]]
    await drive.send_media_group(
        chat_id=telegram_id,
        media=media_group_images
    )


async def send_image_and_video(
        files_path: dict[str, str],
        telegram_id: int | str
) -> str:
    new_file_name = str(Path('uploads', str(uuid4()) + '.mp4'))
    # await convert_video(
    #     files_path['video'],
    #     new_file_name=new_file_name
    # )
    video_message = await drive.send_video_note(
        video_note=FSInputFile(new_file_name),
        chat_id=TELEGRAM_GROUP_ID
    )
    pranks.insert_one(
        PrankCreateStatistic(
            telegram_id=telegram_id,
            date_create=datetime.utcnow(),
            prank_type=PrankType.video
        ).dict()
    )
    await drive.send_photo(
        chat_id=telegram_id,
        photo=FSInputFile(files_path['image']),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Посмотреть видео",
                        callback_data=f"pranktrap_video:{video_message.message_id}"
                    )
                ]
            ]
        )
    )
    pranks.insert_one(
        PrankCreateStatistic(
            telegram_id=telegram_id,
            date_create=datetime.utcnow(),
            prank_type=PrankType.photo
        ).dict()
    )
    return new_file_name

@app.task
def send_image_and_video_task(
        files_path: dict[str, str],
        telegram_id: int | str
) -> None:
    """Отправка видео и фото одновременно"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_image_and_video(files_path, telegram_id))