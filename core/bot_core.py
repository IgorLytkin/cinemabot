from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from aiogram import Bot, types
from .constants import HELP_MESSAGE, START_MESSAGE, UNKNOWN_COMMAND_MESSAGE, RESULT_NONE_MESSAGE
from .database import BotDatabase
from .structs import SearchEntity, Movie, Banner, StatsEntity
from .search import SearchEngine
from .helpers import merge_movies, movie_to_banner, first_non_none
from .scrapper import Scrapper


class BotApi(ABC):

    @abstractmethod
    async def process_start_command(self, message: types.Message) -> None:
        await message.answer(
            text='Этот бот пытается найти для Вас кино\n\n'
                 'Чтобы перейти к поиску - введите ключевые слова и нажмите Enter'
        )

    @abstractmethod
    async def process_help_command(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def process_history_command(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def process_stats_command(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def process_search_command(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def process_unknown_command(self, message: types.Message) -> None:
        pass


class BotApiImpl(BotApi):
    sites_to_watch_online: list[str] = ["kinogo.biz", "rezka.ag"]

    def __init__(self, bot: Bot, database: BotDatabase, engines: dict[str, SearchEngine], scrapper: Scrapper):
        self.bot = bot
        self.database = database
        self.engines = engines
        self.scrapper = scrapper

    async def process_start_command(self, message: types.Message) -> None:
        await self.bot.send_message(message.chat.id, START_MESSAGE)

    async def process_help_command(self, message: types.Message) -> None:
        await self.bot.send_message(message.chat.id, HELP_MESSAGE)

    async def process_history_command(self, message: types.Message) -> None:
        history: list[SearchEntity] = await self.database.load_search_entities(message.chat.id)
        result = '\n'.join(reversed([self._search_entity_to_str(item) for item in history]))
        await self.bot.send_message(message.chat.id, result)

    async def process_stats_command(self, message: types.Message) -> None:
        stats: list[StatsEntity] = await self.database.load_stats_entities(message.chat.id)
        stats = sorted(stats, key=lambda item: -item.count)
        result = '\n'.join([self._stats_entity_to_str(item) for item in stats])
        await self.bot.send_message(message.chat.id, result)

    async def process_search_command(self, message: types.Message) -> None:
        result: Optional[Movie] = None
        result_kp: Optional[Movie] = await self.engines['kinopoisk'].search_movie(message.get_args())
        result_tmdb: Optional[Movie] = await self.engines['tmdb'].search_movie(message.get_args())
        if not result_kp:
            if not result_tmdb:
                await self.bot.send_message(message.chat.id, RESULT_NONE_MESSAGE)
                return
        if result_kp and result_tmdb and result_kp.id_imdb == result_tmdb.id_imdb:
            result = merge_movies([result_kp, result_tmdb])
        else:
            result = first_non_none([result_kp, result_tmdb])
        if result is None:
            await self.bot.send_message(message.chat.id, RESULT_NONE_MESSAGE)
            return
        result.links_to_watch = [await self.scrapper.get_top_link(result.title, site) for site in
                                 self.sites_to_watch_online]
        banner: Banner = movie_to_banner(result)
        if banner.picture:
            await self.bot.send_photo(message.chat.id, banner.picture, caption=banner.text, parse_mode='Markdown')
        else:
            await self.bot.send_message(message.chat.id, banner.text, parse_mode='Markdown')
        search_entity = SearchEntity(message.chat.id, message.get_args(), result.title, datetime.now(), result.id_kp,
                                     result.id_tmdb)
        await self.database.save_search_entity(search_entity)

    async def process_unknown_command(self, message: types.Message) -> None:
        await message.reply(UNKNOWN_COMMAND_MESSAGE)

    @staticmethod
    def _search_entity_to_str(entity: SearchEntity) -> str:
        return f'{entity.datetime}: {entity.text} -> "{entity.title}"'

    @staticmethod
    def _stats_entity_to_str(entity: StatsEntity) -> str:
        return f'{entity.title}: {entity.count}'
