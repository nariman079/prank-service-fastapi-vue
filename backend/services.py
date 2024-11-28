import logging
import os
from pathlib import Path

from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from backend.config import drive, TELEGRAM_GROUP_ID
from backend.utils import convert_video, capture_middle_frame
from backend.schemas import Prank, PrankType, TelegramMessage


async def delete_file(message_uuid: str) -> None:
    """Удаление файла"""
    if os.path.exists('uploads') and os.path.isdir('uploads'):
        for file_name in os.listdir('uploads'):
            file_path = os.path.join('uploads', file_name)
            if os.path.isfile(file_path) and message_uuid in file_name:
                try:
                    os.remove(file_path)
                    logging.info(f"Удален файл: {file_path}")
                except Exception as e:
                    logging.error(f"Ошибка при удалении {file_path}: {e}")
    else:
        logging.error("Папка uploads не существует или не является директорией.")


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
            logging.info("Завершение обработки сегмента видео и отправка в телеграм бота")
            new_image_path = await capture_middle_frame(new_file_name, message_uuid)
            if new_image_path:
                await drive.send_photo(
                    chat_id=telegram_id,
                    photo=FSInputFile(new_image_path),
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(
                                callback_data=f"video_message_id:{video_message.message_id}",
                                text="Посмотреть видео"
                            )]
                        ]
                    )
                )
            logging.info("Завершение обработки изображения  и отправка в телеграм пользователя")
            await Prank.create(
                telegram_id=str(telegram_id),
                prank_type=PrankType.video
            )
            logging.info(f"Запись статистики: {PrankType.video}")
            await delete_file(message_uuid)
        except Exception as error:
            logging.error(f"Ошибка отправки видео или изображения: {error}")
            return
    else:
        logging.error("Не удалось конвертировать файл")
    return new_file_name
