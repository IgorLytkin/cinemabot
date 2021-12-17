from abc import ABC, abstractmethod
from typing import Optional, Any

import aiohttp

from .structs import Movie
from .helpers import first_non_none


class SearchEngine(ABC):

    @abstractmethod
    async def search_movie(self, query: str) -> Optional[Movie]:
        pass


class TmdbSearchEngine(SearchEngine):
    search_movie_endpoint: str = 'https://api.themoviedb.org/3/search/movie'
    images_endpoint: str = "https://image.tmdb.org/t/p/w500"
    get_movie_endpoint: str = "https://api.themoviedb.org/3/movie"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_movie(self, query: str) -> Optional[Movie]:
        search_params = {
            'api_key': self.api_key,
            'query': query,
            'page': 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_movie_endpoint, params=search_params) as response:
                json_response = await response.json()

            results: Optional[dict[str, Any]] = json_response.get('results')
            if not results:
                return None
            top: dict[str, Any] = json_response['results'][0]
            movie_params = {'api_key': self.api_key}
            async with session.get(self.get_movie_endpoint + f'/{top.get("id")}', params=movie_params) as response:
                json_response = await response.json()
                return self._parse_json_movie(json_response)

    def _parse_json_movie(self, json: dict[str, Any]) -> Optional[Movie]:
        poster: Optional[str] = None
        if json.get('poster_path'):
            poster = self.images_endpoint + json.get('poster_path')
        return Movie(
            title=json.get('title'),
            description=json.get('overview'),
            poster=poster,
            id_tmdb=json.get('id'),
            id_imdb=json.get('imdb_id'),
            original_title=json.get('original_title')
        )


class KpUnofficialSearchEngine(SearchEngine):
    search_movie_endpoint: str = 'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword'
    get_movie_endpoint: str = 'https://kinopoiskapiunofficial.tech/api/v2.2/films'

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

    async def search_movie(self, query: str) -> Optional[Movie]:
        params = {
            'api_key': self.api_key,
            'page': 1,
            'keyword': query
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_movie_endpoint, params=params, headers=self.headers) as response:
                json_search_response = await response.json()
                kp_id: Optional[int] = self._parse_top_movie_id(json_search_response)
                if not kp_id:
                    return None
            async with session.get(self.get_movie_endpoint + f'/{kp_id}', headers=self.headers) as response:
                json_response = await response.json()
                return self._parse_movie_json_obj(json_response)

    @staticmethod
    def _parse_top_movie_id(json: dict[str, Any]) -> Optional[int]:
        if not json.get('films'):
            return None
        top = json['films'][0]
        return top.get('filmId')

    @staticmethod
    def _parse_movie_json_obj(json: dict[str, Any]) -> Optional[Movie]:
        return Movie(
            title=first_non_none([json.get('nameRu'), json.get('nameEn')]),
            original_title=json.get('nameOriginal'),
            description=json.get('description'),
            link_kp=json.get('webUrl'),
            poster=json.get('posterUrl'),
            id_imdb=json.get('imdbId'),
            id_kp=json.get('kinopoiskId'),
            rating_kp=json.get('ratingKinopoisk'),
            rating_imdb=json.get('ratingImdb')
        )
