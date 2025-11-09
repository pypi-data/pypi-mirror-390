import os
import json
from .process_ab_listing import process_ab_listing
from .process_home_listing import process_home_listing

def process(config_dir: str):
    if not os.path.isdir(config_dir):
        raise FileNotFoundError(f"config_dir {config_dir} needs to be created")

    browser_dir = f"{config_dir}/chromium"
    listings = json.load(open(f"{config_dir}/listings.json"))
    secrets = json.load(open(f"{config_dir}/secrets.json"))

    for listing in listings:
        if listing['type'] == 'home':
            process_home_listing(listing, secrets)

    for listing in listings:
        if listing['type'] == 'airbnb':
            process_ab_listing(browser_dir, listing, secrets)

