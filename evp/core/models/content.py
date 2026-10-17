import os
from enum import IntEnum
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


class StateEnum(IntEnum):
    retrieved = 0
    rated = 20
    ingested = 30
    processed = 40

class QualityEnum(IntEnum):
    unknown = 0
    irrelevant = 10
    low_quality = 20
    high_quality = 30
    failed = 40

class Post(BaseModel, StoredModelMixin):
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    media: Union[RemoteMedia, LocalMedia]
    state: StateEnum = Field(default=StateEnum.retrieved)
    quality: QualityEnum = Field(default=QualityEnum.unknown)

    def rate(self):
        self.state = StateEnum.rated
        return self.storage.compare_and_set_field(self, ["state"])

    def ingest(self):
        self.state = StateEnum.ingested
        return self.storage.compare_and_set_field(self, ["state"])

    def rewind(self):
        self.state = StateEnum.retrieved
        return self.storage.compare_and_set_field(self, ["state"])
