import logging
from settings import LOG_LEVEL
from utilities.parsers import html2text, readabilipy
from databases.redis import get_cached_scraped_content, store_cached_scraped_content
from utilities.clients import GoogleNewsClient, GoogleSearchClient, BingNewsClient, BingSearchClient
from schemas.response import UrlMetadata, ContentScraping, ScrapeContentFromUrlResponse, UrlDataResponse
from schemas.request import SupportedCountry, SupportedSource
from services.request_service import get_url_data

logging.basicConfig(level=LOG_LEVEL)


def __scrape_content_from_html(url: str, html: str) -> ContentScraping:
    # check cache
    content = get_cached_scraped_content(url)
    if content is not None:
        return content
    article_flag = False
    # first try readability from mozila
    data = readabilipy.parse_html(html)
    if data is not None:
        article_flag = True
    else:
        # now just extract using html2text
        data = html2text.parse_html(html)
    data = data if data is not None else ""
    content = ContentScraping(parsed_data=data, is_probably_article=article_flag)
    store_cached_scraped_content(url, content)
    return content



def scrape_content_from_url(url: str) -> ScrapeContentFromUrlResponse:
    url_data: UrlDataResponse = get_url_data(url)
    if url_data.downstream_response < 200 and url_data.downstream_response >= 400:
        return ScrapeContentFromUrlResponse(is_probably_article=False, parsed_data=None, raw_html=None, failed=True)
    
    parsed_data = __scrape_content_from_html(url, url_data.raw_data)
    failed_flag = parsed_data.parsed_data.isspace() # if the parsed content is only whitespace, return as failed
    return ScrapeContentFromUrlResponse(parsed_data=parsed_data.parsed_data,
                                        raw_html=url_data.raw_data,
                                        is_probably_article=parsed_data.is_probably_article,
                                        failed=failed_flag)





def get_urls_about_target(target_name: str, countries: list[SupportedCountry], sources: list[SupportedSource]) -> list[UrlMetadata]:
    temp_result: list[UrlMetadata] = []
    sources = set(sources)
    if (SupportedSource.GOOGLE_NEWS in sources):
        logging.info("Getting google news links")
        temp_result.extend(GoogleNewsClient.get_google_news_links(target_name, countries))
    if (SupportedSource.BING_NEWS in sources):
        logging.info("Getting bing news links")
        temp_result.extend(BingNewsClient.get_bing_news_results(target_name, countries))
    if (SupportedSource.GOOGLE in sources):
        logging.info("Getting google search links")
        temp_result.extend(GoogleSearchClient.get_google_search_links(target_name, countries))
    if (SupportedSource.BING in sources):
        logging.info("Getting bing links")
        temp_result.extend(BingSearchClient.get_bing_search_results(target_name, countries))
    
    logging.info("Data fetching done. Deduplicating...")
    result: list[UrlMetadata] = []
    seen_urls = set()
    for res in temp_result:
        if res.url in seen_urls:
            continue
        result.append(res)
    return result
    