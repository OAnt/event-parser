import datetime
from typing import Optional, List
from pydantic import BaseModel

class Event(BaseModel):
    venue: str
    date: datetime.date
    performers: List[str]


class Flyer(BaseModel):
    reasoning: Optional[str]
    events: List[Event]
