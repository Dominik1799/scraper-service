import settings
import copy
import random
import requests
import logging
from schemas.response import UrlMetadata, UrlMetadataSourceType
from schemas.request import SupportedCountry


logger = logging.getLogger(__name__)




class GoogleSearch:
    # https://developers.google.com/custom-search/docs/json_api_reference#countryCollections
    COUNTRIES_FILTER_CODES = {
        SupportedCountry.SLOVAKIA: "countrySK",
        SupportedCountry.USA: "countryUS",
        SupportedCountry.GREAT_BRITAIN: "countryUK",
        SupportedCountry.GERMANY: "countryDE",
        SupportedCountry.CZECH_REPUBLIC: "countryCZ",
        SupportedCountry.AUSTRALIA: "countryAU",
        SupportedCountry.NEW_ZEALAND: "countryNZ",
    }
    
    def __construct_country_filter(self, countries: list[SupportedCountry]):
        cr_codes = [GoogleSearch.COUNTRIES_FILTER_CODES[cr] for cr in countries]
        cr_filter = "|".join(cr_codes)
        return cr_filter

    # start pages from 1
    def get_google_results(self, query: str, countries: list[SupportedCountry] = [], start: int = 1) -> list[UrlMetadata]:
        
        # https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
        BASE_SEARCH_URL = "https://customsearch.googleapis.com/customsearch/v1?key={api_key}&cx={engine_id}&start={start}&q={query}"
        COUNTRY_CODE_FILTER = "&cr={country}"
        if len(countries) != 0:
            COUNTRY_CODE_FILTER = COUNTRY_CODE_FILTER.format(country=self.__construct_country_filter(countries))
        else:
            COUNTRY_CODE_FILTER = ""
        url = BASE_SEARCH_URL + COUNTRY_CODE_FILTER
        for creds_string in self.google_credentials:
            engine_id, api_key = creds_string.split(":")
            url = url.format(api_key=api_key, engine_id=engine_id, query=query, start=start)
            logger.info("Url used for google: " + url)
            response = requests.get(url)
            if response.status_code == 429:
                logger.warning("Got 429 for engineId " + engine_id + ". Rotating...")
                continue
            if response.status_code >= 400:
                logger.error("Got error request from google: " + str(response.json()))
                logger.error("Status: " + str(response.status_code))
                return None
            response_json = response.json()
            data = response_json["items"] if "items" in response_json else []
            formatted_data = []
            for d in data:
                temp = UrlMetadata(url=d["link"], title=d["title"], source=UrlMetadataSourceType.GOOGLE)
                formatted_data.append(temp)
            logger.info("Google search for " + query + " was successful")
            return formatted_data

                
        logger.error("All google requests for " + query + " failed.")
        return None   
    
    def __init__(self) -> None:
        self.google_credentials = copy.deepcopy(settings.GOOGLE_SEARCH_API_CREDENTIALS)
        random.shuffle(self.google_credentials)
        

def __create_topic_search_string(topic, language):
    if topic == "basic_check":
        return ""
    # if language is specified and we support it
    if language is not None and language in settings.TOPIC_SEARCH_KEYWORDS[topic]:
        return " " + " OR ".join(settings.TOPIC_SEARCH_KEYWORDS[topic][language])
    # else combine all keywords from all supported languages in specific topic
    all_keywords = []
    for lang in settings.TOPIC_SEARCH_KEYWORDS[topic]:
        all_keywords.append(settings.TOPIC_SEARCH_KEYWORDS[topic][lang])
    return " " + " OR ".join(all_keywords)

def get_google_search_links(target_name, countries: list[SupportedCountry] = []) -> list[UrlMetadata]:
    # for this to work again we need requested language. Meaning we cannot create topic centered searches, only basic_checks
    # google_query = '"' + target_name + '"' + __create_topic_search_string(topic, language)
    google_query = '"' + target_name + '"'
    gs = GoogleSearch()
    results = gs.get_google_results(google_query, countries)
    
    return results