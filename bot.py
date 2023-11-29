import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from config_data.config import Config, load_config
from core.bot_core import BotApi, BotApiImpl
from core.database import BotDatabase, BotDatabaseImpl
from core.search import SearchEngine, TmdbSearchEngine, KpUnofficialSearchEngine
from core.scrapper import Scrapper, GoogleRestScrapper

# Инициализируем хранилище (создаем экземпляр класса RedisStorage)
redis = Redis(host='localhost',port=6379)
storage = RedisStorage(redis=redis)
logger = logging.getLogger(__name__)
dp = Dispatcher(storage=storage)

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


# Запускаем поллинг
if __name__ == '__main__':
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    database: BotDatabase = BotDatabaseImpl(config.database_path)
    engines: dict[str, SearchEngine] = {
        'kinopoisk': KpUnofficialSearchEngine(config.kp_unofficial_api_key),
        'tmdb': TmdbSearchEngine(config.tmpdb_api_key),
    }
    scrapper: Scrapper = GoogleRestScrapper(config.serp_api_key)
    core: BotApi = BotApiImpl(bot, database, engines, scrapper)

    known_commands: list[str] = ['start', 'help', 'search', 'stats', 'history']

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, parse_mode='MarkdownV2')
    dp.run_polling(bot)
