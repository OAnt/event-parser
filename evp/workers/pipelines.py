from typing import Protocol
import requests

from evp.core.models.content import RemoteMedia, StateEnum, QualityEnum
from evp.core.models.events import Flyer
from evp.core.llm.llama import describe_concert_flyer, rate_post
from evp.insta_api.retrieve_posts import retrieve_posts, InstagramPost
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
        post.create_if_missing()

@app.task(queue="llama", pydantic=True)
def rate_post_quality(post: InstagramPost):
    if not post.state.rated and post.rate():
        post.quality = rate_post(post)
        post.storage.compare_and_set_field(post, ["quality"])

@app.task(queue="llama", pydantic=True)
def convert_post_to_flyer(post: InstagramPost):
    if not post.state.ingested and post.ingest():
        flyer = describe_concert_flyer(post)
        flyer.insert()
