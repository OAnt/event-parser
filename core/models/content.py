from typing import Optional

from pydantic import BaseModel, HttpUrl

class RemoteMedia(BaseModel):
    url: Optional[HttpUrl] = None
