import asyncio
import logging
from pathlib import Path
from uuid import uuid4

from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from backend.config import drive
from backend.utils import convert_video
from backend.schemas import Prank, PrankType

messages = dict()

async def send_photo(image_path: str, telegram_id: int | str) -> None:
    """
    Отправка фотографии в телеграм
    """
    logging.info(msg=f"Получение файла: {image_path}")
    message_uuid = Path(image_path).stem
    while True:
        await asyncio.sleep(1)
        message_id = messages.get(message_uuid, None)

        if message_id:
            try:
                await drive.send_photo(
                    chat_id=telegram_id,
                    photo=FSInputFile(image_path),
                    reply_markup=InlineKeyboardMarkup(
                        keyboard=[
                            InlineKeyboardButton(
                                url=f"https://{message_id}",
                                text="Посмотреть видео"
                            )
                        ]
                    )
                )
                logging.info("Завершение обработки изображения и отправки в телеграм бота")
                await Prank.create(
                    telegram_id=str(telegram_id),
                    prank_type=PrankType.photo
                )
                logging.info(f"Запись статистики: {PrankType.photo}")
            except Exception as error:
                logging.error(f"Ошибка отправки изображения: {error}")
        else:
            logging.warning(f"Не найден ID сообщения: {message_uuid}")
            pass

async def send_chunk_video(video_path: str, telegram_id: int | str) -> str | None:
    """
    Отправка видео пользователю телергам
    """
    new_file_name = str(Path('uploads', str(uuid4()) + '.mp4'))
    logging.info(msg=f"Получение файла: {new_file_name}")
    message_uuid = Path(video_path).stem
    is_converted = await convert_video(video_path, new_file_name)
    if is_converted:
        try:
            video_message = await drive.send_video_note(
                video_note=FSInputFile(new_file_name),
                chat_id=telegram_id
            )
            messages[message_uuid] = video_message.message_id
            logging.info("Завершение обработки сегмента видео и отправка в телеграм бота")
            await Prank.create(
                telegram_id=str(telegram_id),
                prank_type=PrankType.video
            )
            logging.info(f"Запись статистики: {PrankType.video}")
        except Exception as error:
            logging.error(f"Ошибка отправки видео: {error}")
            return
    else:
        logging.error("Не удалось конвертировать файл")
    return new_file_name
