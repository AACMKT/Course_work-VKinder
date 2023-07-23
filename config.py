import os
from dotenv import load_dotenv


# Подгружаем из переменных окружения, локально будут храниться токены в файл .env
load_dotenv()
token_vk = os.getenv('token_vk')
token_soob = os.getenv('token_soob')
group_id = os.getenv('group_id')
database = os.getenv('database')
user = os.getenv('user')
password = os.getenv('password')

