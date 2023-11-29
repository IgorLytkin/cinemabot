import os

from aiogram import Bot, types, Dispatcher, executor
from dotenv import load_dotenv
from core.bot_core import BotApi, BotApiImpl
from core.database import BotDatabase, BotDatabaseImpl
from core.search import SearchEngine, TmdbSearchEngine, KpUnofficialSearchEngine
from core.scrapper import Scrapper, GoogleRestScrapper

load_dotenv()

bot = Bot(token=os.environ['TELEGRAM_API_KEY'])
dp = Dispatcher(bot)

database: BotDatabase = BotDatabaseImpl(os.environ['DATABASE_PATH'])
engines: dict[str, SearchEngine] = {
    'kinopoisk': KpUnofficialSearchEngine(os.environ['KP_UNOFFICIAL_API_KEY']),
    'tmdb': TmdbSearchEngine(os.environ['TMDB_API_KEY']),
}
scrapper: Scrapper = GoogleRestScrapper(os.environ['SERP_API_KEY'])
core: BotApi = BotApiImpl(bot, database, engines, scrapper)

known_commands: list[str] = ['start', 'help', 'search', 'stats', 'history']


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    await core.handle_start(message)


@dp.message_handler(commands=['help'])
async def handle_help(message: types.Message):
    await core.handle_help(message)


@dp.message_handler(commands=['search'])
async def handle_search(message: types.Message):
    await core.handle_search(message)


@dp.message_handler(commands=['stats'])
async def handle_stats(message: types.Message):
    await core.handle_stats(message)


@dp.message_handler(commands=['history'])
async def handle_stats(message: types.Message):
    await core.handle_history(message)


@dp.message_handler()
async def handle_unknown(message: types.Message):
    await core.handle_unknown(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
