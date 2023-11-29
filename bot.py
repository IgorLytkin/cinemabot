import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, StateFilter
# from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis

from aiogram.types import (Message)

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

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_age = State()         # Состояние ожидания ввода возраста
    fill_gender = State()      # Состояние ожидания выбора пола
    upload_photo = State()     # Состояние ожидания загрузки фото
    fill_education = State()   # Состояние ожидания выбора образования
    fill_wish_news = State()   # Состояние ожидания выбора получать ли новости

@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await core.process_start_command(message)


@dp.message(Command(commands='help'), StateFilter(default_state))
async def handle_help_command(message: Message):
    await core.process_help_command(message)


# Этот хэндлер будет срабатывать на команду "/search" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='search'), StateFilter(default_state))
async def process_search_command(message: Message):
    await core.process_search_command(message)


# Этот хэндлер будет срабатывать на команду "/stats" в состоянии
# по умолчанию и сообщать статистику использования бота
@dp.message(Command(commands='stats'), StateFilter(default_state))
async def process_stats_command(message: Message):
    await core.process_stats_command(message)


@dp.message(Command(commands='history'), StateFilter(default_state))
async def handle_history_command(message: Message):
    await core.process_history_command(message)


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, моя твоя не понимать')


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
    known_commands: list[str] = ['start', 'help', 'search', 'stats', 'history']

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, parse_mode='MarkdownV2')
    core: BotApi = BotApiImpl(bot, database, engines, scrapper)
    dp.run_polling(bot)
