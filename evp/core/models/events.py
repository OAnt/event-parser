from __future__ import annotations
import datetime
from typing import Optional, List
from pydantic import BaseModel

from evp.core.models.db import StoredModelMixin, register_model

# I decided to store both Flyer and Event because different Flyers
# may report the same event, I need to add a duplicate detection
# phase to obtain events which would be the final clean model,
# reasoning might contains clues to determine if events are 
# duplicates

class Event(BaseModel, StoredModelMixin):
    venue: str
    date: datetime.date
    performers: List[str]


Event.storage = register_model(Event)


class Flyer(BaseModel, StoredModelMixin):
    reasoning: Optional[str]
    events: List[Event]


Flyer.storage = register_model(Flyer)
