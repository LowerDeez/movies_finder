from typing import Dict, List
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache

from constance import config
from tmdbv3api import TMDb, Movie, Discover, Genre

from .utils import modify_result

__all__ = (
    'TMDBWrapper',
    'get_cached_movies_genres'
)


def return_movies(movies: List['Movie']):
    movies = [
        movie
        for movie in movies
        if (
                movie.vote_average > 5
                and movie.vote_count > 50
                and movie.backdrop_path
                and movie.overview
        )
    ]
    movies = sorted(movies, key=lambda x: x.vote_average)
    print('Movies count:', len(movies))
    return movies


class TMDBWrapper:
    def __init__(self, language: str):
        self.tmdb = TMDb()
        self.tmdb.api_key = config.MOVIE_DB_API_KEY  # '26e13c6a960c2e640f5e1867b9c52a46'
        self.tmdb.language = language or settings.LANGUAGE_CODE
        self.movie = Movie()
        self.discover = Discover()
        self.genre = Genre()

    def set_language(self, language: str):
        self.tmdb.language = language

    @modify_result(return_movies)
    def popular(self, page: int = 1):
        return self.movie.popular(page)

    @modify_result(return_movies)
    def top_rated(self, page: int = 1):
        return self.movie.top_rated(page)

    @modify_result(return_movies)
    def upcoming(self, page: int = 1, region: str = 'UA'):
        return self.movie._get_obj(
            self.movie._call(
                self.movie._urls["upcoming"],
                urlencode({
                    # "region": region,
                    "page": str(page)
                })
            )
        )

    @modify_result(return_movies)
    def now_playing(self, page: int = 1):
        return self.movie.now_playing(page)

    @modify_result(return_movies)
    def search_movies(self, query: str, page: int = 1, **kwargs):
        return self.movie.search(term=query, page=page)

    @modify_result(return_movies)
    def discover_movies(self, params: Dict, **kwargs):
        return self.discover.discover_movies(params=params)

    def get_movies_genres(self):
        return self.genre.movie_list()


def get_cached_movies_genres(language: str) -> Dict:
    cache_key = f'tmdb:genres:{language}'
    genres = cache.get(cache_key)

    if genres is None:
        genres = TMDBWrapper(language).get_movies_genres()
        genres = {genre.id: str(genre.name).title() for genre in genres}
        cache.set(cache_key, genres)

    return genres
