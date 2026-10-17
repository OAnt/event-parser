#!/usr/bin/env python3

import argparse
import json
import logging
import sys

from evp.workers.pipelines import retrieve_and_store_posts

log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog="data-importer",
    description="Retrieves posts for a specified list of accounts"
)
parser.add_argument(
    "--instagram-account-conf",
    nargs="?",
    help="Configuration file with the list of account to import",
    default="conf/instagram-accounts.json"
)

if __name__ == "__main__":
    args = parser.parse_args()
    instagram_conf_path = args.instagram_account_conf
    if instagram_conf_path:
        log.info("Importing from Instagram")
        with open(instagram_conf_path, "r") as f:
            accounts = json.load(f)
        for account in accounts:
            log.info(f"Importing {account}")
            retrieve_and_store_posts.delay(
                account["name"],
                limit=account["limit"],
                pages=account["pages"],
            )
