import logging
from pathlib import Path

import httpagentparser
from ffmpeg.asyncio import FFmpeg
from ffmpeg.errors import FFmpegError
from moviepy import VideoFileClip

from backend.config import drive


def symbols_to_number(symbols: str) -> int:
    reverse_mapping = {
        'a': '0',
        'B': '1',
        'c': '2',
        'd': '3',
        'S': '4',
        'F': '5',
        'g': '6',
        'H': '7',
        'i': '8',
        'J': '9'
    }

    number_str = ''.join(reverse_mapping[symbol] for symbol in symbols)

    return int(number_str)



def number_to_symbols(number: int) -> str:
    mapping = {
        '0': 'a',
        '1': 'B',
        '2': 'c',
        '3': 'd',
        '4': 'S',
        '5': 'F',
        '6': 'g',
        '7': 'H',
        '8': 'i',
        '9': 'J'
    }
    number_str = str(number)

    symbol_str = ''.join(mapping[digit] for digit in number_str)

    return symbol_str


async def convert_video(
        filename:str,
        new_file_name: str
) -> bool | None:
    """Конвертация полученного файла для отправки в телеграм"""
    if Path(new_file_name).exists():
        return True
    try:
        ffmpeg = (
            FFmpeg()
            .option("y")  # добавляет флаг "yes", чтобы перезаписывать файлы
            .input(filename)  # здесь используется исходный файл
            .output(
                new_file_name,  # имя выходного файла
                {"codec:v": "libx264", "codec:a": "aac"},  # кодеки видео и аудио
                movflags="+faststart",  # флаг для быстрой загрузки
                strict="experimental",  # для поддержки экспериментальных параметров
            )
        )
        await ffmpeg.execute()
        return True
    except FFmpegError as e:
        print(f"Ошибка при перекодировании: {e}")
        return False

async def get_extension(filename: str) -> str:
    """Получение раcширения файла"""
    sliced_filename = filename.split('.')
    if len(sliced_filename) >= 2:
        return "." + sliced_filename.pop(-1)
    return '.png'


async def hashing(value: str | int) -> str | int:
    """Прямое и обратное хеширование Telegram ID"""
    value = symbols_to_number(value)
    return value


async def send_message_to_telegram(message: str) -> None:
    """Обправка сообщения администратору"""
    payload = {"chat_id": 1807334234,  "text": message}
    try:
        await drive.send_message(**payload)
    except Exception as error:
        logging.error(f"Не удалось отправить сообщение в Telegram: {error}", )


def parse_user_agent(user_agent) -> dict | None:
    """Извлекает данные из строки User-Agent."""
    try:
        parsed_data = httpagentparser.detect(user_agent)
        browser = parsed_data.get('browser', {})
        os = parsed_data.get('platform', {})

        return {
            "browser_name": browser.get('name', None),
            "browser_version": browser.get('version', None),
            "os_name": os.get('name', None),
            "os_version": os.get('version', None),
            "device": parsed_data.get('flavor', None)
        }
    except Exception as error:
        logging.error(f"Failed to parse user agent: {str(error)}")






async def capture_middle_frame(video_path, video_name) -> str | None:
    """Запись скриншота из середины видео"""
    try:
        new_video_name = f"{video_name}.jpg"
        clip = VideoFileClip(video_path)
        middle_time = clip.duration / 3
        frame = clip.get_frame(middle_time)
        from PIL import Image
        image = Image.fromarray(frame)
        image.save(f'uploads/{new_video_name}')
        logging.info(f"Скриншот сохранён: {video_name}")
        return f'uploads/{new_video_name}'
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return None