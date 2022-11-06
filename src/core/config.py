import os
from logging import config as logging_config

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILM_CACHE_EXPIRE_IN_SECONDS = 1 * 5
GENRE_CACHE_EXPIRE_IN_SECONDS = 1 * 5
PERSON_CACHE_EXPIRE_IN_SECONDS = 1 * 5
CACHE_EXPIRE_IN_SECONDS = 1 * 5

ES_INDEXES = {'films': ('movies', 'Film'),
              'persons': ('persons', 'Person'),
              'genre': ('genres', 'Genre')}

ES_INDEX_GENRES = 'genres'
ES_INDEX_PERSONS = 'persons'
ES_INDEX_MOVIES = 'movies'

ES_SIZE = 1000
