# import aiohttp
# import asyncio
# import aiofiles
# async def send_media_request(url, telegram_id, video_path, image_path):
#     async with aiohttp.ClientSession() as session:
#         async with aiofiles.open(video_path, 'rb') as video_file, aiofiles.open(image_path, 'rb') as image_file:
#             form_data = aiohttp.FormData()
#             form_data.add_field('telegram_id', telegram_id)
#             form_data.add_field('video', video_file, filename='video.mp4', content_type='video/mp4')
#             form_data.add_field('image', image_file, filename='image.jpg', content_type='image/jpeg')
#
#             async with session.post(url, data=form_data) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     print("Response:", data)
#                 else:
#                     print("Failed to send media:", response.status, await response.text())
#
# # Параметры для отправки запроса
# url = "https://tiktok.copicon.ru/api/v1/send_media/"
# telegram_id = "BiaHddScdS"
# video_path = "tests/test_uploads/video.mp4"
# image_path = "tests/test_uploads/photo.png"
#
# # Запуск асинхронного запроса
# async def main():
#     async with asyncio.TaskGroup() as tg:
#         for i in range(10):
#             tg.create_task(send_media_request(url, telegram_id, video_path, image_path))
# #
# # asyncio.run(main())
import asyncio
import time
import random

last_chunk_time = dict()
active_tasks = dict()
INACTIVITY_TIMEOUT = 1

value = 0

async def add_chunk():
    filename = 'test'
    for i in range(10):
        last_chunk_time[filename] = time.time()
        await asyncio.sleep(random.randint(0, 2))
        print(filename not in active_tasks)
        print(active_tasks)
        print(filename)
        if filename not in active_tasks:
            task = asyncio.create_task(check_and_process_video('test'))
            active_tasks[filename] = task




async def check_and_process_video(
        filename: str,
        telegram_id: str | None = None
) -> None:
    """Проверка и обработка полученного видео"""

    await asyncio.sleep(INACTIVITY_TIMEOUT-0.2)

    while True:
        print(time.time() - last_chunk_time.get(filename, 0))
        if time.time() - last_chunk_time.get(filename, 0) >= INACTIVITY_TIMEOUT:
            print(f"Start processing task for {filename}")
            # send_chunk_video_task.apply_async((str(file_path), telegram_id))
            last_chunk_time.pop(filename, None)
            print(active_tasks)
            active_tasks.pop(filename, None)
            print(active_tasks)
            break
        else:
            print(f"New chunk received for {filename}, delaying processing")
            await asyncio.sleep(INACTIVITY_TIMEOUT-0.2)

async def main():
    await add_chunk()
# asyncio.run(main())