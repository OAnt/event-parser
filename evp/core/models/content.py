import os
from pydantic import BaseModel, HttpUrl, FilePath

class RemoteMedia(BaseModel):
    url: HttpUrl

class LocalMedia(BaseModel):
    path: FilePath

    @property
    def url(self):
        return f"file://{os.path.abspath(self.path)}"
