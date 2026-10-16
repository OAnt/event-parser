from __future__ import annotations
import logging
from typing import Optional, ClassVar, Self

import requests
from pydantic import Field

from evp import conf
from evp.core.exceptions import APIException
from evp.core.models.content import Post, RemoteMedia
from evp.core.models.db import register_model, MongoStorage


log = logging.getLogger(__name__)


class InstagramPost(Post):
    storage: ClassVar[MongoStorage[InstagramPost]]
    description: Optional[str] = Field(validation_alias="caption", default=None)
    media_type: Optional[str] = None
    id: str


InstagramPost.storage = register_model(InstagramPost, "id")


def retrieve_posts(organization: str):
    url = f"{conf.GRAPH}/{conf.INSTA_ID}"
    log.info(url)
    response = requests.get(
        url , {
            "fields": "business_discovery.username(%s){media{caption,media_url,timestamp,media_type}}" % (organization,),
            "access_token": conf.TOKEN,
        },
    )
    data = response.json()
    if response.ok:
        posts = data["business_discovery"]["media"]["data"]
        for post in filter(lambda x: "media_url" in x, posts):
            media = RemoteMedia(url=post.pop("media_url"))
            instagram_post = InstagramPost(media=media, **post)
            yield instagram_post
    else:
        raise APIException(data["error"])
