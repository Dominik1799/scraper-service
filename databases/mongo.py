from pymongo import MongoClient
import settings
from schemas.request import SupportedCountry
from schemas.response import UrlMetadata
import logging


def __create_mongo_client():
    mongo_uri = f"mongodb://{settings.MONGODB_USERNAME}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}:{settings.MONGODB_PORT}"
    return MongoClient(mongo_uri)


def ensure_initialized_db():
    # Connect to MongoDB instance
    client = __create_mongo_client()
    client.admin.command('ping')
    
    # Access the database
    db = client[settings.MONGODB_DATABASE]
    # create collections and ensure indexes
    if settings.MONGODB_TARGET_NAME_CACHE_COLLECTION not in db.list_collection_names():
        logging.info(f"Initializing collection {settings.MONGODB_TARGET_NAME_CACHE_COLLECTION}")
        db.create_collection(settings.MONGODB_TARGET_NAME_CACHE_COLLECTION)
        db[settings.MONGODB_TARGET_NAME_CACHE_COLLECTION].create_index([("key", 1)])
    if settings.MONGODB_URL_DATA_CACHE_COLLECTION not in db.list_collection_names():
        logging.info(f"Initializing collection {settings.MONGODB_TARGET_NAME_CACHE_COLLECTION}")
        db.create_collection(settings.MONGODB_URL_DATA_CACHE_COLLECTION)
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("url", 1)])
    logging.info("MongoDB ready for use")
    client.close()

def __create_target_cache_key(target_name: str, countries: list[SupportedCountry], keywords: list[str]) -> str:
    countries_str = [c.name for c in countries]
    countries_str.sort()
    keywords.sort()
    
    countries_joined = "_".join(countries_str)
    keywords_joined = "_".join(keywords)
    return f"{target_name}${countries_joined}${keywords_joined}"

def upsert_target_search_cache(target_name: str, countries: list[SupportedCountry], keywords: list[str], matched_urls: list[UrlMetadata]):
    key = __create_target_cache_key(target_name, countries, keywords)
    