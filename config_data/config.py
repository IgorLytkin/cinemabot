from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str          # Токен для доступа к телеграм-боту
    database_path: str  # Путь к базе данных SQL Lite
    kp_unofficial_api_key: str # Ключ для неофициального API Кинопоиск
    tmpdb_api_key: str  # Ключ для API TMPDB
    serp_api_key: str   # Ключ для SERP API

@dataclass
class Config:
    tg_bot: TgBot


# Создаем функцию, которая будет читать файл .env и возвращать
# экземпляр класса Config с заполненными полями
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            database_path=env('DATABASE_PATH'),
            kp_unofficial_api_key=env('KP_UNOFFICIAL_API_KEY'),
            tmpdb_api_key=env('TMDB_API_KEY'),
            serp_api_key=env('SERP_API_KEY')

        )
    )