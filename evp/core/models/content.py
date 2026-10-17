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
    ingested = 1
    processed = 2

class Post(BaseModel, StoredModelMixin):
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    media: Union[RemoteMedia, LocalMedia]
    state: StateEnum = Field(default=StateEnum.retrieved)
