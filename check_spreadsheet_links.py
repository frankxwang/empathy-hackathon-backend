import requests
import csv
from io import StringIO
from smtplib import SMTP
import json
import hashlib


def hash_website(url):
    # verify is False since some of the government websites don't work for some reason if verify is True
    # fix maybe in the future?
    return hashlib.sha512(requests.get(url, verify=False, timeout=10).content).hexdigest()


def check_url_hash(url):
    hash_content = hash_website(url)
    return (hash_content != website_hashes[url]), hash_content


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

urls_changed = []
urls_timeout = []

for state_index, state in list(enumerate(side_headers))[1:]:

    print(state)

    for item_index, item in list(enumerate(headers))[1:]:

        url = rows[state_index][item_index]

        if url == "":
            continue

        print(url)

        try:
            has_changed, hash_content = check_url_hash(url)
        except requests.exceptions.RequestException:
            urls_timeout.append((url, state, item))
            continue

        if has_changed:
            urls_changed.append((url, state, item))
            website_hashes[url] = hash_content

with SMTP() as smtp:

    msg = "From: " + email + "\nSubject: firststep.id Daily Links Update\n"
    msg += "Websites whose content has been changed:\n"
    for info in urls_changed:
        url, state, item = info
        msg += "\n"
        msg += "State: " + state + ", Item: " + item + "\n"
        msg += "Link: " + url + "\n"

    msg += "\nWebsites that the Python scripts could not access (need to be manually checked):\n"
    for info in urls_timeout:
        url, state, item = info
        msg += "\n"
        msg += "State: " + state + ", Item: " + item + "\n"
        msg += "Link: " + url + "\n"

    smtp.connect()
    smtp.login(email, password)
    smtp.sendmail(email, recipients, msg)

with open(website_hashes_file, "w") as f:
    json.dump(website_hashes, f)
