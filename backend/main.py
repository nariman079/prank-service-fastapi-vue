import asyncio
import time
from typing import Annotated
import aiofiles
from pathlib import Path

from fastapi import FastAPI, UploadFile, Body, Response
from fastapi.middleware.cors import CORSMiddleware
import logging

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from backend.config import path, ColoredFormatter
from backend.schemas import User, Prank, PrankType, Error
from backend.utils import hashing
from backend.worker import send_chunk_video_task, send_photo_task

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:', handlers=[logging.StreamHandler()])
logging.getLogger().handlers[0].setFormatter(ColoredFormatter())

last_chunk_time = dict()
active_tasks = dict()

INACTIVITY_TIMEOUT = 3
ATTEMPT = 10

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def exception_handler(
        request: Request,
        exc: Exception
) -> JSONResponse:
    """
    Обработка исключений
    """
    headers = request.headers
    ip = request.client.host

    await Error.create(
        ip=ip,
        headers=headers,
        exception_data=str(exc),
        exception_args=exc.args
    )
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'message': "Internal server error"
        }
    )

@app.middleware("http")
async def send_response_to_telegram(request: Request, call_next) -> Response:
    """
    Отправка сообщения о запросе
    """
    response = await call_next(request)

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    message = (
        f"IP: {request.client.host}\n"
        f"User-Agent: {request.headers.get('User-Agent')}\n"
        f"Request URL: {request.url}\n"
        f"Status Code: {response.status_code}\n"
        f"Response Body: \n{response_body.decode('utf-8')}\n"
    )
    logging.info(message)

    user = await User.is_exists(ip=request.client.host)
    if not user:
        await User.create(
            ip=request.client.host,
            user_agent=request.headers.get('User-Agent')
        )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@app.post("/api/v1/send_chunk/")
async def send_chunks(
        telegram_id: Annotated[int | str, Body()],
        video: UploadFile,
):
    """Обработка сегментов видеопотока"""
    logging.info("Обработки сегментов видеопотока")

    file_path, file_obj = (path / video.filename, video)
    telegram_id = await hashing(telegram_id)

    logging.info(f"Запись времени получения сегмнета: {file_path}")
    last_chunk_time[video.filename] = time.time()

    async with aiofiles.open(file_path, 'ab') as file:
        await file.write(await file_obj.read())

    if video.filename not in active_tasks:
        logging.info(f"Запуск асинхронной задачи для обработки полученного сегмента: {video.filename}")
        task = asyncio.create_task(
            check_and_process_video(
                video.filename,
                file_path,
                telegram_id
            )
        )
        active_tasks[video.filename] = task

    return {
        "image": video.filename
    }

async def check_and_process_video(
        filename: str,
        file_path: Path,
        telegram_id: str
) -> None:
    """
    Проверка и обработка полученного видео
    """
    await asyncio.sleep(INACTIVITY_TIMEOUT)
    while True:
        if time.time() - last_chunk_time.get(filename, 0) >= INACTIVITY_TIMEOUT:
            logging.info(f"Запуск асинхронной задачи по обработке сегмента видео: {filename}")
            send_chunk_video_task.apply_async((str(file_path), telegram_id))
            last_chunk_time.pop(filename, None)
            active_tasks.pop(filename, None)
            break
        else:
            logging.warning(f"Ожидание завершения получения сегмена видео: {filename}")
            await asyncio.sleep(INACTIVITY_TIMEOUT)

async def check_and_process_image(
        filename: str,
        file_path: Path,
        telegram_id: str
) -> None:
    """
    Проверка и обработка полученного изображения
    """
    await asyncio.sleep(INACTIVITY_TIMEOUT+1)
    current_attempt = 0
    while True:
        file = Path(f"uploads/{file_path.stem}.mp4")

        if file.exists():
            logging.info(f"Запуск асинхронной задачи по обработке изображения: {filename}")
            send_photo_task.apply_async((str(file_path), telegram_id))
            break
        else:
            logging.warning(f"Ожидание завершения получения изображения: {filename}")

            # Завершение цикла когда совершено 10 попыток найти изображение
            current_attempt += 1
            if current_attempt >= ATTEMPT:
                break

            await asyncio.sleep(INACTIVITY_TIMEOUT+1)

@app.post("/api/v1/send_image/")
async def send_image(
        telegram_id: Annotated[int | str, Body()],
        image: UploadFile,
):
    """Обработка изображения"""
    logging.info("Обработка изображения")
    file_name, file_obj = (path / image.filename, image)
    telegram_id = await hashing(telegram_id)

    async with aiofiles.open(file_name, 'wb') as file:
        await file.write(await file_obj.read())

    logging.info(f"Запуск асинхронной задачи по обработке изображения: {str(file_name)}")
    asyncio.create_task(check_and_process_image(image.filename, file_name, telegram_id))

    return {"image": image.filename}

@app.post("/api/v1/statistics/add_moan/")
async def send_statistics(telegram_id_hash: str | int):
    """
    Добавление статистики о Moan
    """
    telegram_id = await hashing(telegram_id_hash)
    await Prank.create(
        telegram_id=str(telegram_id),
        prank_type=PrankType.moan
    )
    return {
        "message": "Статистика добавлена"
    }

@app.get("/api/v1/statistics")
async def get_statistics():
    """
    Получение статистики
    """
    statistic = Prank.aggregate(
        [{
            "$group": {
                "_id": "$prank_type",
                "count": {"$sum": 1}
            }
        }]
    )
    return {
        item["_id"]: item["count"]
        for item in statistic
    }

