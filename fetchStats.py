import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Import the new network utilities
from utils.network import get_request, post_request
from utils.html import gen_html_from_players
import utils.sql as sql

load_dotenv()

def fetchCloudStats():
    # Use the new get_request wrapper
    data = get_request("/api/v1/cloud_data")
    if not data:
        return

    print("\nFetch Process: Fetched cloud stats")
    print("\nFetch Process: Storing stats in database...")
    
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
        if not isinstance(j, dict) or j == {}:
            return ''
        return ' 🔇'
    
    try:
        # Pass params as a dictionary to the wrapper
        data = get_request("/api/v1/player_status", params={"name": name})
        if not data:
            raise Exception("No data received")
    except Exception:
        return f"<h3> <span style='color: red;'>Something went wrong... Check if <i>{name}</i> is a real player! </span></h3>", "⚠️ Failed to fetch match stats"

    if not data.get("online"):
        return f"{name} is offline.", "Player is offline."
    
    match = data.get("match")
    if not match:
        return "Name not found or player is not in a match.", "No match data found for player."
    
    uuids = [p["uuid"] for p in match.get("players", [])]
    uuids_str = ",".join(uuids)

    # Use post_request (is_json=False because we are sending a raw comma-separated string)
    resp = post_request("/api/v1/player_data/bulk", data=uuids_str, is_json=False)
    
    players_in_match = []
    for p in resp:
        punishments = p.get("punishments") if isinstance(p.get("punishments"), dict) else {}
        active = punishments.get('active', {}) if isinstance(punishments, dict) else {}
        username = p.get("username") or ""
        
        username_html = (
            f"{username} <img src='https://mc-heads.net/avatar/{username}' width='20' height='20'>"
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

    formatted_uuids = []
    for u in uuids_list:
        clean_u = u.strip()
        if len(clean_u) == 32:
            formatted_uuids.append(f"{clean_u[:8]}-{clean_u[8:12]}-{clean_u[12:16]}-{clean_u[16:20]}-{clean_u[20:]}")
        else:
            formatted_uuids.append(clean_u)

    chunk_size = 50
    all_player_data = []
    
    print(f"🕵️  Sending {len(formatted_uuids)} UUIDs to API in batches of {chunk_size}...")

    for i in range(0, len(formatted_uuids), chunk_size):
        chunk = formatted_uuids[i:i + chunk_size]
        uuids_str = ",".join(chunk)
        
        try:
            # Using the new post_request wrapper
            resp = post_request("/api/v1/player_data/bulk", data=uuids_str, is_json=False)
            
            if isinstance(resp, dict):
                resp = [resp]
            if isinstance(resp, list):
                all_player_data.extend(resp)
        except Exception as e:
            print(f"⚠️ Failed to fetch a batch: {e}")
            continue

    print(f"✅ API successfully returned data for {len(all_player_data)} players total!")

    DIRECT_FIELDS = ['kills', 'deaths', 'assists', 'infected_kills', 'vehicle_kills', 'bot_kills', 
                     'infected_rounds_won', 'infected_matches_won', 'highest_kill_streak', 
                     'highest_death_streak', 'exp', 'prestige', 'total_games', 'time_played', 
                     'no_scopes', 'first_bloods', 'fire_kills', 'match_karma']
    MAPPING = {'back_stabs': 'backstabs', 'head_shots': 'headshots', 'trophies': 'match_wins'}
    CLASS_ID_MAP = {0: 'rifle_xp', 1: 'lt_rifle_xp', 2: 'assault_xp', 3: 'support_xp', 
                    4: 'medic_xp', 5: 'sniper_xp', 6: 'gunner_xp', 7: 'anti_tank_xp', 9: 'commander_xp'}

    for player_data in all_player_data:
        if not isinstance(player_data, dict):
            continue

        output = {}
        for field in DIRECT_FIELDS:
            if field in player_data:
                output[field] = player_data[field]
        
        for key, mapped_key in MAPPING.items():
            if key in player_data:
                output[mapped_key] = player_data[key]
        
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

if __name__ == "__main__":
    fetchStats()