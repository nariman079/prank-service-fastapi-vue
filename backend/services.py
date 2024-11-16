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
    logging.info(msg=f"Получение файла: {image_path}")
    try:
        await drive.send_photo(
            chat_id=telegram_id,
            photo=FSInputFile(image_path)
        )
        logging.info("Завершение обработки изображения и отправки в телеграм бота")
        await Prank.create(
            telegram_id=str(telegram_id),
            prank_type=PrankType.photo
        )
        logging.info(f"Запись статистики: {PrankType.photo}")
    except Exception as error:
        logging.error(f"Ошибка отправки изображения: {error}")


async def send_chunk_video(video_path: str, telegram_id: int | str) -> str | None:
    """
    Отправка видео пользователю телергам
    """
    new_file_name = str(Path('uploads', str(uuid4()) + '.mp4'))
    logging.info(msg=f"Получение файла: {new_file_name}")
    is_converted = await convert_video(video_path, new_file_name)
    if is_converted:
        try:
            await drive.send_video_note(
                video_note=FSInputFile(new_file_name),
                chat_id=telegram_id
            )
            logging.info("Завершение обработки сегмента видео и отправка в телеграм бота")
            await Prank.create(
                telegram_id=str(telegram_id),
                prank_type=PrankType.video
            )
            logging.debug(f"Запись статистики: {PrankType.video}")
        except Exception as error:
            logging.error(f"Ошибка отправки видео: {error}")
            return
    else:
        logging.error("Не удалось конвертировать файл")
    return new_file_name
