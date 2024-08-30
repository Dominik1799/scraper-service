import logging
from fastapi import APIRouter, Query, HTTPException
from services import request_service
from settings import LOG_LEVEL
from schemas.response import UrlDataResponse

logging.basicConfig(level=LOG_LEVEL)

router = APIRouter(prefix="/request", tags=["Make any HTTP request"])

@router.get("/get", description="Make downstream HTTP GET request. Returns object with raw page data")
async def get_url_content(url: str = Query(...)) -> UrlDataResponse:
    try:
        url_data = request_service.get_url_data(url)
        return url_data
    except Exception as e:
        logging.exception("Error: ")
        return HTTPException(status_code=500, detail="Failed to scrape the content from the provided URL due to the server error.")
