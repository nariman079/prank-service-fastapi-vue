from pathlib import Path


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
