import argparse
import os
import requests

from evp.insta_api import conf

parser = argparse.ArgumentParser(
    prog="fb-token-retriever",
    description="Retrieves a long term token from Facebook using a short term one",
    epilog="Assumes both FB_APP_ID and FB_APP_SECRET environment variable are available",
)
parser.add_argument('short_term_token')

if __name__ == "__main__":
    args = parser.parse_args()
    app_secret = os.environ["FB_APP_SECRET"]
    app_id = os.environ["FB_APP_ID"]
    token_response = requests.get(
        f"{conf.GRAPH}/oauth/access_token", {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": args.short_term_token,
        }
    )
    token_data = token_response.json()
    long_term_token = token_data['access_token']
    print(long_term_token)
    account_response = requests.get(
        f"{conf.GRAPH}/me/accounts", {
            "access_token": long_term_token
        },
    )
    account_data = account_response.json()
    print(account_data)
