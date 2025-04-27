import fastf1.events
from datetime import datetime
import pandas as pd
from urllib.parse import urljoin
import requests
from langchain_core.tools import tool


DATE = datetime.now().date()
BASE_URL = "http://api.jolpi.ca"


def get_most_recent_gp():
    df = fastf1.events.get_event_schedule(DATE.year)
    most_recent_race = (
        df[df["EventDate"] <= pd.to_datetime(DATE)]
        .sort_values("EventDate", ascending=False)
        .iloc[0]
    )

    return most_recent_race["EventName"]


def event_to_round(year):
    r = requests.get(urljoin(BASE_URL, f"/ergast/f1/{year}/races.json"))

    race_to_round = {}
    data = r.json()
    races = data["MRData"]["RaceTable"]["Races"]
    for race in races:
        race_to_round[race["raceName"]] = race["round"]

    return race_to_round


@tool
def get_gp_results(year, event) -> dict:
    """
    Fetches the race results for a specific year and event.

    Args:
        year (int): The year of the race season.
        event (str): The name of the event (e.g., "Monaco Grand Prix").

    Returns:
        dict: A dictionary where the keys are the finishing positions (as strings)
              and the values are the driver codes (as strings).
    """
    event_round = event_to_round(year)[event]

    url = urljoin(BASE_URL, f"/ergast/f1/{year}/{event_round}/results")

    r = requests.get(url)
    data = r.json()

    results = data["MRData"]["RaceTable"]["Races"][0]["Results"]

    result_dict = {}
    for result in results:
        result_dict[result["position"]] = result["Driver"]["code"]

    return result_dict


@tool
def get_nth_driver(n: int, year: int, event: str) -> str:
    """
    Fetches the racer by their finishing position.
    Args:
        n (int): The finishing position of the driver.
        year (int): The year of the event
        event (str): The name of the event (e.g., "Monaco Grand Prix").
    Returns:
        str: The driver code of the racer who finished in position n.
    """
    result = get_gp_results.func(year, event)

    return result[str(n)]


def list_drivers(): ...


def get_most_recent_session(): ...
