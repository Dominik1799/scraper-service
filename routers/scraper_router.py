from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/scraper", tags=["scraper"])

@router.get("/scrape", tags=["Scrape content on the provided URL"])
async def scrape_url(url: str = Query(...)):
    try:
        foo = 3
    except Exception as e:
        raise HTTPException(status_code=501, detail="Service failed to scrape provided URL")
