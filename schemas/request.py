from pydantic import BaseModel
from typing import List
from typing import Literal
from enum import Enum

class Topic(str, Enum):
    basic_check = "basic_check"


class SupportedCountry(str, Enum):
    SLOVAKIA = "slovakia"
    USA = "usa"
    GREAT_BRITAIN = "great_britain"
    GERMANY = "germany"
    CZECH_REPUBLIC = "czech_republic"