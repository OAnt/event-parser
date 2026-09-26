import argparse
import logging
import sys

from insta_api.retrieve_posts import retrieve_posts

parser = argparse.ArgumentParser(
    prog="post-retriever",
    description="Retrieves posts for a specified list of accounts"
)
parser.add_argument("--account", nargs="+", help="Name of an account to scrap")

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    for account in args.account:
        posts = retrieve_posts(account)
        print(list(posts))
