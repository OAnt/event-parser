import os
from enum import IntEnum, Flag, auto
from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel, HttpUrl, FilePath, Field

from evp.core.models.db import StoredModelMixin 

class RemoteMedia(BaseModel):
    url: HttpUrl


class LocalMedia(BaseModel):
    path: FilePath

    @property
    def url(self):
        return f"file://{os.path.abspath(self.path)}"


class StateEnum(Flag):
    rated = auto()
    ingested = auto()
    processed = auto()

class QualityEnum(IntEnum):
    unknown = 0
    irrelevant = 10
    low_quality = 20
    high_quality = 30
    failed = 40

class State(BaseModel):
    rated: Optional[bool] = False
    ingested: Optional[bool] = False
    processed: Optional[bool] = False

class Post(BaseModel, StoredModelMixin):
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    media: Union[RemoteMedia, LocalMedia]
    state: Optional[State] = Field(default_factory=State, required=False)
    quality: QualityEnum = Field(default=QualityEnum.unknown)

    def rate(self):
        self.state.rated = True
        return self.storage.compare_and_set_field(self, ["state.rated"])

    def ingest(self):
        self.state.ingested = True
        return self.storage.compare_and_set_field(self, ["state.ingested"])

    def rewind(self):
        self.state.ingested = False
        return self.storage.compare_and_set_field(self, ["state.ingested"])
