import json
import hashlib
import requests
import csv
from io import StringIO
from goose3 import Goose, Configuration

config = Configuration()
config.http_timeout = 10
g = Goose(config)


def hash_website(url):
    # verify is False since some of the government websites don't work for some reason if verify is True
    # fix maybe in the future?
    return hashlib.sha512(g.extract(url).cleaned_text.encode("utf-8")).hexdigest()


with open("config.json", "r") as f:
    info = json.load(f)
    spreadsheet_link = info["spreadsheet_link"]
    website_hashes_file = info["website_hashes_file"]

r = requests.get(spreadsheet_link)
text = StringIO(r.text)
reader = csv.reader(text)

rows = [row[1:] for row in reader][1:]

headers = rows[0]
side_headers = [row[0] for row in rows]

website_hashes = {}

for state_index, state in list(enumerate(side_headers))[1:]:

    print(state)

    for item_index, item in list(enumerate(headers))[1:]:

        url = rows[state_index][item_index]

        if url == "":
            continue

        print(url)

        try:
            website_hashes[url] = hash_website(url)
        except requests.exceptions.RequestException:
            website_hashes[url] = "Timed Out"
            continue

with open(website_hashes_file, "w") as f:
    json.dump(website_hashes, f)