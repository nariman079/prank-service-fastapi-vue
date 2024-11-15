import logging
from pathlib import Path
from uuid import uuid4

from aiogram.types import FSInputFile

from backend.config import drive
from backend.utils import convert_video
from backend.schemas import Prank, PrankType





async def send_photo(image_path: str, telegram_id: int | str) -> None:
    """
    Отправка фотографии в телеграм
    """
    logging.info(msg=f"FILE NAME: {image_path}")
    try:
        await drive.send_photo(
            chat_id=telegram_id,
            photo=FSInputFile(image_path)
        )
        await Prank.create(
            telegram_id=telegram_id,
            prank_type=PrankType.photo
        )
    except Exception as error:
        logging.error(f"Error by send photo: {error}")


async def send_chunk_video(video_path: str, telegram_id: int | str) -> str:
    """
    Отправка видео пользователю телергам
    """
    new_file_name = str(Path('uploads', str(uuid4()) + '.mp4'))
    logging.info(msg=f"Getting file: {new_file_name}")
    is_converted = await convert_video(video_path, new_file_name)
    if is_converted:
        try:
            await drive.send_video_note(
                video_note=FSInputFile(new_file_name),
                chat_id=telegram_id
            )
            await Prank.create(
                telegram_id=telegram_id,
                prank_type=PrankType.video
            )
        except Exception as error:
            logging.error(f"Error by send video: {error}")
    else:
        logging.error("Не удалось конвертировать файл")
    return new_file_name
