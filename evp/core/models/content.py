import os
from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel, HttpUrl, FilePath

class RemoteMedia(BaseModel):
    url: HttpUrl


class LocalMedia(BaseModel):
    path: FilePath

    @property
    def url(self):
        return f"file://{os.path.abspath(self.path)}"


class Post(BaseModel):
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    media: Union[RemoteMedia, LocalMedia]
