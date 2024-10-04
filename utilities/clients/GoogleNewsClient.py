from asyncio.log import logger
import logging
import feedparser
from datetime import datetime, timedelta
from utilities.clients.decodeGoogleNewsUrl import decode_google_news_url
from utilities.request_util import async_proxy_request
from schemas.response import UrlMetadata
from schemas.request import SupportedCountry, SupportedSource
import settings



class GnewsParser:
    __BASE_URL = "https://news.google.com/rss/search?q=<QUERY><DATERANGE><LOCALE>"
    __DATE_RANGE = "+after:<AFTER>+before:<BEFORE>"
    __LOCALE = {
        SupportedCountry.SLOVAKIA: "&hl=sk&gl=SK&ceid=SK:sk",
        SupportedCountry.USA: "&hl=en-US&gl=US&ceid=US:en",
        SupportedCountry.GREAT_BRITAIN: "&hl=en-GB&gl=GB&ceid=GB:en",
        SupportedCountry.GERMANY: "&hl=de&gl=DE&ceid=DE:de",
        SupportedCountry.CZECHIA: "&hl=cs&gl=CZ&ceid=CZ:cs",
        SupportedCountry.AUSTRALIA: "&hl=en-AU&gl=AU&ceid=AU%3Aen",
        SupportedCountry.NEW_ZEALAND: "&hl=en-NZ&gl=NZ&ceid=NZ%3Aen",
        SupportedCountry.ITALY: "&hl=it&gl=IT&ceid=IT%3Ait",
        SupportedCountry.AUSTRIA: "&hl=de&gl=AT&ceid=AT%3Ade",
        SupportedCountry.BELGIUM: "&hl=nl&gl=BE&ceid=BE%3Anl",
        SupportedCountry.BULGARIA: "&hl=bg&gl=BG&ceid=BG%3Abg",
        SupportedCountry.CROATIA: "&hl=bg&gl=BG&ceid=BG%3Abg", # I cannot find locale for croatia
        SupportedCountry.CYPRUS: "&hl=bg&gl=BG&ceid=BG%3Abg", # I cannot find locale for cyprus
        SupportedCountry.DENMARK: "&hl=sv&gl=SE&ceid=SE%3Asv", # I cannot find locale for denmark
        SupportedCountry.ESTONIA: "&hl=et-EE&gl=EE&ceid=EE%3Aet",
        SupportedCountry.FINLAND: "&hl=fi-FI&gl=FI&ceid=FI%3Afi",
        SupportedCountry.FRANCE: "&hl=fr&gl=FR&ceid=FR%3Afr",
        SupportedCountry.GREECE: "&hl=el&gl=GR&ceid=GR%3Ael",
        SupportedCountry.HUNGARY: "&hl=hu&gl=HU&ceid=HU%3Ahu",
        SupportedCountry.IRELAND: "&hl=en-IE&gl=IE&ceid=IE%3Aen",
        SupportedCountry.LATVIA: "&hl=lv&gl=LV&ceid=LV%3Alv",
        SupportedCountry.LITHUANIA: "&hl=lt&gl=LT&ceid=LT%3Alt",
        SupportedCountry.LUXEMBOURG: "&hl=nl&gl=BE&ceid=BE%3Anl", # I cannot find locale for luxembourg
        SupportedCountry.MALTA: "&hl=el&gl=GR&ceid=GR%3Ael", # I cannot find locale for malta
        SupportedCountry.NETHERLANDS: "&hl=nl&gl=NL&ceid=NL%3Anl",
        SupportedCountry.POLAND: "&hl=pl&gl=PL&ceid=PL%3Apl",
        SupportedCountry.PORTUGAL: "&hl=pt-PT&gl=PT&ceid=PT%3Apt-150",
        SupportedCountry.ROMANIA: "&hl=ro&gl=RO&ceid=RO%3Aro",
        SupportedCountry.SLOVENIA: "&hl=sl&gl=SI&ceid=SI%3Asl",
        SupportedCountry.SPAIN: "&hl=es&gl=ES&ceid=ES%3Aes",
        SupportedCountry.SWEDEN: "&hl=sv&gl=SE&ceid=SE%3Asv",
    }

    def __init__(self, query, from_date="", to_date="", country: SupportedCountry = SupportedCountry.USA):
        url = GnewsParser.__BASE_URL
        url = url.replace("<QUERY>", query.replace(" ", "%20"))
        url = url.replace("<DATERANGE>", self.__get_date_range(from_date, to_date))
        url = url.replace("<LOCALE>", self.__get_locale(country))
        self.__url = url
        
    def get_url(self):
        return self.__url
    
    def __get_locale(self, country: SupportedCountry):
        if country != "" and country in GnewsParser.__LOCALE:
            return GnewsParser.__LOCALE[country]
        else:
            return ""
    
    def __get_date_range(self, from_date, to_date):
        # TODO: validate that the date is valid
        date_range = ""
        if from_date != "":
            date_range += "+after:<AFTER>".replace("<AFTER>", from_date)
        if to_date != "":
            date_range += "+before:<BEFORE>".replace("<BEFORE>", to_date)
        return date_range

    async def get_raw_results(self):
        gnews_response = await async_proxy_request(self.__url, "GET", headers={'Cache-control': 'max-age=0'}, try_normal_request_first=True, timeout=15)
        logging.info("Url used for google news: " + self.__url)
        if gnews_response is None:
            return None
        res = feedparser.parse(gnews_response.text)
        return res["entries"]
    
    
    async def get_articles(self, n=50) -> list:
        raw_results = await self.get_raw_results()
        raw_results = raw_results[0:n]
        results = []
        # get unix timestamp on each article
        # get correct urls
        for ent in raw_results:
            link = decode_google_news_url(ent["link"])
            if link and link["status"]:
                results.append({
                    "title": ent["title"],
                    "link": link["decoded_url"],
                    "published": self.convert_date_to_unix_timestamp(ent["published"]),
                    "source": ent["source"]["href"]
                })
    
        return results
        
    
    def convert_date_to_unix_timestamp(self, date_string):
        # Define the input format of the date string
        input_format = "%a, %d %b %Y %H:%M:%S %Z"
        # Parse the date string into a datetime object
        try:
            dt_object = datetime.strptime(date_string, input_format)
        except ValueError:
            return None  # Invalid date format
    
        # Convert the datetime object to a Unix timestamp
        unix_timestamp = dt_object.timestamp()
    
        return unix_timestamp



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

async def get_google_news_links(target_name, countries: list[SupportedCountry] = []) -> list[UrlMetadata]:
    # for this to work again we need requested language. Meaning we cannot create topic centered searches, only basic_checks
    # gnews_query = '"' + target_name + '"' + __create_topic_search_string(topic, language)
    gnews_query = '"' + target_name + '"'
    all_articles = []
    
    try:
        if len(countries) == 0:
            gp = GnewsParser(gnews_query)
            articles = await gp.get_articles(n=10)
            all_articles.extend(articles)
        else:
            for country in countries:
                gp = GnewsParser(gnews_query, country=country)
                articles = await gp.get_articles(n=10)
                all_articles.extend(articles)
    except Exception:
        logger.exception("Google news scraping failed.")
    result = []
    for art in all_articles:
        temp = UrlMetadata(url=art["link"], title=art["title"], source=SupportedSource.GOOGLE_NEWS)
        result.append(temp)
    return result