from flask import Flask
import csv
import requests
from io import StringIO
import hashlib

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
    print(headers)
    side_headers = [row[1] for row in rows]

    state_index = side_headers.index(state)
    item_index = headers.index(item)

    return rows[state_index][item_index]


@app.route("/get_embassy/<country>")
def get_url_embassy(country):
    return "https://embassy.goabroad.com/embassies-of/" + country

# item is the column, state is abbreviation
# @app.route('/check_url/<item>/<state>')
# def check_url_from_spreadsheet(item, state):
#     url = get_url_from_spreadsheet(item, state)
#     if not check_url(url):

if __name__ == "__main__":
    app.run("0.0.0.0")
