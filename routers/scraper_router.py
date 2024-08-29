import logging
from fastapi import APIRouter, Query, HTTPException
from services import scraper_service
from settings import LOG_LEVEL
from typing import List
from schemas.response import UrlMetadata
from schemas.request import SupportedCountry, SupportedSource

logging.basicConfig(level=LOG_LEVEL)

router = APIRouter(prefix="/scraper", tags=["Scrape content"])

@router.get("/scrape", description="Scrape content on the provided URL")
async def scrape_url(url: str = Query(...)):
    try:
        article_data = scraper_service.scrape_content_from_url(url=url)
        return article_data
    except Exception as e:
        logging.exception("Error: ")
        return HTTPException(status_code=500, detail="Failed to scrape the content from the provided URL due to the server error.")


@router.get("/links-about-target", description="Scrape URLs about a target from various sources")
def get_links_about_target(target_name: str, 
                           country: List[SupportedCountry] = Query(max_length=3, default = []),
                           source: List[SupportedSource] = Query(default = [SupportedSource.GOOGLE_NEWS], min_length=1)) -> list[UrlMetadata]:
    try:
        result = scraper_service.get_urls_about_target(target_name, country, source)
        return result
    except Exception:
        logging.exception("Error: ")
        return HTTPException(status_code=500, detail="Failed to aquire URLS about target")