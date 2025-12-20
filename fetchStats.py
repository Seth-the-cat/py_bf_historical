import requests
from requests import RequestException
from typing import Any, Dict, Optional
from datetime import datetime

import sqlUtils

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
        datetime.now().isoformat(),
        data.get("players_online"),
        data.get("game_player_count").get("dom"),
        data.get("game_player_count").get("tdm"),
        data.get("game_player_count").get("inf"),
        data.get("game_player_count").get("gg"),
        data.get("game_player_count").get("ttt"),
        data.get("game_player_count").get("boot"),
    )
    sqlUtils.add_stats(data_tuple)

if __name__ == "__main__":
    fetchCloudStats()

def fetchStats():
    fetchCloudStats()