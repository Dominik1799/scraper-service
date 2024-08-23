from pydantic import BaseModel
from typing import List
from typing import Literal
from enum import Enum


class UrlDataResponse(BaseModel):
    data: str
    downstream_response: int
    got_reponse: bool


class UrlMetadataSourceType(str, Enum):
    GOOGLE_NEWS = "GOOGLE_NEWS"
    GOOGLE = "GOOGLE"

    
class UrlMetadata(BaseModel):
    url: str
    title: str
    source: Literal["GOOGLE_NEWS", "GOOGLE"]