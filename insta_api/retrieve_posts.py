import logging
from datetime import datetime
from typing import Optional

import requests
from pydantic import BaseModel, HttpUrl, Field

from insta_api import conf
from core.exceptions import APIException
from core.models.content import RemoteMedia


log = logging.getLogger(__name__)


class InstagramPost(RemoteMedia):
    caption: Optional[str] = None
    url: Optional[HttpUrl] = Field(default=None, validation_alias="media_url")
    timestamp: Optional[datetime] = None
    media_type: Optional[str] = None
    id: str


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
        for post in data["business_discovery"]["media"]["data"]:
            instagram_post = InstagramPost(**post)
            yield instagram_post
    else:
        raise APIException(data["error"])
