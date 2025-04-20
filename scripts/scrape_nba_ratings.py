from enum import StrEnum
import json
import random
from time import sleep
from typing import Any
from bs4 import BeautifulSoup, Tag
from requests import Response, get
from dotenv import load_dotenv
from os import environ

from tqdm import tqdm

load_dotenv()

BASKETBALL_REFERENCE_URL: str = "https://www.basketball-reference.com"

# default headers for requests to basketball-reference
HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": environ['BASKETBALL_REFERENCE_COOKIE'],
}

# the year we are searching for, in terms of roster data
SEARCH_YEAR: str = "2025"


class Team(StrEnum):
    BOSTON_CELTICS = "BOS"
    NEW_YORK_NICKS = "NYK"
    TORONTO_RAPTORS = "TOR"
    BROOKLYN_NETS = "BRK"
    PHILADELPHIA_76ERS = "PHI"
    CLEVELAND_CAVALIERS = "CLE"
    INDIANA_PACERS = "IND"
    MILWAUKEE_BUCKS = "MIL"
    DETROIT_PISTONS = "DET"
    CHICAGO_BULLS = "CHI"
    ORLANDO_MAGIC = "ORL"
    ATLANTA_HAWKS = "ATL"
    MIAMI_HEAT = "MIA"
    CHARLOTTE_HORNETS = "CHO"
    WASHINGTON_WIZARDS = "WAS"
    OKLAHOMA_CITY_THUNDER = "OKC"
    LOS_ANGELES_LAKERS = "LAL"
    HOUSTON_ROCKETS = "HOU"
    DENVER_NUGGETS = "DEN"
    LOS_ANGELES_CLIPPERS = "LAC"
    MEMPHIS_GRIZZLIES = "MEM"
    MINNESOTA_TIMBERWOLVES = "MIN"
    GOLDEN_STATE_WARRIORS = "GSW"
    DALLAS_MAVERICKS = "DAL"
    PORTLAND_TRAIL_BLAZERS = "POR"
    SACRAMENTO_KINGS = "SAC"
    SAN_ANTONIO_SPURS = "SAS"
    UTAH_JAZZ = "UTA"
    PHOENIX_SUNS = "PHO"
    NEW_ORLEANS_PELICANS = "NOP"


def serialize_sets(obj: Any) -> Any:
    """
    Custom JSON encoder to serialize sets as lists.
    :param obj: The object to serialize.
    :return: The serialized object.
    """
    if isinstance(obj, set):
        return list(obj)

    return obj


def main() -> None:
    player_links: dict[Team, set[str]] = {}

    # --- Retrieve the player links for each team ---
    for team in tqdm(list(Team)[:2], desc="Retrieving player links", unit="team"):
        player_links[team] = get_roster_player_links(team)
        sleep(random.uniform(2.0, 5.0))

    print(json.dumps(player_links, indent=4, default=serialize_sets))
    # TODO...


def get_roster_player_links(team: Team) -> set[str]:
    """ Gets a list of player links for the given team.
    :param team: The team to get the roster links for.
    :return: A set of player links for the given team.
    """
    team_url: str = f"{BASKETBALL_REFERENCE_URL}/teams/{team}/{SEARCH_YEAR}.html"

    response: Response = get(team_url, headers=HEADERS)

    if (response.status_code != 200):
        raise ValueError(f"Failed retrieval - {team}. {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    # we need to grab the data in the following table with id="roster"
    table: BeautifulSoup = soup.find('table', id='roster')
    if table is None:
        raise ValueError(f"Table with id 'roster' not found for team {team}.")

    link_elements: list[Tag] = table.find_all('a', href=True)

    player_links: set[str] = set()

    for el in link_elements:
        link: str = el.get('href')

        if not link:
            continue

        # we only want links that start with /players/
        if link.startswith('/players/'):
            player_links.add(f'{BASKETBALL_REFERENCE_URL}{link}')

    return player_links


if __name__ == '__main__':
    main()
