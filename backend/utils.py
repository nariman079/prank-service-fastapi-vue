from aiogram import Bot
from aiogram.types import Message, FSInputFile
from ffmpeg.asyncio import FFmpeg
from ffmpeg.errors import FFmpegError

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


async def send_file(
        bot: Bot,
        file_path: str,
        telegram_id: str | int,
        method: str,
        arg: str
) -> Message:
    """ Первоклассная функция для отправки фа"""
    key_args = {
        'chat_id':telegram_id,
        arg: FSInputFile(file_path)
    }
    return await getattr(bot, method)(**key_args)


async def convert_video(
        filename:str,
        new_file_name: str
) -> None:
    """Конвертация полученного файла для отправки в телеграм"""
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
    except FFmpegError as e:
        print(f"Ошибка при перекодировании: {e}")
