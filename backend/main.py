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

from backend.config import path
from backend.schemas import PrankStatistic, User
from backend.utils import hashing, send_message_to_telegram
from backend.worker import send_image_and_video_task, send_chunk_video_task

logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)

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



@app.exception_handler(Exception)
async def exception_handler(
        request: Request,
        exc: Exception
) -> JSONResponse:
    """Обработка исключений"""
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'message': "Internal server error"
        }
    )



@app.middleware("http")
async def send_response_to_telegram(request: Request, call_next) -> Response:
    """Отрпрака сообщения о запросе"""
    response = await call_next(request)

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    message = (
        f"IP: {request.client.host}"
        f"User-Agent: {request.headers.get('User-Agent')}"
        f"Request URL: {request.url}\n"
        f"Status Code: {response.status_code}\n"
        f"Response Body: \n{response_body.decode('utf-8')}\n"
    )
    logging.info(message)
    # await send_message_to_telegram(message)

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
async def send_media(
        telegram_id: Annotated[int | str, Body()],
        video: UploadFile,
):
    """Обработки сегментов видеопотока"""
    file_path, file_obj = (path / video.filename, video)
    telegram_id = await hashing(telegram_id)

    # Запись времени получения сегмнета
    last_chunk_time[video.filename] = time.time()

    async with aiofiles.open(file_path, 'ab') as file:
        await file.write(await file_obj.read())


    if video.filename not in active_tasks:
        # Запуск асинхронной задачи для обработки полученного сегмента
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
    """Проверка и обработка полученного видео"""
    await asyncio.sleep(INACTIVITY_TIMEOUT - 0.2)
    while True:
        if time.time() - last_chunk_time.get(filename, 0) >= INACTIVITY_TIMEOUT:
            send_chunk_video_task.delay(str(file_path), telegram_id)
            last_chunk_time.pop(filename, None)
            active_tasks.pop(filename, None)
            break
        else:
            print(f"New chunk received for {filename}, delaying processing")
            await asyncio.sleep(INACTIVITY_TIMEOUT - 0.2)


@app.post("/api/v1/send_image/")
async def send_media(
        telegram_id: Annotated[int | str, Body()],
        video: UploadFile,
):
    file_name, file_obj = (path / video.filename, video)
    telegram_id = await hashing(telegram_id)

    async with aiofiles.open(file_name, 'wb') as file:
        await file.write(await file_obj.read())

    send_chunk_video_task.apply_async((str(file_name), telegram_id))

    return {
        "image": video.filename
    }

#
# @app.post("/api/v1/statistics/")
# async def send_statistics(
#         prank_stat: PrankStatistic
# ):
#     prank_stat.telegram_id = await hashing(prank_stat.telegram_id)
#     pranks.insert_one(prank_stat.dict())
#     return prank_stat
#
#
# @app.get("/api/v1/statistics")
# async def send_statistics():
#     moans = pranks.count_documents({'prank_type': 'moan'})
#     photo = pranks.count_documents({'prank_type': 'photo'})
#     video = pranks.count_documents({'prank_type': 'video'})
#     return {
#         'photo': photo,
#         'moan': moans,
#         'video': video
#     }
