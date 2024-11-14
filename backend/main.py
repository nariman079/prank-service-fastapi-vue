import asyncio
import time
from typing import Annotated
import aiofiles
from pathlib import Path

from fastapi import FastAPI, UploadFile, Body, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from starlette.requests import Request

from backend.config import pranks, drive
from backend.schemas import PrankStatistic
from backend.utils import symbols_to_number
from backend.worker import send_image_and_video_task, send_chunk_video_task

last_chunk_time = dict()
active_tasks = dict()

INACTIVITY_TIMEOUT = 1

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(filename="backend.logs")

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

async def send_message_to_telegram(message: str):
    payload = {
        "chat_id": 1807334234,
        "text": message,
    }
    try:
        await drive.send_message(**payload)
    except:
        print("Не удалось отправить сообщение в Telegram:")

@app.middleware("http")
async def send_response_to_telegram(request: Request, call_next):
    response = await call_next(request)

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    message = (
        f"Request URL: {request.url}\n"
        f"Status Code: {response.status_code}\n"
        f"Response Body: \n{response_body.decode('utf-8')}\n"
    )

    await send_message_to_telegram(message)

    return Response(content=response_body, status_code=response.status_code, headers=dict(response.headers))


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
    print(f"DATA INFO: {full_image_path}, {full_video_path}, {telegram_id}")

    for file_name, file_obj in full_video_path, full_image_path:
        async with aiofiles.open(file_name, 'wb') as file:
            print(f"WRITTEN FILES: {file.name}")
            await file.write(await file_obj.read())

    files_path = {
        'video': str(full_video_path[0]),
        'image': str(full_image_path[0])
    }
    send_image_and_video_task.apply_async((files_path, telegram_id))

    return {
        "video": image.filename
    }


@app.post("/api/v1/send_chunk/")
async def send_media(
    telegram_id: Annotated[int | str, Body()],
    video: UploadFile,
):
    """Обработки сегментов видеопотока"""
    path = Path('uploads')
    file_path, file_obj = (path / video.filename, video)
    telegram_id = await hashing(telegram_id)

    last_chunk_time[video.filename] = time.time()

    logging.warning(f"DATA INFO: {file_path}, {telegram_id}")

    async with aiofiles.open(file_path, 'ab') as file:
        logging.warning(f"WRIT FILES: {file.name}")
        await file.write(await file_obj.read())
    print(active_tasks)
    if video.filename not in active_tasks:
        task = asyncio.create_task(check_and_process_video(video.filename, telegram_id ))
        active_tasks[video.filename] = task

    # asyncio.create_task(check_and_process_video(file_path, telegram_id))

    return {
        "image": video.filename
    }


async def check_and_process_video(filename: str, telegram_id: str) -> None:
    """Проверка и обработка полученного видео"""
    await asyncio.sleep(INACTIVITY_TIMEOUT - 0.2)
    while True:
        if time.time() - last_chunk_time.get(filename, 0) >= INACTIVITY_TIMEOUT:
            print(f"Start processing task for {filename}")
            send_chunk_video_task.delay(filename, telegram_id)
            print(f"End processing task for {filename}")
            print(last_chunk_time, active_tasks)
            last_chunk_time.pop(filename, None)
            active_tasks.pop(filename, None)
            print(last_chunk_time, active_tasks)
            break
        else:
            print(f"New chunk received for {filename}, delaying processing")
            await asyncio.sleep(INACTIVITY_TIMEOUT -  0.2)


@app.post("/api/v1/send_image/")
async def send_media(
    telegram_id: Annotated[int | str, Body()],
    video: UploadFile,
):
    path = Path('uploads')
    file_name, file_obj = (path / video.filename, video)
    telegram_id = await hashing(telegram_id)
    print(f"DATA INFO: {file_name}, {telegram_id}")

    async with aiofiles.open(file_name, 'ab') as file:
        print(f"WRITTEN FILES: {file.name}")
        await file.write(await file_obj.read())


    send_chunk_video_task.apply_async((str(file_name), telegram_id))

    return {
        "image": video.filename
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
