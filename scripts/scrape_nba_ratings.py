from dataclasses import dataclass
from enum import StrEnum
import json
import random
import re
from time import sleep
from typing import Any, Literal
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


@dataclass
class SeasonData:
    year: str  # 2024-25 will be 2025
    age: int
    team: Team
    league: str | Literal['NBA']
    position: Literal['C', 'PF', 'SF', 'SG', 'PG']
    games_played: int
    games_started: int

    minutes_per_game: float
    field_goals_per_game: float
    field_goal_attempts_per_game: float
    three_point_field_goals_per_game: float
    three_point_field_goal_attempts_per_game: float
    two_point_field_goals_per_game: float
    two_point_field_goal_attempts_per_game: float
    free_throws_per_game: float
    free_throw_attempts_per_game: float

    field_goal_percentage: float
    three_point_percentage: float
    two_point_percentage: float
    effective_field_goal_percentage: float
    free_throw_percentage: float

    offensive_rebounds_per_game: float
    defensive_rebounds_per_game: float
    total_rebounds_per_game: float
    assists_per_game: float
    steals_per_game: float
    blocks_per_game: float
    turnovers_per_game: float
    personal_fouls_per_game: float
    points_per_game: float

    @staticmethod
    def convert_data_stat(data_stat: str) -> str:
        data_stat_to_attr: dict[str, str] = {
            'age': 'age',
            'pos': 'position',
            'team_name_abbr': 'team',
            'comp_name_abbr': 'league',
            'pos': 'position',
            'games': 'games_played',
            'games_started': 'games_started',
            'mp_per_g': 'minutes_per_game',
            'fg_per_g': 'field_goals_per_game',
            'fga_per_g': 'field_goal_attempts_per_game',
            'fg_pct': 'field_goal_percentage',
            'fg3_per_g': 'three_point_field_goals_per_game',
            'fg3a_per_g': 'three_point_field_goal_attempts_per_game',
            'fg3_pct': 'three_point_percentage',
            'fg2_per_g': 'two_point_field_goals_per_game',
            'fg2a_per_g': 'two_point_field_goal_attempts_per_game',
            'fg2_pct': 'two_point_percentage',
            'efg_pct': 'effective_field_goal_percentage',
            'ft_per_g': 'free_throws_per_game',
            'fta_per_g': 'free_throw_attempts_per_game',
            'ft_pct': 'free_throw_percentage',
            'orb_per_g': 'offensive_rebounds_per_game',
            'drb_per_g': 'defensive_rebounds_per_game',
            'trb_per_g': 'total_rebounds_per_game',
            'ast_per_g': 'assists_per_game',
            'stl_per_g': 'steals_per_game',
            'blk_per_g': 'blocks_per_game',
            'tov_per_g': 'turnovers_per_game',
            'pf_per_g': 'personal_fouls_per_game',
            'pts_per_g': 'points_per_game',
        }

        return data_stat_to_attr.get(data_stat, '')


@dataclass
class PlayerData:
    name: str
    team: Team
    height_cm: int  # in centimeters
    weight_kg: int  # in kilograms

    seasons: dict[str, SeasonData]  # year -> SeasonData


def serialize_sets(obj: Any) -> Any:
    """
    Custom JSON encoder to serialize sets as lists.
    :param obj: The object to serialize.
    :return: The serialized object.
    """
    if isinstance(obj, set):
        return list(obj)

    return obj


# def main() -> None:
#     player_links: dict[Team, set[str]] = {}

#     # --- Retrieve the player links for each team ---
#     for team in tqdm(list(Team)[:2], desc="Retrieving player links", unit="team"):
#         player_links[team] = get_roster_player_links(team)
#         sleep(random.uniform(2.0, 5.0))

#     print(json.dumps(player_links, indent=4, default=serialize_sets))
#     # TODO...


def get_roster_player_links(team: Team) -> set[str]:
    """ Gets a list of player links for the given team.
    :param team: The team to get the roster links for.
    :return: A set of player links for the given team.
    """
    team_url: str = f"{BASKETBALL_REFERENCE_URL}/teams/{team}/{SEARCH_YEAR}.html"

    response: Response = get(team_url, headers=HEADERS)

    if (response.status_code != 200):
        raise ValueError(
            f"Failed team retrieval - {team}. {response.status_code}")

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


def get_player_data(player_url: str, team: Team) -> PlayerData:
    """ Gets the player data for the given player URL.
    :param player_url: The URL of the player to get data for.
    :param team: The team the player is on.
    :return: The player data for the given player URL.
    """
    response: Response = get(player_url, headers=HEADERS)

    if (response.status_code != 200):
        raise ValueError(
            f"Failed player retrieval - {player_url}. {response.status_code}")

    soup: BeautifulSoup = BeautifulSoup(response.content, 'html.parser')
    table: BeautifulSoup = soup.find('table', id='per_game_stats')
    raw_season_stats: list[Tag] = table.find_all('tbody')

    # final processed data for season stats
    processed_season_data: dict[str, SeasonData] = {}

    for season in raw_season_stats:

        processed_stats: dict[str, Any] = {}

        for data in season.find_all('td'):
            data_stat: str = data.get('data-stat')
            if data_stat is None:
                continue

            data_stat_value: str = data.get_text()
            attribute: str = SeasonData.convert_data_stat(data_stat)
            if not attribute:
                print(f"Attribute not found for data_stat: {data_stat}")
                continue

            if attribute == 'positions':
                raw_positions: list[str] = data_stat_value.split('and')
                data[attribute] = [pos.strip() for pos in raw_positions]

            if data_stat_value.startswith('.'):
                processed_stats[attribute] = float(data_stat_value[1:]) / 10

            elif data_stat_value.isdigit():
                processed_stats[attribute] = int(data_stat_value)

            elif data_stat_value.isdecimal():
                processed_stats[attribute] = float(data_stat_value)

            else:
                processed_stats[attribute] = data_stat_value

        row_head: Tag = season.find('th')
        if row_head is None:
            raise ValueError("Row head not found.")

        year: str = row_head.get('csk')
        if year is None:
            raise ValueError("Year not found.")

        processed_stats['year'] = year

        raw_season_stats = SeasonData(**processed_stats)
        processed_season_data[year] = raw_season_stats

    player_meta_tag: Tag = soup.find('div', id='meta')

    name_h1: Tag = player_meta_tag.find('h1')
    if name_h1 is None:
        raise ValueError("Name not found.")

    third_p: Tag = player_meta_tag.find_all('p')[2]
    height_weight = re.findall(r'\((.*?)\)', third_p.get_text())[0].split(',')

    height: str = height_weight[0].strip().replace('cm', '')
    weight: str = height_weight[1].strip().replace(
        'kg', '').replace('\xa0', '')

    return PlayerData(
        name=name_h1.get_text(),
        team=team,
        height_cm=int(height),
        weight_kg=int(weight),
        seasons=processed_season_data,
    )
