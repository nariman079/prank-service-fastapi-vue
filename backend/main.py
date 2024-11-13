from typing import Annotated
import aiofiles
from pathlib import Path

from fastapi import FastAPI, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.config import pranks
from backend.schemas import PrankStatistic
from backend.utils import symbols_to_number
from backend.worker import send_image_and_video_task

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_extension(filename:str) -> str:
    """Получение разширения файла"""
    sliced_filename = filename.split('.')
    if len(sliced_filename) >= 2:
        return "." + sliced_filename.pop(-1)
    return '.png'

async def hashing(value: str | int) -> str | int:
    """Прямое и обратное хеширование Telegram ID"""
    value = symbols_to_number(value)
    return value

@app.post("/api/v1/send_media/")
async def send_media(
    telegram_id: Annotated[int | str, Body()],
    video: UploadFile,
    image: UploadFile,
):
    path = Path('uploads')
    full_image_path = (path / image.filename, image)
    full_video_path = (path / video.filename, video)
    telegram_id = await hashing(telegram_id)
    logging.info(msg=f"DATA INFO: {full_image_path}, {full_video_path}, {telegram_id}")
    for file_name, file_obj in full_video_path, full_image_path:
        async with aiofiles.open(file_name, 'wb') as file:
            logging.info(f"WRITTEN FILES: {file.name}")
            await file.write(await file_obj.read())

    files_path = {
        'video': str(full_video_path[0]),
        'image': str(full_image_path[0])
    }
    send_image_and_video_task.apply_async((files_path, telegram_id))

    return {
        "image": image.filename
    }


@app.post("/api/v1/statistics/")
async def send_statistics(
        prank_stat: PrankStatistic
):
    prank_stat.telegram_id = await hashing(prank_stat.telegram_id)
    pranks.insert_one(prank_stat.dict())
    return prank_stat

@app.get("/api/v1/statistics")
async def send_statistics():
    moans = pranks.count_documents({'prank_type':'moan'})
    photo = pranks.count_documents({'prank_type': 'photo'})
    video = pranks.count_documents({'prank_type': 'video'})
    return {
        'photo':photo,
        'moan': moans,
        'video': video
    }