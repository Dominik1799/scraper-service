import logging
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from services import scraper_service
from settings import LOG_LEVEL
from typing import List
from schemas.response import UrlMetadata, ContentScraping, ScrapeContentFromUrlResponse
from schemas.request import SupportedCountry, SupportedSource, ParseHtmlRequest

logging.basicConfig(level=LOG_LEVEL)

router = APIRouter(prefix="/scraper", tags=["Scrape content"])

@router.get("/scrape", description="Scrape content on the provided URL. Return raw data and also parsed data.")
async def scrape_url(url: str = Query(...)) -> ScrapeContentFromUrlResponse:
    try:
        data = await scraper_service.scrape_content_from_url(url=url)
        return data
    except Exception as e:
        logging.exception("Error: ")
        return HTTPException(status_code=500, detail="Failed to scrape the content from the provided URL due to the server error.")

@router.get("/links-about-target", description="Scrape URLs about a target from various sources")
async def get_links_about_target(target_name: str, 
                           country: List[SupportedCountry] = Query(max_length=3, default = []),
                           source: List[SupportedSource] = Query(default = [SupportedSource.GOOGLE_NEWS], min_length=1),
                           keywords: List[str] = Query(default=[]),
                           background_tasks: BackgroundTasks = None) -> list[UrlMetadata]:
    try:
        result = await scraper_service.get_urls_about_target(target_name, country, 
                                                             source, remove_social_media=True, 
                                                             keywords=keywords, bg_task=background_tasks)
        return result
    except Exception:
        logging.exception("Error: ")
        return HTTPException(status_code=500, detail="Failed to aquire URLS about target")