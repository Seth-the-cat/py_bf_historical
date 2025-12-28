import requests
from requests import RequestException
from typing import Any, Dict, Optional
from datetime import datetime
from utils.html import gen_html_from_players

import utils.sql as sql

def get_json(url: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Dict[str, Any]:
    """Send a GET request to the given URL and parse the response as JSON."""
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except RequestException as exc:
        raise exc
    except ValueError:
        raise ValueError(f"Response from {url} was not valid JSON.")

def fetchCloudStats():
    data = get_json("https://blockfrontapi.vuis.dev/api/v1/cloud_data")
    print("\nFetch Process: Fetched cloud stats")
    print("\nFetch Process: Storing stats in database...")
    data_tuple = (
        data.get("players_online"),
        data.get("game_player_count").get("dom"),
        data.get("game_player_count").get("tdm"),
        data.get("game_player_count").get("inf"),
        data.get("game_player_count").get("gg"),
        data.get("game_player_count").get("ttt"),
        data.get("game_player_count").get("boot"),
    )
    sql.add_cloud_stats(data_tuple)

def fetchMatchStats(name: str):
    def addMuted(json):
        print(json)
        if json == {}:
            return ''
        else:
            return ' 🔇'
     
    try:
        data = get_json(f"https://blockfrontapi.vuis.dev/api/v1/player_status?name={name}")
    except:
        return f"<h3> <span style='color: red;'>Something went wrong... Check if <i>{name}</i> is a real player! </span></h3>", "⚠️ Failed to fetch match stats"

    if not data.get("online"):
        print("Player is offline.")
        return f"{name} is offline.", "Player is offline."
    match = data.get("match")
    if not match:
        print("No match data found for player.")
        return "Name not found or player is not in a match.", "No match data found for player."
    uuids = [p["uuid"] for p in match.get("players", [])]
    print("\nFetch Process: Fetched player UUIDs")
    uuids_str = ",".join(uuids)
    print(uuids_str)

    resp = requests.post("https://blockfrontapi.vuis.dev/api/v1/player_data/bulk", data=uuids_str).json()
    players_in_match = [
        {
            "username": p.get("username") + " <img src='https://mc-heads.net/avatar/" +p.get("username") + "' width='20' height='20'>" + addMuted(p.get("punishments")['active']),
            "kills": p.get("kills", 0),
            "deaths": p.get("deaths", 0),
            "Rank": p.get("rank"),
            "Prestige": p.get("prestige", 0),
        }
        for p in resp
    ]

    return gen_html_from_players(players_in_match), f"{len(players_in_match)} out of {match.get('max_players')} players in match."

def fetchPlayersStats():
    print("test")
    uuids = ", ".join([tup[0] for tup in sql.get_players_uuids()])
    resp = requests.post("https://blockfrontapi.vuis.dev/api/v1/player_data/bulk", data=uuids).json()
    output = {}
    DIRECT_FEILD = ['kills', 'deaths', 'assists', 'infected_kills', 'vehicle_kills','bot_kills', 'infected_rounds_won', 'infected_matches_won','highest_kill_streak', 'highest_death_streak', 'exp', 'prestige', 'total_games', 'time_played']
    MAPPING = {'back_stabs': 'backstabs', 'head_shots': 'headshots', 'trophies': 'match_wins'}
    CLASS_ID_MAP = {0: 'rifle_xp', 1: 'lt_rifle_xp', 2: 'assault_xp', 3: 'support_xp', 4: 'medic_xp', 5: 'sinper_xp', 6: 'gunner_xp', 7: 'anti_tank_xp', 9: 'commander_xp'}
    for player_data in resp:
        for field in DIRECT_FEILD:
            if field in player_data:
                output[field] = player_data[field]
        for key, mapped_key in MAPPING.items():
            if key in player_data:
                print(key, player_data[key])
                output[mapped_key] = player_data[key]
        for class_xp in player_data.get('class_xp', []):
            class_id = class_xp.get('class_id')
            if class_id in CLASS_ID_MAP:
                output[CLASS_ID_MAP[class_id]] = class_xp.get('xp')
        sql.add_player_stats(sql.get_player_stats(player_data['uuid']), player_data)
        

    print(output)

def fetchStats():
    fetchCloudStats()

# fetchPlayersStats()