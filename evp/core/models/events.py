from __future__ import annotations
import datetime
from typing import Optional, List
from pydantic import BaseModel

from evp.core.models.db import register_model, MongoStorage

class Event(BaseModel):
    storage: ClassVar[MongoStorage[Event]]
    venue: str
    date: datetime.date
    performers: List[str]


Event.storage = register_model(Event)


class Flyer(BaseModel):
    reasoning: Optional[str]
    events: List[Event]
