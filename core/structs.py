from dataclasses import dataclass

import datetime as datetime
from typing import Optional

from aiogram import types


@dataclass
class SearchEntity:
    chat_id: types.base.Integer
    text: str
    title: str
    datetime: datetime.datetime
    kp_id: Optional[int]
    tmdb_id: Optional[int]


@dataclass
class StatsEntity:
    title: str
    kp_id: Optional[int]
    tmdb_id: Optional[int]
    count: int


@dataclass
class Movie:
    title: Optional[str] = None
    description: Optional[str] = None
    link_kp: Optional[str] = None
    poster: Optional[str] = None
    original_title: Optional[str] = None
    id_tmdb: Optional[str] = None
    id_imdb: Optional[str] = None
    id_kp: Optional[int] = None
    rating_tmdb: Optional[float] = None
    rating_imdb: Optional[float] = None
    rating_kp: Optional[float] = None
    links_to_watch: Optional[list[str]] = None


@dataclass
class Banner:
    text: str
    picture: Optional[str]
