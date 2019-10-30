from flask import Flask
import csv
import requests
from io import StringIO
import hashlib
from smtplib import SMTP
import json

app = Flask(__name__)

application = app

spreadsheet_link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vREryrwAkgkB-fsWClSUogKrhAMxeo9D1Tgs3lHWUIw5K-OTDd66XdsmRVfZ2qnzwIzZr8RBbKWBxLo/pub?gid=0&single=true&output=csv"


def check_url(url):
    return requests.get(url).status_code == 200


def hash_website(url):
    return hashlib.sha256(requests.get(url).content).hexdigest()

# item is the column, state is abbreviation
@app.route('/get_url/<item>/<state>')
def get_url_from_spreadsheet(item, state):
    r = requests.get(spreadsheet_link)
    text = StringIO(r.text)
    reader = csv.reader(text)

    rows = [row for row in reader][1:]

    headers = rows[0]
    side_headers = [row[1] for row in rows]

    state_index = side_headers.index(state)
    item_index = headers.index(item)

    return rows[state_index][item_index]


@app.route("/get_embassy/<country>")
def get_url_embassy(country):
    return "https://embassy.goabroad.com/embassies-of/" + country


# currently not used
def check_url_from_spreadsheet(item, state):
    url = get_url_from_spreadsheet(item, state)
    if url != "" and not check_url(url):
        with SMTP("firststep.id") as smtp:
            with open("config.json", "r") as f:
                info = json.load(f)
                email = info["email"]
                password = info["password"]
                recipients = info["recipients"]

            smtp.login(email, password)

            msg = "From: " + email + "\nSubject: The link " + url + " needs to be updated\nThe link " + url + " is no longer a valid link and needs to be updated. The column is " + item + " and the state is " + state + "."

            smtp.sendmail(email, recipients, msg)

            return False

    return True


def check_all_urls_from_spreadsheet():

    r = requests.get(spreadsheet_link)
    text = StringIO(r.text)
    reader = csv.reader(text)

    rows = [row for row in reader][1:]

    headers = rows[0]
    side_headers = [row[1] for row in rows]

    with SMTP("firststep.id") as smtp:
        for state_index, state in enumerate(headers):
            for item_index, item in enumerate(side_headers):

                url = rows[state_index][item_index]

                if url != "" and not check_url(url):
                    with open("config.json", "r") as f:
                        info = json.load(f)
                        email = info["email"]
                        password = info["password"]
                        recipients = info["recipients"]

                    smtp.login(email, password)

                    msg = "From: " + email + "\nSubject: The link " + url + " needs to be updated\nThe link " + url + " is no longer a valid link and needs to be updated. The column is " + item + " and the state is " + state + "."

                    smtp.sendmail(email, recipients, msg)


if __name__ == "__main__":
    app.run("0.0.0.0")
