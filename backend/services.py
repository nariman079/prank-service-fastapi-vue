import logging
import os
from pathlib import Path

from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from backend.config import drive, TELEGRAM_GROUP_ID
from backend.utils import convert_video
from backend.schemas import Prank, PrankType, TelegramMessage


async def delete_file(filepath: str) -> bool | None:
    """Удаление файла"""
    try:
        os.remove(filepath)
        logging.info(f"Удаление файла: {filepath}")
        return True
    except Exception as exec:
        logging.error(f"Ошибка удаления файла {exec}")
        return False


async def send_photo(image_path: str, telegram_id: int | str) -> None:
    """
    Отправка фотографии в телеграм
    """
    logging.info(msg=f"Получение файла: {image_path}")
    message_uuid = Path(image_path).stem
    telegram_message = await TelegramMessage.get(message_uuid=message_uuid)
    logging.info(f"{message_uuid} {image_path} {Path(image_path).exists()}")
    if telegram_message:
        try:
            await drive.send_photo(
                chat_id=telegram_id,
                photo=FSInputFile(image_path),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            callback_data=f"video_message_id:{telegram_message.message_id}",
                            text="Посмотреть видео"
                        )]
                    ]
                )
            )
            logging.info("Завершение обработки изображения и отправки в телеграм бота")
            await Prank.create(
                telegram_id=str(telegram_id),
                prank_type=PrankType.photo
            )
            logging.info(f"Запись статистики: {PrankType.photo}")

            await delete_file(image_path)

        except Exception as error:
            logging.error(f"Ошибка отправки изображения: {error}")

async def send_chunk_video(video_path: str, telegram_id: int | str) -> str | None:
    """
    Отправка видео пользователю телергам
    """
    message_uuid = Path(video_path).stem
    new_file_name = str(Path('uploads', str(message_uuid) + '.mp4'))
    logging.info(msg=f"Получение файла: {new_file_name}")
    is_converted = await convert_video(video_path, new_file_name)
    if is_converted:
        try:
            video_message = await drive.send_video_note(
                video_note=FSInputFile(new_file_name),
                chat_id=TELEGRAM_GROUP_ID
            )
            await TelegramMessage.get_or_create(
                message_uuid=message_uuid,
                message_id=str(video_message.message_id)
            )
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
