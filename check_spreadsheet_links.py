import requests
import csv
from io import StringIO
from smtplib import SMTP
import json
import hashlib


def hash_website(url):
    # verify is False since some of the government websites don't work for some reason if verify is True
    # fix maybe in the future?
    return hashlib.sha512(requests.get(url, verify=False).content).hexdigest()


def check_url_hash(url):
    hash_content = hash_website(url)
    return hash_content == website_hashes[url], hash_content


with open("config.json", "r") as f:
    info = json.load(f)
    email = info["email"]
    password = info["password"]
    recipients = info["recipients"]
    spreadsheet_link = info["spreadsheet_link"]
    website_hashes_file = info["website_hashes_file"]

    with open(website_hashes_file) as f:
        website_hashes = json.load(f)

r = requests.get(spreadsheet_link)
text = StringIO(r.text)
reader = csv.reader(text)

rows = [row[1:] for row in reader][1:]

headers = rows[0]
side_headers = [row[0] for row in rows]

with SMTP() as smtp:

    for state_index, state in list(enumerate(side_headers))[1:]:

        for item_index, item in list(enumerate(headers))[1:]:

            url = rows[state_index][item_index]

            if url == "":
                continue

            has_changed, hash_content = check_url_hash(url)

            if has_changed:

                msg = "From: " + email + "\nSubject: The link " + url + " may need to be updated\nThe content on " + url + " has changed and the link may need to be updated. The column is " + item + " and the state is " + state + "."

                smtp.connect()
                smtp.login(email, password)
                smtp.sendmail(email, recipients, msg)

                website_hashes[url] = hash_content

with open(website_hashes_file, "w") as f:
    json.dump(website_hashes, f)
