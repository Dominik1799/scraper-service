from enum import Enum
from pydantic import BaseModel

class Topic(str, Enum):
    basic_check = "basic_check"


class SupportedCountry(str, Enum):
    USA = "usa"
    AUSTRALIA = "australia"
    NEW_ZEALAND = "new_zealand"
    GREAT_BRITAIN = "great_britain"
    # EU
    GERMANY = "germany"
    CZECHIA = "czechia"
    SLOVAKIA = "slovakia"
    ITALY = "italy"
    AUSTRIA = "austria"
    BELGIUM = "belgium"
    BULGARIA = "bulgaria"
    CROATIA = "croatia"
    CYPRUS = "cyprus"
    DENMARK = "denmark"
    ESTONIA = "estonia"
    FINLAND = "finland"
    FRANCE = "france"
    GREECE = "greece"
    HUNGARY = "hungary"
    IRELAND = "ireland"
    LATVIA = "latvia"
    LITHUANIA = "lithuania"
    LUXEMBOURG = "luxembourg"
    MALTA = "malta"
    NETHERLANDS = "netherlands"
    POLAND = "poland"
    PORTUGAL = "portugal"
    ROMANIA = "romania"
    SLOVENIA = "slovenia"
    SPAIN = "spain"
    SWEDEN = "sweden"
    


class SupportedSource(str, Enum):
    GOOGLE_NEWS = "google_news"
    GOOGLE = "google"
    BING_NEWS = "bing_news"
    BING = "bing"
    
class ParseHtmlRequest(BaseModel):
    url: str
    html: str