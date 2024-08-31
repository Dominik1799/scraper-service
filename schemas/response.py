from pydantic import BaseModel
from enum import Enum


class UrlDataResponse(BaseModel):
    raw_data: str
    downstream_response: int
    got_response: bool


class UrlMetadataSourceType(str, Enum):
    GOOGLE_NEWS = "GOOGLE_NEWS"
    GOOGLE = "GOOGLE"
    BING_NEWS = "BING_NEWS"
    BING = "BING"

    
class UrlMetadata(BaseModel):
    url: str
    title: str
    source: UrlMetadataSourceType

class ContentScraping(BaseModel):
    parsed_data: str
    is_probably_article: bool
    
class ScrapeContentFromUrlResponse(BaseModel):
    parsed_data: str
    raw_html: str
    is_probably_article: bool
    failed: bool