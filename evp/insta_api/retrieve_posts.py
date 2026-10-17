from __future__ import annotations
import logging
from typing import Optional, Self

import requests
from pydantic import Field

from evp import conf
from evp.core.exceptions import APIException
from evp.core.models.content import Post, RemoteMedia
from evp.core.models.db import register_model, MongoStorage


log = logging.getLogger(__name__)


class InstagramPost(Post):
    description: Optional[str] = Field(validation_alias="caption", default=None)
    media_type: Optional[str] = None
    id: str
    account: str


InstagramPost.storage = register_model(InstagramPost, "id")


def retrieve_posts(organization: str, limit:int = 25, page_count: int = 1):
    url = f"{conf.GRAPH}/{conf.INSTA_ID}"
    _media_insta_spec = f"media.limit({limit})"
    media_insta_spec = _media_insta_spec
    for i in range(0, page_count):
        search_string = "business_discovery.username(%s){%s{caption,media_url,timestamp,media_type}}" % (
            organization, media_insta_spec
        )
        log.info(f"{organization}:{i} => {url}, {search_string}")
        response = requests.get(
            url , {
                "fields": search_string,
                "access_token": conf.TOKEN,
            },
        )
        data = response.json()
        if response.ok:
            posts = data["business_discovery"]["media"]["data"]
            log.info(f"found {len(posts)} for {organization}")
            for post in filter(lambda x: "media_url" in x, posts):
                media = RemoteMedia(url=post.pop("media_url"))
                instagram_post = InstagramPost(
                    media=media, account=organization, **post
                )
                yield instagram_post
            after = data["business_discovery"]["media"]["paging"]["cursors"].get("after", None)
            if after:
                log.info(f"found next page {after}")
                media_insta_spec = f"{_media_insta_spec}.after({after})"
            else:
                log.info(f"No more pages")
                break;
        else:
            raise APIException(data["error"])
