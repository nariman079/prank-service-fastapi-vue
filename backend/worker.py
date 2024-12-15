import asyncio
import os

from celery import Celery
from dotenv import load_dotenv

from backend.services import send_photo, send_chunk_video

load_dotenv()

app = Celery(__name__)
app.conf.broker_url = os.getenv("REDIS_FULL_URL")
app.conf.result_backend = os.getenv("REDIS_FULL_URL")


@app.task
def send_photo_task(
        image_path: str,
        telegram_id: int | str
) -> None:
    """
    Асинхронная задача для отправки фото
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_photo(image_path, telegram_id))

@app.task
def send_chunk_video_task(
        video_path: str,
        telegram_id: int
) -> None:
    """
    Асирхронная задача для отправки видео
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_chunk_video(video_path, telegram_id))