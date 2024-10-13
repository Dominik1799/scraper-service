import settings
import copy
import random
import httpx
import logging
from schemas.dto import UrlMetadataDto
from schemas.request import SupportedCountry, SupportedSource


logger = logging.getLogger(__name__)




class GoogleSearch:
    # https://developers.google.com/custom-search/docs/json_api_reference#countryCollections
    COUNTRIES_FILTER_CODES = {
        SupportedCountry.SLOVAKIA: "countrySK",
        SupportedCountry.USA: "countryUS",
        SupportedCountry.GREAT_BRITAIN: "countryUK",
        SupportedCountry.GERMANY: "countryDE",
        SupportedCountry.CZECHIA: "countryCZ",
        SupportedCountry.AUSTRALIA: "countryAU",
        SupportedCountry.NEW_ZEALAND: "countryNZ",
        SupportedCountry.ITALY: "countryIT",
        SupportedCountry.AUSTRIA: "countryAT",
        SupportedCountry.BELGIUM: "countryBE",
        SupportedCountry.BULGARIA: "countryBG",
        SupportedCountry.CROATIA: "countryHR",
        SupportedCountry.CYPRUS: "countryCY",
        SupportedCountry.DENMARK: "countryDK",
        SupportedCountry.ESTONIA: "countryEE",
        SupportedCountry.FINLAND: "countryFI",
        SupportedCountry.FRANCE: "countryFR",
        SupportedCountry.GREECE: "countryGR",
        SupportedCountry.HUNGARY: "countryHU",
        SupportedCountry.IRELAND: "countryIE",
        SupportedCountry.LATVIA: "countryLV",
        SupportedCountry.LITHUANIA: "countryLT",
        SupportedCountry.LUXEMBOURG: "countryLU",
        SupportedCountry.MALTA: "countryMT",
        SupportedCountry.NETHERLANDS: "countryNL",
        SupportedCountry.POLAND: "countryPL",
        SupportedCountry.PORTUGAL: "countryPL",
        SupportedCountry.ROMANIA: "countryRO",
        SupportedCountry.SLOVENIA: "countrySI",
        SupportedCountry.SPAIN: "countryES",
        SupportedCountry.SWEDEN: "countrySE",
    }
    
    def __construct_country_filter(self, countries: list[SupportedCountry]):
        cr_codes = [GoogleSearch.COUNTRIES_FILTER_CODES[cr] for cr in countries]
        cr_filter = "|".join(cr_codes)
        return cr_filter

    # start pages from 1
    async def get_google_results(self, query: str, countries: list[SupportedCountry] = [], start: int = 1) -> list[UrlMetadataDto]:
        # https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
        BASE_SEARCH_URL = "https://customsearch.googleapis.com/customsearch/v1?key={api_key}&cx={engine_id}&start={start}&q={query}"
        COUNTRY_CODE_FILTER = "&cr={country}"
        if len(countries) != 0:
            COUNTRY_CODE_FILTER = COUNTRY_CODE_FILTER.format(country=self.__construct_country_filter(countries))
        else:
            COUNTRY_CODE_FILTER = ""
        url = BASE_SEARCH_URL + COUNTRY_CODE_FILTER
        async with httpx.AsyncClient(timeout=10) as client:
            for creds_string in self.google_credentials:
                engine_id, api_key = creds_string.split(":")
                url = url.format(api_key=api_key, engine_id=engine_id, query=query, start=start)
                logger.debug("Url used for google: " + url)
                response = await client.get(url)
                if response.status_code == 429:
                    logger.warning("Got 429 for engineId " + engine_id + ". Rotating...")
                    continue
                if response.status_code >= 400:
                    logger.error("Got error request from google: " + str(response.json()))
                    logger.error("Status: " + str(response.status_code))
                    return []
                response_json = response.json()
                data = response_json["items"] if "items" in response_json else []
                formatted_data = []
                for d in data:
                    temp = UrlMetadataDto(url=d["link"], 
                                          title=d["title"], 
                                          source=SupportedSource.GOOGLE,
                                          country= countries[0] if len(countries) > 0 else None)
                    formatted_data.append(temp)
                logger.debug("Google search for " + query + " was successful")
                return formatted_data

                
        logger.error("All google requests for " + query + " failed.")
        return []   
    
    def __init__(self) -> None:
        self.google_credentials = copy.deepcopy(settings.GOOGLE_SEARCH_API_CREDENTIALS)
        random.shuffle(self.google_credentials)
        

async def get_google_search_links(target_name, countries: list[SupportedCountry] = [], keywords: list[str] = []) -> list[UrlMetadataDto]:
    google_query = '"' + target_name + '"'
    if len(keywords) != 0:
        google_query = google_query + " AND (" + " OR ".join(keywords) + ")"
    gs = GoogleSearch()
    try:
        results = await gs.get_google_results(google_query, countries)
    except Exception:
        logger.exception("Google search API call failed.")
        results = []
    
    return results