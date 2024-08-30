import logging
import redis
from settings import REDIS_HOST, REDIS_PORT, REDIS_DATABASE
from schemas.response import ContentScraping
import json

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)


REDIS_RAW_HTML_NAMESPACE = "RAW_HTML"

REDIS_PARSED_CONTENT_NAMESPACE = "PARSED_CONTENT"

try:
    redis_client.ping()
except Exception as e:
    logging.error("Redis connection failed. Exitting.", e)
    exit(1)


def __build_key(namespace: str, id: str):
    return namespace + ":" + id


def get_cached_scraped_content(url_identifier: str) -> ContentScraping | None:
    key = __build_key(REDIS_PARSED_CONTENT_NAMESPACE, url_identifier)
    data = redis_client.get(key)
    if data is None:
        return None
    data = data.decode("utf-8")
    data = json.loads(data)
    return ContentScraping(parsed_data=data["parsed_data"], is_probably_article=data["is_probably_article"])


def store_cached_scraped_content(url_identifier: str, data: ContentScraping):
    key = __build_key(REDIS_PARSED_CONTENT_NAMESPACE, url_identifier)
    dict_model = data.model_dump(mode="json")
    str_model = json.dumps(dict_model, ensure_ascii=False)
    redis_client.set(key, str_model)


def store_raw_content(url_identifier: str, html: str):
    key = __build_key(REDIS_RAW_HTML_NAMESPACE, url_identifier)
    redis_client.set(key, html)


def get_cached_raw_content(url_identifier: str) -> str | None:
    key = __build_key(REDIS_RAW_HTML_NAMESPACE, url_identifier)
    html = redis_client.get(key)
    if html is None:
        return None
    return html.decode("utf-8")