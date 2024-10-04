from pydantic import BaseModel
from schemas.request import SupportedCountry, SupportedSource


class UrlDataCache(BaseModel):
    url: str
    title: str = ""
    sources: list[SupportedSource] = []
    raw_html: str
    parsed_content: str
    is_probably_article: bool = False
    matched_targets: list[str]
    countries: list[SupportedCountry] = []
    cannot_scrape: bool = False
    