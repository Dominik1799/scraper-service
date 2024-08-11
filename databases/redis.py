import logging
import redis
from settings import REDIS_HOST, REDIS_PORT, REDIS_DATABASE

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)

try:
    redis_client.ping()
except Exception as e:
    logging.error("Redis connection failed. Exitting.", e)
    exit(1)


def store_clean_article(url_identifier: str, article: str):
    redis_client.set(url_identifier, article)
    

def get_cached_clean_article(url_identifier: str) -> str:
    article = redis_client.get(url_identifier)
    if article is None:
        return None
    article = article.decode("utf-8")
    return article
