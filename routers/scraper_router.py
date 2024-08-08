import logging
from fastapi import APIRouter, Query, HTTPException
from services import scraper_service
from settings import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

router = APIRouter(prefix="/scraper", tags=["scraper"])

@router.get("/scrape", tags=["Scrape content on the provided URL"])
async def scrape_url(url: str = Query(...)):
    try:
        article_data = scraper_service.scrape_content_from_url(url=url)
        return article_data
    except Exception as e:
        logging.error(e)
        return HTTPException(status_code=500, detail="Failed to scrape the content from the provided URL due to the server error.")
