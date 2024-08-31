from enum import Enum
from pydantic import BaseModel

class Topic(str, Enum):
    basic_check = "basic_check"


class SupportedCountry(str, Enum):
    SLOVAKIA = "slovakia"
    USA = "usa"
    GREAT_BRITAIN = "great_britain"
    GERMANY = "germany"
    CZECH_REPUBLIC = "czech_republic"
    AUSTRALIA = "australia"
    NEW_ZEALAND = "new_zealand"


class SupportedSource(str, Enum):
    GOOGLE_NEWS = "google_news"
    GOOGLE = "google"
    BING_NEWS = "bing_news"
    BING = "bing"
    
class ParseHtmlRequest(BaseModel):
    url: str
    html: str