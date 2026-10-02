import argparse
import logging
import sys

from core.exceptions import APIException
from core.pipelines.content import retrieve_media
from core.llm.llama import describe_concert_flyer_2
from insta_api.retrieve_posts import retrieve_posts

parser = argparse.ArgumentParser(
    prog="post-retriever",
    description="Retrieves posts for a specified list of accounts"
)
parser.add_argument("--account", nargs="+", help="Name of an account to scrap")
parser.add_argument(
    "--folder",
    nargs="?",
    default="data/images",
    help="Folder to store resulting images",
)

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    for account in args.account:
        posts = retrieve_posts(account)
        for post in posts:
            print(describe_concert_flyer_2(post))
            # filename = f"{args.folder}/{post.id}.jpg"
            # with open(filename, "wb") as f:
                # try:
                    # retrieve_media(post, f)
                # except APIException as e:
                    # log.warning(e)
