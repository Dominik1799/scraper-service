from pymongo import MongoClient
from pymongo.collection import Collection
import settings
from schemas.request import SupportedCountry, SupportedSource
from schemas.dto import UrlDataCache, UrlMetadataDto
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import time

def __create_mongo_client():
    mongo_uri = f"mongodb://{settings.MONGODB_USERNAME}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}:{settings.MONGODB_PORT}"
    return MongoClient(mongo_uri)

def __create_async_mongo_client():
    mongo_uri = f"mongodb://{settings.MONGODB_USERNAME}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}:{settings.MONGODB_PORT}"
    return AsyncIOMotorClient(mongo_uri, server_api=ServerApi('1'))

def ensure_initialized_db():
    # Connect to MongoDB instance
    client = __create_mongo_client()
    client.admin.command('ping')
    
    # Access the database
    db = client[settings.MONGODB_DATABASE]
    # create collections and ensure indexes
    if settings.MONGODB_URL_DATA_CACHE_COLLECTION not in db.list_collection_names():
        logging.info(f"Initializing collection {settings.MONGODB_TARGET_NAME_CACHE_COLLECTION}")
        db.create_collection(settings.MONGODB_URL_DATA_CACHE_COLLECTION)
    indexes = db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].index_information()
    if "url_index" not in indexes:
        logging.info("Initializing url_index")
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("url", 1)], name="url_index", unique=True)
    if "matched_targets_index" not in indexes:
        logging.info("Initializing matched_targets_index")
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("matched_targets", 1)], name="matched_targets_index")
    if "countries_index" not in indexes:
        logging.info("Initializing countries_index")
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("countries", 1)], name="countries_index")
    if "sources_index" not in indexes:
        logging.info("Initializing sources_index")
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("sources", 1)], name="sources_index")
    logging.info("MongoDB ready for use")
    client.close()


def __create_new_url_data(metadata: UrlMetadataDto, target_name: str, collection: Collection):
    ts = time.time()
    dc = UrlDataCache(url=metadata.url,
                      title=metadata.title,
                      sources=[metadata.source],
                      raw_html="",
                      parsed_content="",
                      is_probably_article=False,
                      matched_targets=[target_name],
                      countries=[metadata.country] if metadata.country is not None else [],
                      cannot_scrape=False,
                      last_found=ts,
                      last_updated=ts,
                      first_found=ts)
    dc_dict = dc.model_dump(mode="json")
    collection.insert_one(dc_dict)

# this is called if we parse URL content but dont have it cached with any target names, etc. 
# this can happen if somebody wants to parse the url but he found the URL on his own, without scraper service
def __create_new_url_data_after_parsing(url: str, raw_html: str, parsed_data: str, is_probably_article: bool ,collection: Collection):
    ts = time.time()
    dc = UrlDataCache(url=url,
                      title="",
                      sources=[],
                      raw_html=raw_html,
                      parsed_content=parsed_data,
                      is_probably_article=is_probably_article,
                      matched_targets=[],
                      countries=[],
                      cannot_scrape=False,
                      last_found=ts,
                      last_updated=ts,
                      first_found=ts)
    dc_dict = dc.model_dump(mode="json")
    collection.insert_one(dc_dict)

def __update_existing_url_data_after_parsing(existing_doc: dict, raw_html: str, parsed_data: str, is_probably_article: bool, collection: Collection):
    dc = UrlDataCache.model_validate(existing_doc)
    ts = time.time()
    dc.raw_html = raw_html
    dc.parsed_content = parsed_data
    dc.is_probably_article = is_probably_article
    dc.last_updated = ts
    dc_dict = dc.model_dump(mode="json")
    collection.replace_one({'url': dc.url}, dc_dict)
    

def __update_existing_url_match_data(existing_doc: dict, metadata: UrlMetadataDto, target_name: str, collection: Collection):
    dc = UrlDataCache.model_validate(existing_doc)
    ts = time.time()
    if target_name not in dc.matched_targets:
        dc.matched_targets.append(target_name)
    if metadata.source not in dc.sources:
        dc.sources.append(metadata.source)
    if metadata.country is not None and metadata.country not in dc.countries:
        dc.countries.append(metadata.country)
    dc.last_found = ts
    dc.last_updated = ts
    dc.title = metadata.title
    dc_dict = dc.model_dump(mode="json")
    collection.replace_one({'url': metadata.url}, dc_dict)


def upsert_found_urls(url_metadata: list[UrlMetadataDto], target_name: str):
    client = __create_mongo_client()
    collection = client[settings.MONGODB_DATABASE][settings.MONGODB_URL_DATA_CACHE_COLLECTION]
    for um in url_metadata:
        existing = collection.find_one({'url': um.url})
        if existing is None:
            __create_new_url_data(um, target_name, collection)
        else:
            __update_existing_url_match_data(existing, um, target_name, collection)


async def get_cached_data(url: str) -> UrlDataCache | None:
    async_client = __create_async_mongo_client()
    collection = async_client[settings.MONGODB_DATABASE][settings.MONGODB_URL_DATA_CACHE_COLLECTION]
    query = { "url": url }
    result = await collection.find_one(query)
    if result is None:
        return None
    return UrlDataCache.model_validate(result)


def upsert_url_data(url: str, raw_html: str, parsed_data: str, is_probably_article: bool = False, cannot_scrape: bool = False):
    client = __create_mongo_client()
    collection = client[settings.MONGODB_DATABASE][settings.MONGODB_URL_DATA_CACHE_COLLECTION]
    existing = collection.find_one({'url': url})
    if existing is None:
        __create_new_url_data_after_parsing(url, raw_html, parsed_data, is_probably_article, collection)
    else:
        __update_existing_url_data_after_parsing(existing, raw_html, parsed_data, is_probably_article, collection)

async def get_cached_urls(target_name: str, countries: list[SupportedCountry], sources: list[SupportedSource]) -> list[UrlMetadataDto]:
    async_client = __create_async_mongo_client()
    collection = async_client[settings.MONGODB_DATABASE][settings.MONGODB_URL_DATA_CACHE_COLLECTION]
    # for some reason fastapi passes these two varibles as sets and not lists into this function. Thats why we need convert this
    # mongo does not work with sets in query
    sources = list(sources)
    countries = list(countries)
    query = {   
             "matched_targets": target_name,
             "sources": {"$in": sources}
            }
    if len(countries) > 0:
        query["countries"] = {"$in": countries}
    cursor = collection.find(query)
    query_result = await cursor.to_list(length=30) # max retrieve 30 articles from cache
    query_result = [UrlDataCache.model_validate(r) for r in query_result]
    result = [UrlMetadataDto(url=dc.url, 
                             title=dc.title, 
                             source=sources[0], 
                             country=None if len(countries) == 0 else countries[0]) for dc in query_result]
    return result
    