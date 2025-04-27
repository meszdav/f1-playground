import fastf1.events
from datetime import datetime
import pandas as pd
from urllib.parse import urljoin
import requests


DATE = datetime.now().date()
BASE_URL = "http://api.jolpi.ca"


def get_most_recent_gp():
    df = fastf1.events.get_event_schedule(DATE.year)
    most_recent_race = df[df["EventDate"] <= pd.to_datetime(DATE)].sort_values("EventDate", ascending=False).iloc[0]

    return most_recent_race["Country"]

def event_to_round(year):
    r = requests.get(urljoin(BASE_URL, f"/ergast/f1/{year}/races.json"))

    race_to_round = {} 
    data = r.json()
    races = data['MRData']['RaceTable']['Races']

    for race in races:
        race_to_round[race['raceName']] = race['round']
    return race_to_round


def get_results(year, event):
    event_round = event_to_round(year)[event]

    url = urljoin(BASE_URL, f"/results/{year}/{event_round}.json")

    r = requests.get(url)
    data = r.json()

    results = data['MRData']['RaceTable']['Races'][0]['Results']

    result_dict = {}
    for result in results:
        result_dict[result["position"]] = result['Driver']['code']

    return result_dict

def list_drivers():
    ...

def get_most_recent_session():
    ...
    