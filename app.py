from flask import Flask, render_template, session

import csv
import urllib.request
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "covid-19"


def date2js(date):
    return '/'.join(reversed(date.split('/')))


class Datum:
    def __init__(self, date, cases, deaths):
        self.date = date2js(date)
        self.cases = int(cases)
        self.deaths = int(deaths)

    def serialize(self):
        return {'date': self.date, 'cases': self.cases, 'deaths': self.deaths}


class Territory:

    with open('static/countries_coords.csv', 'r') as f:
        coords = {v[0]: {'lat': v[1], 'lon': v[2]} for v in list(csv.reader(f))[1:]}

    def __init__(self, name, code):
        self.name = name
        self.code = code

        c = self.coords[code]

        self.lon = c['lon']
        self.lat = c['lat']

        self.data = []

    def serialize(self):
        return {'name': self.name,
                'longitude': self.lon,
                'latitude': self.lat,
                'data': [d.serialize() for d in self.data]}


def get_data():
    with open('static/world_cases.csv', 'r') as f:
        reader = csv.reader(f)

        territories = {}

        for row in list(reader)[1:]:
            name = row[6]
            code = row[7]

            if code not in territories.keys():
                try:
                    territories[code] = Territory(name, code)
                    territories[code].data.append(Datum(row[0], row[4], row[5]))
                except KeyError:
                    pass
            else:
                territories[code].data.append(Datum(row[0], row[4], row[5]))

    return [t.serialize() for t in territories.values()]


@app.route('/')
def hello_world():
    now = datetime.now()

    if 'update' not in session or session['update'] + timedelta(hours=24) <= now:
        print('Trying to update data...')
        try:
            url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
            urllib.request.urlretrieve(url, 'static/world_cases.csv')
            print('Success')
            session['update'] = now
        except Exception as e:
            print(e)
    data = get_data()
    return render_template("index.html", h1="Hello World", data=data)


if __name__ == '__main__':
    app.run()
