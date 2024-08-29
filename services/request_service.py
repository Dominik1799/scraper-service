from utilities import request_util
from schemas.response import UrlDataResponse



def get_url_data(url: str) -> UrlDataResponse:
    response = request_util.proxy_request(url=url, req_method="GET")
    if response == None:
        return UrlDataResponse(data="", downstream_response=0, got_response=False)
    return UrlDataResponse(data=response.text, downstream_response=response.status_code, got_response=True)