from schemas.request import SupportedCountry
from schemas.response import UrlMetadata, UrlMetadataSourceType
import requests
import logging
import settings

logger = logging.getLogger(__name__)

# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/query-parameters
class BingSearchClient:
    # https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/market-codes#country-codes
    COUNTRIES_FILTER_CODES = {
        SupportedCountry.SLOVAKIA: "SK",
        SupportedCountry.USA: "US",
        SupportedCountry.GREAT_BRITAIN: "GB",
        SupportedCountry.GERMANY: "DE",
        SupportedCountry.CZECH_REPUBLIC: "CZ",
        SupportedCountry.AUSTRALIA: "AU",
        SupportedCountry.NEW_ZEALAND: "NZ",
    }
    
    def get_bing_search_results(self, query: str, countries: list[SupportedCountry]) -> list[UrlMetadata]:
        BASE_NEWS_URL = "https://api.bing.microsoft.com/v7.0/search?q={query}&safeSearch=Off".format(query=query)
        COUNTRY_CODE_FILTER = "&cc={country}"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.BING_API_KEY
        }
        raw_results: list[dict] = []
        if len(countries) == 0:
            response = requests.get(BASE_NEWS_URL, headers=headers)
            if response.status_code < 200 or response.status_code >= 300:
                logging.warn("Got non 200 status code from BING for URL: " + BASE_NEWS_URL)
                logging.warn("Status: " + str(response.status_code))
                logging.warn(response.text)
                return []
            data = response.json()
            if "webPages" in data and "value" in data["webPages"]:
                raw_results = data["webPages"]["value"]
        else:
            for cr in countries:
                cr_filter = COUNTRY_CODE_FILTER.format(country=BingSearchClient.COUNTRIES_FILTER_CODES[cr])
                url = BASE_NEWS_URL + cr_filter
                response = requests.get(url, headers=headers)
                if response.status_code < 200 or response.status_code >= 300:
                    logging.warn("Got non 200 status code from BING for URL: " + url)
                    logging.warn("Status: " + str(response.status_code))
                    logging.warn(response.text)
                    return raw_results
                data = response.json()
                if "webPages" in data and "value" in data["webPages"]:
                    raw_results.extend(data["webPages"]["value"])
        
        # now convert bing format to our format
        final_result: list[UrlMetadata] = []
        for res in raw_results:
            final_result.append(
                UrlMetadata(url=res["url"], title=res["name"], source=UrlMetadataSourceType.BING)
            )
        return final_result
    
    

def get_bing_search_results(target_name, countries: list[SupportedCountry]) -> list[UrlMetadata]:
    bing_query = '"' + target_name + '"'
    bn = BingSearchClient()
    try:
        results = bn.get_bing_search_results(bing_query, countries)
    except Exception:
        logger.exception("Bing news API call failed.")
        results = []
    return results
            
            