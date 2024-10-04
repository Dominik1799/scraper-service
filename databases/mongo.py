from pymongo import MongoClient
from pymongo.collection import Collection
import settings
from schemas.request import SupportedCountry
from schemas.response import UrlMetadata
from schemas.dto import UrlDataCache
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
    if settings.MONGODB_URL_DATA_CACHE_COLLECTION not in db.list_collection_names():
        logging.info(f"Initializing collection {settings.MONGODB_TARGET_NAME_CACHE_COLLECTION}")
        db.create_collection(settings.MONGODB_URL_DATA_CACHE_COLLECTION)
    indexes = db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].list_indexes()
    if "url_index" not in indexes:
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("url", 1)], name="url_index")
    if "matched_targets_index" not in indexes:
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("matched_targets", 1)], name="matched_targets_index")
    if "countries_index" not in indexes:
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("countries", 1)], name="countries_index")
    if "sources_index" not in indexes:
        db[settings.MONGODB_URL_DATA_CACHE_COLLECTION].create_index([("sources", 1)], name="sources_index")
    logging.info("MongoDB ready for use")
    client.close()


def __create_new_url_data(metadata: UrlMetadata, target_name: str, countries: list[SupportedCountry], collection: Collection):
    dc = UrlDataCache(url=metadata.url,
                      title=metadata.title,
                      sources=[metadata.source],
                      raw_html="",
                      parsed_content="",
                      is_probably_article=False,
                      matched_targets=[target_name],
                      countries=countries,
                      cannot_scrape=False)
    dc_dict = dc.model_dump(mode="json")
    collection.insert_one(dc_dict)

def __update_existing_url_match_data(existing_doc: dict, metadata: UrlMetadata, target_name: str, countries: list[SupportedCountry], collection: Collection):
    dc = UrlDataCache.model_validate(existing_doc)
    if target_name not in dc.matched_targets:
        dc.matched_targets.append(target_name)
    if metadata.source not in dc.sources:
        dc.sources.append(metadata.source)
    countries.extend(dc.countries)
    deduplicated_countries = list(set(countries))
    dc.countries = deduplicated_countries
    dc_dict = dc.model_dump(mode="json")
    collection.replace_one({'url': metadata.url}, dc_dict)


def upsert_found_urls(url_metadata: list[UrlMetadata], target_name: str, countries: list[SupportedCountry]):
    client = __create_mongo_client()
    collection = client[settings.MONGODB_DATABASE][settings.MONGODB_URL_DATA_CACHE_COLLECTION]
    for um in url_metadata:
        existing = collection.find_one({'url': um.url})
        if existing is None:
            __create_new_url_data(um, target_name, countries, collection)
        else:
            __update_existing_url_match_data(existing, um, target_name, countries, collection)