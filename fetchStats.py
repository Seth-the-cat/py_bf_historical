
import logging
import requests
from utils.html import gen_html_from_players

import utils.sql as sql
import utils.network as network
logger = logging.getLogger(__name__)


def fetchCloudStats():
    data = network.get_request("/api/v1/cloud_data")
    logger.info("\nFetch Process: Fetched cloud stats")
    logger.info("\nFetch Process: Storing stats in database...")
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
        logger.debug(json)
        if json == {}:
            return ''
        else:
            return ' 🔇'
     
    try:
        data = network.get_request(f"https://blockfrontapi.vuis.dev/api/v1/player_status?name={name}")
    except:
        return f"<h3> <span style='color: red;'>Something went wrong... Check if <i>{name}</i> is a real player! </span></h3>", "⚠️ Failed to fetch match stats"

    if not data.get("online"):
        logger.info("Player is offline.")
        return f"{name} is offline.", "Player is offline."
    match = data.get("match")
    if not match:
        logger.info("No match data found for player.")
        return "Name not found or player is not in a match.", "No match data found for player."
    uuids = [p["uuid"] for p in match.get("players", [])]
    logger.info("\nFetch Process: Fetched player UUIDs")
    uuids_str = ",".join(uuids)
    logger.debug(uuids_str)

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
    sql_result = sql.get_players_uuids()
    if not sql_result:
        logger.info("No players Found in database skipping")
        return
    uuids = [tup[0] for tup in sql_result]
    uuid_string = ",".join(uuids)
    logger.info(f"Making request to api for '{uuid_string}'")
    try:
        response = network.post_request("/api/v1/player_data/bulk",data=uuid_string,is_json=False)
    except Exception as e:
        logger.error(f"ERROR making API request: {e}")
        return

    api_data = response
    logger.debug(str(api_data)+"\n-------------")
    DIRECT_FEILD = [
    'kills', 'deaths', 'assists', 'infected_kills', 'vehicle_kills', 'bot_kills', 'infected_rounds_won', 'infected_matches_won', 'highest_kill_streak', 'highest_death_streak', 'exp', 'prestige', 'total_games', 'time_played', 'no_scopes', 'first_bloods', 'fire_kills', 'match_karma']
    MAPPING = {'back_stabs': 'backstabs', 'head_shots': 'headshots', 'trophies': 'match_wins'}
    CLASS_ID_MAP = {0: 'rifle_xp', 1: 'lt_rifle_xp', 2: 'assault_xp', 3: 'support_xp', 4: 'medic_xp', 5: 'sniper_xp', 6: 'gunner_xp', 7: 'anti_tank_xp', 9: 'commander_xp'}
    for player_data in api_data:
        logger.debug(f"({player_data, type(player_data)}\n\n-------------")
        output = {}
        for field in DIRECT_FEILD:
            if field in player_data:
                output[field] = player_data[field]
        for key, mapped_key in MAPPING.items():
            if key in player_data:
                output[mapped_key] = player_data[key]
        for entry in player_data.get('class_exp', []):
                c_id = entry.get('id')
                if c_id in CLASS_ID_MAP:
                    output[CLASS_ID_MAP[c_id]] = entry.get('exp', 0)
        # find player's DB id by UUID, skip if not present
        player_db_id = sql.get_player_id_by_name(player_data['username'])
        if not player_db_id:
            logger.info(f"Skipping player {player_data.get('username')} ({player_data.get('uuid')}): not found in DB")
            continue
        sql.add_player_stats(player_db_id, output)


def fetchStats():
    fetchCloudStats()
    fetchPlayersStats()