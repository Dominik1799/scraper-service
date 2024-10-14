import logging
from fastapi import BackgroundTasks
from settings import LOG_LEVEL
from utilities.parsers.d2m.d2m_extractor import extract_text_as_semantic_md
from utilities.parsers.readability.readability_extractor import extract_text_with_readability
from utilities.parsers.html2text.html2text_extractor import extract_text_with_html2text
from utilities.clients import GoogleNewsClient, GoogleSearchClient, BingNewsClient, BingSearchClient
from schemas.response import UrlMetadata, ContentScraping, ScrapeContentFromUrlResponse, UrlDataResponse
from schemas.request import SupportedCountry, SupportedSource
from schemas.dto import UrlMetadataDto
from databases import mongo
from services.request_service import get_url_data
import settings
import copy
import asyncio
from typing import Tuple
import httpx
from httpx import AsyncClient

logging.basicConfig(level=LOG_LEVEL)

def __extract_text(html: str) -> Tuple[str, bool]:
    if not settings.SCRAPE_WITH_PYTHON_ONLY:
        logging.debug("Trying extracting text with mozilla readability")
        text = extract_text_with_readability(html)
        if text is not None:
            logging.debug("Mozilla readabilty success, setting article flag to True")
            return text, True
        logging.debug("Trying extracting text as semantic markdown")
        text = extract_text_as_semantic_md(html)
        if text is not None:
            logging.debug("Semantic markdown success")
            return text, False
    logging.debug("Extracting via default html2text")
    return extract_text_with_html2text(html), False

async def __scrape_content_from_html(url: str, html: str) -> ContentScraping:
    cacheData = await mongo.get_cached_data(url)
    # if the existing documen
    if cacheData is not None and (cacheData.cannot_scrape or cacheData.parsed_content != ""):
        return ContentScraping(parsed_data=cacheData.parsed_content, is_probably_article=cacheData.is_probably_article)
    clean_text, article_flag = __extract_text(html)
    clean_text = clean_text if clean_text is not None else ""
    content = ContentScraping(parsed_data=clean_text, is_probably_article=article_flag)
    cannot_scrape = clean_text == "" or clean_text.isspace()
    mongo.upsert_url_data(url, html, clean_text, article_flag, cannot_scrape)
    return content



async def scrape_content_from_url(url: str) -> ScrapeContentFromUrlResponse:
    url_data: UrlDataResponse = await get_url_data(url)
    if url_data.downstream_response < 200 or url_data.downstream_response >= 400:
        return ScrapeContentFromUrlResponse(is_probably_article=False, parsed_data="", raw_html="", failed=True)
    
    parsed_data = await __scrape_content_from_html(url, url_data.raw_data)
    failed_flag = parsed_data.parsed_data.isspace() # if the parsed content is only whitespace, return as failed
    return ScrapeContentFromUrlResponse(parsed_data=parsed_data.parsed_data,
                                        raw_html=url_data.raw_data,
                                        is_probably_article=parsed_data.is_probably_article,
                                        failed=failed_flag)



def __is_social_media(url) -> bool:
    for sm in settings.SOCIAL_MEDIA_WEBSITES:
        if sm in url:
            return True
    return False

async def __is_file_hardcore_version(url: str, http_client: AsyncClient) -> bool:
    try:
        head = await http_client.head(url)
        if head.status_code > 299:
            # fuck it, bail
            return False
        content_type = head.headers.get('Content-Type')
        if content_type and 'html' in content_type:
            return False
        return True
    # what to return in exceptions?
    except httpx.TimeoutException:
        logging.warning(f"Got ReadTimeout from HEAD {url}")
        return False
    except Exception:
        logging.exception(f"Exception occured while making HEAD request to {url}")
        return False


def __is_file_ez_version(url: str) -> bool:
    for extension in settings.FILE_EXTENSIONS:
        if url.endswith(f".{extension}"):
            return True
    return False


async def get_urls_about_target(target_name: str, countries: list[SupportedCountry], 
                                sources: list[SupportedSource], remove_social_media: bool = True, 
                                keywords: list[str] = [], bg_task: BackgroundTasks = None) -> list[UrlMetadata]:
    temp_result: list[UrlMetadataDto] = []
    sources = set(sources)
    tasks = []
    tasks.append(mongo.get_cached_urls(target_name, countries, sources, keywords))
    if (SupportedSource.GOOGLE_NEWS in sources):
        logging.debug("Getting google news links")
        tasks.append(GoogleNewsClient.get_google_news_links(target_name, countries, keywords))
    if (SupportedSource.BING_NEWS in sources):
        logging.debug("Getting bing news links")
        tasks.append(BingNewsClient.get_bing_news_results(target_name, countries, keywords))
    if (SupportedSource.GOOGLE in sources):
        logging.debug("Getting google search links")
        tasks.append(GoogleSearchClient.get_google_search_links(target_name, countries, keywords))
    if (SupportedSource.BING in sources):
        logging.debug("Getting bing links")
        tasks.append(BingSearchClient.get_bing_search_results(target_name, countries, keywords))
    gathered_results: list[list[UrlMetadataDto]] = await asyncio.gather(*tasks)
    cached: list[UrlMetadata] = [UrlMetadata(url=c.url, title=c.title, source=c.source) for c in gathered_results[0]]
    for res in gathered_results[1:]: # index 0 contains cached results
        temp_result.extend(res)
    # remove social media
    no_social_media_result = temp_result if not remove_social_media else [r for r in temp_result if not __is_social_media(r.url)]
    # remove files ez
    no_files_result = [r for r in no_social_media_result if not __is_file_ez_version(r.url)]
    # remove files hardcore
    clean_results: list[UrlMetadata] = []
    tasks = []
    async with httpx.AsyncClient() as client:
        for res in no_files_result:
            tasks.append(__is_file_hardcore_version(res.url, client))
        result_flags = await asyncio.gather(*tasks)
        for i in range(0, len(no_files_result)):
            # if is file, continue
            if result_flags[i]:
                continue
            clean_results.append(no_files_result[i])
    # cache newly found URLs in the background
    bg_task.add_task(mongo.upsert_found_urls, copy.deepcopy(clean_results), target_name, keywords)
    # now add cached URLs
    clean_results.extend(cached)
    logging.debug("Data fetching done. Deduplicating...")
    result: list[UrlMetadata] = []
    seen_urls = set()
    # deduplicate
    for res in clean_results:
        if res.url in seen_urls:
            continue
        seen_urls.add(res.url)
        result.append(UrlMetadata(url=res.url, title=res.title, source=res.source))
    return result
    