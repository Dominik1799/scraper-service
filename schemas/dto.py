from pydantic import BaseModel
from schemas.response import UrlMetadataSourceType, UrlMetadata
from schemas.request import SupportedCountry



class TargetSearchCache(BaseModel):
    key: str
    matched_urls: list[UrlMetadata]

class UrlDataCache(BaseModel):
    url: str
    title: str = ""
    source: UrlMetadataSourceType
    raw_html: str
    parsed_content: str
    is_probably_article: bool = False


class UrlDataCache(BaseModel):
    url: str
    title: str = ""
    source: UrlMetadataSourceType = None
    raw_html: str
    parsed_content: str
    is_probably_article: bool = False
    matched_targets: list[str]
    countries: list[SupportedCountry] = []
    