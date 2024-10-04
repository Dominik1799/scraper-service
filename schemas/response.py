from pydantic import BaseModel
from enum import Enum
from schemas.request import SupportedSource


class UrlDataResponse(BaseModel):
    raw_data: str
    downstream_response: int
    got_response: bool

    
class UrlMetadata(BaseModel):
    url: str
    title: str
    source: SupportedSource

class ContentScraping(BaseModel):
    parsed_data: str
    is_probably_article: bool
    
class ScrapeContentFromUrlResponse(BaseModel):
    parsed_data: str
    raw_html: str
    is_probably_article: bool
    failed: bool