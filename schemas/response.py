from pydantic import BaseModel
from typing import List
from typing import Literal



class UrlDataResponse(BaseModel):
    data: str
    downstream_response: int
    got_reponse: bool
    
    
class UrlMetadata(BaseModel):
    url: str
    title: str
    source: Literal["GOOGLE_NEWS", "GOOGLE"]