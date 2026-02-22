import os
import requests
from requests import RequestException
from typing import Any, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from utils.html import gen_html_from_players

load_dotenv()

import utils.sql as sql

# Base API URL read from environment or .env file. Defaults to the previous hardcoded value.
API_BASE_URL = os.getenv("API_BASE_URL", "https://blockfrontapi.vuis.dev")

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
    data = get_json(f"{API_BASE_URL}/api/v1/cloud_data")
    print("\nFetch Process: Fetched cloud stats")
    print("\nFetch Process: Storing stats in database...")
    # guard against unexpected types from the API (e.g., string instead of dict)
    game_player_count = data.get("game_player_count") if isinstance(data.get("game_player_count"), dict) else {}
    data_tuple = (
        data.get("players_online"),
        game_player_count.get("dom"),
        game_player_count.get("tdm"),
        game_player_count.get("inf"),
        game_player_count.get("gg"),
        game_player_count.get("ttt"),
        game_player_count.get("boot"),
    )
    sql.add_cloud_stats(data_tuple)

def fetchMatchStats(name: str):
    def addMuted(j):
        # tolerate non-dict values (some API responses may be unexpected types)
        print(j)
        if not isinstance(j, dict) or j == {}:
            return ''
        return ' 🔇'
     
    try:
        data = get_json(f"{API_BASE_URL}/api/v1/player_status?name={name}")
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

    resp = requests.post(f"{API_BASE_URL}/api/v1/player_data/bulk", data=uuids_str).json()
    players_in_match = []
    for p in resp:
        punishments = p.get("punishments") if isinstance(p.get("punishments"), dict) else {}
        active = punishments.get('active', {}) if isinstance(punishments, dict) else {}
        username_html = (
            (p.get("username") or "")
            + " <img src='https://mc-heads.net/avatar/" + (p.get("username") or "") + "' width='20' height='20'>"
            + addMuted(active)
        )
        players_in_match.append({
            "username": username_html,
            "kills": p.get("kills", 0),
            "deaths": p.get("deaths", 0),
            "Rank": p.get("rank"),
            "Prestige": p.get("prestige", 0),
        })

    return gen_html_from_players(players_in_match), f"{len(players_in_match)} out of {match.get('max_players')} players in match."

def fetchPlayersStats():
    uuids_list = [tup[0] for tup in sql.get_players_uuids()]
    if not uuids_list:
        return

    uuids_str = ",".join(uuids_list)
    
    # Ensure we get a valid JSON response
    response = requests.post(f"{API_BASE_URL}/api/v1/player_data/bulk", data=uuids_str)
    try:
        resp = response.json()
    except ValueError:
        print("API did not return valid JSON")
        return

    # If the API returns a single dict instead of a list, wrap it in a list
    if isinstance(resp, dict):
        resp = [resp]
    
    # If resp is a string here, it means the API returned something like '"Internal Server Error"'
    if not isinstance(resp, list):
        print(f"Expected list of players, but got {type(resp)}")
        return

    DIRECT_FEILD = ['kills', 'deaths', 'assists', 'infected_kills', 'vehicle_kills', 'bot_kills', 'infected_rounds_won', 'infected_matches_won', 'highest_kill_streak', 'highest_death_streak', 'exp', 'prestige', 'total_games', 'time_played', 'no_scopes', 'first_bloods', 'fire_kills', 'match_karma']
    MAPPING = {'back_stabs': 'backstabs', 'head_shots': 'headshots', 'trophies': 'match_wins'}
    CLASS_ID_MAP = {0: 'rifle_xp', 1: 'lt_rifle_xp', 2: 'assault_xp', 3: 'support_xp', 4: 'medic_xp', 5: 'sniper_xp', 6: 'gunner_xp', 7: 'anti_tank_xp', 9: 'commander_xp'}

    for player_data in resp:
        # SAFETY CHECK: If player_data is a string, skip it to avoid the AttributeError
        if not isinstance(player_data, dict):
            print(f"Skipping invalid player entry: {player_data}")
            continue

        output = {}
        for field in DIRECT_FEILD:
            if field in player_data:
                output[field] = player_data[field]
        
        for key, mapped_key in MAPPING.items():
            if key in player_data:
                output[mapped_key] = player_data[key]
        
        # Now this is safe from 'str' object errors
        class_exp = player_data.get('class_exp', [])
        if isinstance(class_exp, list):
            for entry in class_exp:
                if isinstance(entry, dict):
                    c_id = entry.get('id')
                    if c_id in CLASS_ID_MAP:
                        output[CLASS_ID_MAP[c_id]] = entry.get('exp', 0)

        player_uuid = player_data.get('uuid')
        player_name = player_data.get('username')
        if player_uuid and player_name:
            sql.update_player_name(player_uuid, player_name)
        player_db_id = sql.get_player_id_by_name(player_name)
        if player_db_id:
            sql.add_player_stats(player_db_id, output)

def fetchStats():
    fetchCloudStats()
    fetchPlayersStats()