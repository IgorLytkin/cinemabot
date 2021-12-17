from typing import Optional, Any

from .structs import Movie, Banner
from dataclasses import fields


def merge_movies(movies: list[Movie]) -> Optional[Movie]:
    result: Optional[Movie] = None
    for movie in movies:
        if not movie:
            continue
        if not result:
            result = movie
        else:
            for field in fields(Movie):
                if not getattr(result, field.name):
                    new_value = getattr(movie, field.name)
                    setattr(result, field.name, new_value)
    return result


def movie_to_banner(movie: Movie) -> Banner:
    text: str = ''
    if movie.title:
        if movie.original_title and movie.original_title != movie.title:
            text += f'{movie.title} ({movie.original_title})\n\n'
        else:
            text += f'{movie.title}\n\n'
    rating_text: str = ''
    if movie.rating_imdb:
        rating_text += f'IMDB: {movie.rating_imdb}/10 '
    if movie.rating_kp:
        rating_text += f'Кинопоиск: {movie.rating_kp}/10 '
    if movie.rating_tmdb:
        rating_text += f'TMDB: {movie.rating_tmdb}/10'
    if rating_text != '':
        rating_text += '\n\n'
    text += rating_text
    if movie.description:
        text += f'{movie.description}\n\n'
    if movie.link_kp:
        text += f'[Страница на Кинопоиск]({movie.link_kp})\n\n'
    if movie.links_to_watch:
        links: str = ""
        for i in range(len(movie.links_to_watch)):
            links += f'[Кинотеатр{i + 1}]({movie.links_to_watch[i]})\n'
        text += f'Смотреть онлайн:\n{links}'
    return Banner(text, movie.poster)


def first_non_none(lst: list[Any]) -> Optional[Any]:
    for item in lst:
        if item:
            return item
    return None
