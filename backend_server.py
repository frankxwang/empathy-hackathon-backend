from flask import Flask
import csv
import requests
from io import StringIO
import hashlib
from smtplib import SMTP
import json

app = Flask(__name__)

application = app


def get_spreadsheet_link():
    with open("config.json") as f:
        return json.load(f)["spreadsheet_link"]

# item is the column, state is abbreviation
@app.route('/get_url/<item>/<state>')
def get_url_from_spreadsheet(item, state):
    r = requests.get(get_spreadsheet_link())
    text = StringIO(r.text)
    reader = csv.reader(text)

    rows = [row[1:] for row in reader][1:]

    headers = rows[0]
    side_headers = [row[0] for row in rows]

    state_index = side_headers.index(state)
    item_index = headers.index(item)

    return rows[state_index][item_index]


@app.route("/get_embassy/<country>")
def get_url_embassy(country):
    return "https://embassy.goabroad.com/embassies-of/" + country


if __name__ == "__main__":
    app.run("0.0.0.0")
