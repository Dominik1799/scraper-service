from utilities import request_util
from schemas.response import UrlDataResponse
from databases import redis


def get_url_data(url: str) -> UrlDataResponse:
    cached = redis.get_cached_raw_content(url)
    if cached is not None:
        return UrlDataResponse(raw_data=cached, downstream_response=200, got_response=False)
    response = request_util.proxy_request(url=url, req_method="GET")
    if response == None:
        return UrlDataResponse(raw_data="", downstream_response=0, got_response=False)
    html = response.text
    redis.store_raw_content(url, html)
    return UrlDataResponse(raw_data=html, downstream_response=response.status_code, got_response=True)