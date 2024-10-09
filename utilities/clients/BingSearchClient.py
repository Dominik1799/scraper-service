from schemas.request import SupportedCountry, SupportedSource
from schemas.dto import UrlMetadataDto
import httpx
import logging
import settings

logger = logging.getLogger(__name__)

# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/query-parameters
class BingSearchClient:
    # https://learn.microsoft.com/en-us/bing/search-apis/bing-news-search/reference/market-codes#country-codes
    # if not on the link above, search for country codes here: 
    # https://www.bing.com/account/general?ru=https%3a%2f%2fwww.bing.com%2f%3fsetlang%3den%26cc%3dsk%26cc%3dSK&FORM=O2HV65&id=region_section#region-section
    COUNTRIES_FILTER_CODES = {
        SupportedCountry.SLOVAKIA: "SK",
        SupportedCountry.USA: "US",
        SupportedCountry.GREAT_BRITAIN: "GB",
        SupportedCountry.GERMANY: "DE",
        SupportedCountry.CZECHIA: "CZ",
        SupportedCountry.AUSTRALIA: "AU",
        SupportedCountry.NEW_ZEALAND: "NZ",
        SupportedCountry.ITALY: "IT",
        SupportedCountry.AUSTRIA: "AT",
        SupportedCountry.BELGIUM: "BE",
        SupportedCountry.BULGARIA: "BG",
        SupportedCountry.CROATIA: "HR",
        SupportedCountry.CYPRUS: "CY",
        SupportedCountry.DENMARK: "DK",
        SupportedCountry.ESTONIA: "EE",
        SupportedCountry.FINLAND: "FI",
        SupportedCountry.FRANCE: "FR",
        SupportedCountry.GREECE: "GR",
        SupportedCountry.HUNGARY: "HU",
        SupportedCountry.IRELAND: "IE",
        SupportedCountry.LATVIA: "LV",
        SupportedCountry.LITHUANIA: "LT",
        SupportedCountry.LUXEMBOURG: "LU",
        SupportedCountry.MALTA: "MT",
        SupportedCountry.NETHERLANDS: "NL",
        SupportedCountry.POLAND: "PL",
        SupportedCountry.PORTUGAL: "PT",
        SupportedCountry.ROMANIA: "RO",
        SupportedCountry.SLOVENIA: "SI",
        SupportedCountry.SPAIN: "ES",
        SupportedCountry.SWEDEN: "SE",
    }
    
    async def get_bing_search_results(self, query: str, countries: list[SupportedCountry]) -> list[UrlMetadataDto]:
        BASE_NEWS_URL = "https://api.bing.microsoft.com/v7.0/search?q={query}&safeSearch=Off".format(query=query)
        COUNTRY_CODE_FILTER = "&cc={country}"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.BING_API_KEY
        }
        # each dict contains results key (bing search results) and country key (country from which we got these results)
        raw_results: list[dict] = []
        if len(countries) == 0:
            async with httpx.AsyncClient() as client:
                response = await client.get(BASE_NEWS_URL, headers=headers)
                if response.status_code < 200 or response.status_code >= 300:
                    logging.warning("Got non 200 status code from BING for URL: " + BASE_NEWS_URL)
                    logging.warning("Status: " + str(response.status_code))
                    logging.warning(response.text)
                    return []
                data = response.json()
                if "webPages" in data and "value" in data["webPages"]:
                    raw_results.append({"results": data["webPages"]["value"], "country": None})
        else:
            async with httpx.AsyncClient() as client:
                for cr in countries:
                    cr_filter = COUNTRY_CODE_FILTER.format(country=BingSearchClient.COUNTRIES_FILTER_CODES[cr])
                    url = BASE_NEWS_URL + cr_filter
                    response = await client.get(url, headers=headers)
                    if response.status_code < 200 or response.status_code >= 300:
                        logging.warning("Got non 200 status code from BING for URL: " + url)
                        logging.warning("Status: " + str(response.status_code))
                        logging.warning(response.text)
                        return raw_results
                    data = response.json()
                    if "webPages" in data and "value" in data["webPages"]:
                        raw_results.append({"results": data["webPages"]["value"], "country": cr})
        
        # now convert bing format to our format
        final_result: list[UrlMetadataDto] = []
        for res in raw_results:
            for data in res["results"]:
                final_result.append(
                    UrlMetadataDto(url=data["url"], title=data["name"], source=SupportedSource.BING, country=res["country"])
                )
        return final_result
    
    

async def get_bing_search_results(target_name, countries: list[SupportedCountry], keywords: list[str] = []) -> list[UrlMetadataDto]:
    bing_query = '"' + target_name + '"'
    if len(keywords) != 0:
        bing_query = bing_query + " AND (" + " OR ".join(keywords) + ")"
    bn = BingSearchClient()
    try:
        results = await bn.get_bing_search_results(bing_query, countries)
    except Exception:
        logger.exception("Bing news API call failed.")
        results = []
    return results
            
            