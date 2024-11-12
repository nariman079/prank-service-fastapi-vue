import json

import requests

# Настройки
outline_server_url = ""  # Замените на IP-адрес и порт вашего сервера Outline
access_key = ""  # Замените на ваш ключ управления

from decouple import config
from outline_vpn.outline_vpn import OutlineVPN