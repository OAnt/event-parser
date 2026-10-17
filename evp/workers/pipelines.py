from typing import Protocol
import requests

from evp.core.models.content import RemoteMedia, Post
from evp.core.models.events import Flyer
from evp.core.llm.llama import describe_concert_flyer
from evp.insta_api.retrieve_posts import retrieve_posts
from evp.workers.celery import app


class Writable(Protocol):
    def write(self, data: bytes, /) -> object: ...


def retrieve_media(remote_media: RemoteMedia, out: Writable, chunk_size: int = 1024):
    response = requests.get(remote_media.url)
    if response.ok:
        for chunk in response.iter_content(chunk_size=chunk_size):
            out.write(chunk)
    else:
        raise APIException(f"Could not download {remote_media.url}")


@app.task
def retrieve_and_store_posts(organization: str, *args, **kwargs):
    for post in retrieve_posts(organization, *args, **kwargs):
        post.storage.create_if_missing(post)


@app.task(queue="llama", pydantic=True)
def convert_post_to_flyer(post: Post) -> Flyer:
    return describe_concert_flyer(post)
