from fastapi import APIRouter, Query, HTTPException
from services import scraper_service

router = APIRouter(prefix="/scraper", tags=["scraper"])

@router.get("/scrape", tags=["Scrape content on the provided URL"])
async def scrape_url(url: str = Query(...)):
    try:
        article_data = scraper_service.scrape_content_from_url(url=url)
        return article_data
    except Exception as e:
        raise HTTPException(status_code=501, detail="Service failed to scrape provided URL")
