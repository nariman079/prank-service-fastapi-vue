import unittest.mock

import pytest
from unittest.mock import AsyncMock, patch

from tests.conftest import client
from backend.worker import send_image_and_video

def test_ping(client):
    """PING PONG"""
    value = "pong"
    assert 'pong' == value


async def mock_func(art: str):
    return {
        'type': 'test'
    }

@pytest.mark.asyncio
async def test_mocks():
    with patch('tests.integrations.test_send_media_task.mock_func', new_callable=AsyncMock) as mock_funcs:
        await mock_func('sd')
        mock_funcs.assert_called_once_with('sd')

# Пример функции для тестирования
import requests

def fetch_data_from_api(url):
    response = requests.post(url)
    return response.json()

@patch('requests.post')
def test_fetch_data_from_api(mock_get):
    mock_get.return_value.json.return_value = {"key": "value"}
    result = fetch_data_from_api('http://fakeurl.com')
    assert result == {"key": "value"}

@pytest.mark.asyncio
async def test_send_image_and_video():
    # Мок-данные для входных параметров
    files_path = {
        'video': 'tests/test_uploads/video.mp4',
        'image': 'tests/test_uploads/photo.png'
    }
    telegram_id = 1807334234

    # Мокаем зависимости
    with patch('backend.utils.convert_video', new_callable=AsyncMock) as mock_convert_video, \
            patch('backend.utils.send_file', new_callable=AsyncMock) as mock_send_file, \
            patch('backend.bot.drive.send_photo', new_callable=AsyncMock) as mock_send_photo:
        # Мокаем возвращаемое значение send_file
        mock_send_file.return_value.message_id = 98765  # Моковый message ID

        mock_filename = await send_image_and_video(files_path, telegram_id)

        # Проверяем, что convert_video был вызван с правильными аргументами
        mock_convert_video.assert_called_once_with(files_path['video'], new_file_name=mock_filename)

        # Проверяем, что send_file был вызван один раз с корректными параметрами
        mock_send_file.assert_called_once()
        assert mock_send_file.call_args[1]['telegram_id'] == telegram_id
        assert mock_send_file.call_args[1]['method'] == 'send_video_note'
        assert mock_send_file.call_args[1]['arg'] == 'video_note'

        # Проверяем вызов send_photo
        mock_send_photo.assert_called_once()
        assert mock_send_photo.call_args[1]['chat_id'] == telegram_id
        assert mock_send_photo.call_args[1]['photo'] == files_path['image']
        assert 'reply_markup' in mock_send_photo.call_args[1]

        # Проверяем данные в inline-кнопке
        reply_markup = mock_send_photo.call_args[1]['reply_markup']
        assert reply_markup.inline_keyboard[0][
                   0].callback_data == f"pranktrap_video:{mock_send_file.return_value.message_id}"