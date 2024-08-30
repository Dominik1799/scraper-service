from asyncio.log import logger
import logging
import feedparser
from datetime import datetime, timedelta
from utilities.clients.decodeGoogleNewsUrl import decode_google_news_url
from utilities.request_util import proxy_request
from schemas.response import UrlMetadata, UrlMetadataSourceType
from schemas.request import SupportedCountry
import settings



class GnewsParser:
    __BASE_URL = "https://news.google.com/rss/search?q=<QUERY><DATERANGE><LOCALE>"
    __DATE_RANGE = "+after:<AFTER>+before:<BEFORE>"
    __LOCALE = {
        SupportedCountry.SLOVAKIA: "&hl=sk&gl=SK&ceid=SK:sk",
        SupportedCountry.USA: "&hl=en-US&gl=US&ceid=US:en",
        SupportedCountry.GREAT_BRITAIN: "&hl=en-GB&gl=GB&ceid=GB:en",
        SupportedCountry.GERMANY: "&hl=de&gl=DE&ceid=DE:de",
        SupportedCountry.CZECH_REPUBLIC: "&hl=cs&gl=CZ&ceid=CZ:cs",
        SupportedCountry.AUSTRALIA: "&hl=en-AU&gl=AU&ceid=AU%3Aen",
        SupportedCountry.NEW_ZEALAND: "&hl=en-NZ&gl=NZ&ceid=NZ%3Aen",
        # TODO: uncomment them when we add their support to SupportedCountries object
        # "bg-bg": "&hl=bg&gl=BG&ceid=BG:bg", # bulgarian
        # "fr-fr": "&hl=fr&gl=FR&ceid=FR:fr",
        # "fr-be": "&hl=fr&gl=BE&ceid=BE:fr", # belgium
        # "de-at": "&hl=de&gl=AT&ceid=AT:de", # austria
        # "de-ch": "&hl=de&gl=CH&ceid=CH:de", # switzerland
        # "el-gr": "&hl=el&gl=GR&ceid=GR:el", # greek
        # "nl-nl": "&hl=nl&gl=NL&ceid=NL:nl", # dutch
        # "nl-be": "&hl=nl&gl=BE&ceid=BE:nl", # belgium
        # "hu-hu": "&hl=hu&gl=HU&ceid=HU:hu",
        # "it-it": "&hl=it&gl=IT&ceid=IT:it",
        # "lv-lv": "&hl=lv&gl=LV&ceid=LV:lv", # latvia
        # "en-lv": "&hl=en-LV&gl=LV&ceid=LV:en", # latvia-eng
        # "lt-lt": "&hl=lt&gl=LT&ceid=LT:lt", # lithuania
        # "pl-pl": "&hl=pl&gl=PL&ceid=PL:pl", # polish
        # "pt-pt": "&hl=pt-PT&gl=PT&ceid=PT:pt-150", # portugal
        # "ro-ro": "&hl=ro&gl=RO&ceid=RO:ro", # romanian
        # "sl-sl": "&hl=sl&gl=SI&ceid=SI:sl",# slovenian
        # "uk-ua": "&hl=uk&gl=UA&ceid=UA:uk", # ukraine
        # "en-gl": "&hl=en-001", # global english articles
        # "en-au": "&hl=en-AU&gl=AU&ceid=AU%3Aen", # global english articles
        # "en-nz": "&hl=en-NZ&gl=NZ&ceid=NZ%3Aen" # global english articles
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

    def get_raw_results(self):
        gnews_response = proxy_request(self.__url, "GET", headers={'Cache-control': 'max-age=0'}, try_normal_request_first=True, timeout=15)
        logging.info("Url used for google news: " + self.__url)
        if gnews_response is None:
            return None
        res = feedparser.parse(gnews_response.text)
        return res["entries"]
    
    
    def get_articles(self, n=50) -> list:
        raw_results = self.get_raw_results()[0:n]
        results = []
        # get unix timestamp on each article
        # get correct urls
        for ent in raw_results:
            link = decode_google_news_url(ent["link"])
            if link:
                results.append({
                    "title": ent["title"],
                    "link": link,
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

def get_google_news_links(target_name, countries: list[SupportedCountry] = []) -> list[UrlMetadata]:
    # for this to work again we need requested language. Meaning we cannot create topic centered searches, only basic_checks
    # gnews_query = '"' + target_name + '"' + __create_topic_search_string(topic, language)
    gnews_query = '"' + target_name + '"'
    all_articles = []
    
    if len(countries) == 0:
        gp = GnewsParser(gnews_query)
        articles = gp.get_articles(n=10)
        all_articles.extend(articles)
    else:
        for country in countries:
            gp = GnewsParser(gnews_query, country=country)
            articles = gp.get_articles(n=10)
            all_articles.extend(articles)
    
    result = []
    for art in all_articles:
        temp = UrlMetadata(url=art["link"], title=art["title"], source=UrlMetadataSourceType.GOOGLE_NEWS)
        result.append(temp)
    return result