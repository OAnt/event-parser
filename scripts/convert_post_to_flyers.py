#!/usr/bin/env python3

import argparse

from evp.insta_api.retrieve_posts import InstagramPost
from evp.workers.pipelines import convert_post_to_flyer

parser = argparse.ArgumentParser(
    prog="post-converter",
    description="Converts Instagram post into Flyers",
)
parser.add_argument("--account", nargs="+", help="Accounts to process")

if __name__ == "__main__":
    args = parser.parse_args()
    for account in args.account:
        posts = InstagramPost.storage.collection.find({
            "account": account
        })
        for _post in posts:
            post = InstagramPost(**_post)
            convert_post_to_flyer.delay(post.model_dump(mode="json"))
