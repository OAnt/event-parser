from typing import Protocol
import requests

from core.models.content import RemoteMedia


class Writable(Protocol):
    def write(self, data: bytes, /) -> object: ...


def retrieve_media(remote_media: RemoteMedia, out: Writable, chunk_size: int = 1024):
    response = requests.get(remote_media.url)
    if response.ok:
        for chunk in response.iter_content(chunk_size=chunk_size):
            out.write(chunk)
    else:
        raise APIException(f"Could not download {remote_media.url}")
