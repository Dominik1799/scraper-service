from utilities import request_util
from schemas.response import UrlDataResponse
from databases import mongo


async def get_url_data(url: str) -> UrlDataResponse:
    cached = await mongo.get_cached_data(url)
    if cached is not None and cached.cannot_scrape:
        return UrlDataResponse(raw_data="", downstream_response=0, got_response=False)
    if cached is not None and cached.raw_html != "":
        return UrlDataResponse(raw_data=cached.raw_html, downstream_response=200, got_response=False)
    response = await request_util.async_proxy_request(url=url, req_method="GET")
    if response == None:
        mongo.upsert_url_data(url, html, "", cannot_scrape=True)
        return UrlDataResponse(raw_data="", downstream_response=0, got_response=False)
    html = response.text
    mongo.upsert_url_data(url, html, "")
    return UrlDataResponse(raw_data=html, downstream_response=response.status_code, got_response=True)