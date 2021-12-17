import asyncio
import datetime
from abc import ABC, abstractmethod
from typing import Optional

from aiogram import types
from .structs import SearchEntity, StatsEntity
import aiosqlite


class BotDatabase(ABC):

    @abstractmethod
    async def save_search_entity(self, entity: SearchEntity) -> None:
        pass

    @abstractmethod
    async def load_search_entities(self, chat_id: types.base.Integer) -> list[SearchEntity]:
        pass

    @abstractmethod
    async def load_stats_entities(self, chat_id: types.base.Integer) -> list[StatsEntity]:
        pass


_sql_requests: dict[str, str] = {
    'table_exists': "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';",
    'create_table_history': "CREATE TABLE history (chat_id INTEGER, text STRING, title STRING, search_time TIMESTAMP, kp_id INTEGER, tmdb_id INTEGER)",
    'save_search_entity': "INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)",
    'load_search_entities': "SELECT chat_id, text, title, search_time, kp_id, tmdb_id FROM history WHERE chat_id = {}",
    'load_stats_entities': "SELECT title, kp_id, tmdb_id, COUNT(*) FROM history WHERE chat_id = {} GROUP By kp_id, tmdb_id, title;"
}


class BotDatabaseImpl(BotDatabase):

    def __init__(self, db_path: str):
        asyncio.get_event_loop().run_until_complete(self._init(db_path))

    async def save_search_entity(self, entity: SearchEntity) -> None:
        await self.connection.execute(_sql_requests['save_search_entity'],
                                      (entity.chat_id,
                                       entity.text,
                                       entity.title,
                                       entity.datetime,
                                       self._int_to_none(entity.kp_id),
                                       self._int_to_none(entity.tmdb_id)))
        await self.connection.commit()

    async def load_search_entities(self, chat_id: types.base.Integer) -> list[SearchEntity]:
        cursor = await self.connection.execute(_sql_requests['load_search_entities'].format(chat_id))
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            date = datetime.datetime.strptime(row[3].split('.')[0], "%Y-%m-%d %H:%M:%S")
            result.append(SearchEntity(
                row[0],
                row[1],
                row[2],
                date,
                self._get_int_optional(row[4]),
                self._get_int_optional(row[5])))
        return result

    async def load_stats_entities(self, chat_id: types.base.Integer) -> list[StatsEntity]:
        cursor = await self.connection.execute(_sql_requests['load_stats_entities'].format(chat_id))
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            result.append(StatsEntity(
                row[0],
                self._get_int_optional(row[1]),
                self._get_int_optional(row[2]),
                row[3]))
        return result

    async def _init(self, db_path: str):
        connection = aiosqlite.connect(db_path)
        self.connection = connection
        await self.connection.__aenter__()
        await self._init_tables()

    async def _init_tables(self):
        if not await self._check_table_exists('history'):
            query: str = _sql_requests['create_table_history']
            await self.connection.execute(query)

    async def _check_table_exists(self, table_name: str):
        cursor = await self.connection.execute(_sql_requests['table_exists'].format(table_name))
        result = await cursor.fetchone()
        return True if result else False

    @staticmethod
    def _int_to_none(x: Optional[int]) -> int:
        return -1 if not x else x

    @staticmethod
    def _get_int_optional(x: int) -> Optional[int]:
        return x if x != -1 else None
