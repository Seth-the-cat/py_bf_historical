import contextlib
from pathlib import Path
import sqlite3
import requests
import os


DATA_DIR = Path("./data")
# Ensure the 'data' directory exists before we try to connect
os.makedirs(DATA_DIR,exist_ok=True)
   

DB_FILE = os.path.join(DATA_DIR, 'stats.db')


def create_connection(db_file=DB_FILE):
    """ create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database at {db_file}: {e}")
        return None

    # check if table exists, if not create it
    try:
        cur = conn.cursor()
        if cur.execute("PRAGMA foreign_keys;") == 0:
            cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cloud_stats';")
        if cur.fetchone() is None:
            print("Table 'cloud_stats' not found. Creating it...")
            cur.execute("CREATE TABLE cloud_stats (id integer PRIMARY KEY, date DATETIME DEFAULT CURRENT_TIMESTAMP, players_online integer, players_in_dom integer, players_in_tdm integer, players_in_inf integer, players_in_gg integer, players_in_ttt integer, players_in_boot integer)")
            conn.commit()
        if cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players';").fetchone() is None:
            print("Table 'players' not found. Creating it...")
            cur.execute("CREATE TABLE players (id integer PRIMARY KEY, uuid text UNIQUE, name text UNIQUE)")
            conn.commit()
        if cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player_stats';").fetchone() is None:
            print("Table 'player_stats' not found. Creating it...")
            create_table_sql = """
                                CREATE TABLE IF NOT EXISTS player_stats (
                                    stat_id INTEGER PRIMARY KEY,
                                    player_id INTEGER,
                                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    kills INTEGER ,
                                    assists INTEGER ,
                                    deaths INTEGER ,
                                    kdr REAL GENERATED ALWAYS AS (CAST(kills AS REAL) / NULLIF(deaths, 0)) VIRTUAL,
                                    headshots INTEGER ,
                                    hskr REAL GENERATED ALWAYS AS (CAST(headshots AS REAL) / NULLIF(kills, 0)) VIRTUAL,
                                    backstabs INTEGER ,
                                    no_scopes INTEGER ,
                                    first_bloods INTEGER ,
                                    fire_kills INTEGER ,
                                    bot_kills INTEGER ,
                                    infected_kills INTEGER ,
                                    infected_rounds_won INTEGER ,
                                    infected_matches_won INTEGER ,
                                    vehicle_kills INTEGER ,
                                    highest_kill_streak INTEGER ,
                                    highest_death_streak INTEGER ,
                                    exp INTEGER ,
                                    prestige INTEGER ,
                                    rifle_xp INTEGER ,
                                    lt_rifle_xp INTEGER ,
                                    assault_xp INTEGER ,
                                    support_xp INTEGER ,
                                    medic_xp INTEGER ,
                                    sniper_xp INTEGER ,
                                    gunner_xp INTEGER ,
                                    anti_tank_xp INTEGER ,
                                    commander_xp INTEGER , 
                                    match_karma INTEGER ,
                                    total_games INTEGER ,
                                    match_wins INTEGER ,
                                    time_played INTEGER , 
                                    FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE
                                );
                                """
            cur.execute(create_table_sql)
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

    return conn

@contextlib.contextmanager
def get_cursor():
    connection = create_connection()
    try:
        connection.row_factory = sqlite3.Row 
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()

def add_cloud_stats(stats):
    """ Create a new stats entry into the stats table """
    with get_cursor() as cur: #
        sql = ''' INSERT INTO cloud_stats(players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot)
                VALUES(?,?,?,?,?,?,?) '''
        cur.execute(sql, stats)
        last_id = cur.lastrowid
        return last_id

def add_player(username):
    """ Create a new player entry into the players table """
    result = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}").json()
    if not result.get("id",None):
        raise ValueError(f"Invalid username: '{username}'")
    uuid = result["id"]
    with get_cursor() as cur:
        sql = ''' INSERT INTO players(uuid, name)
                VALUES(?, ?) '''
        cur.execute(sql, (uuid, username))
        last_id = cur.lastrowid
        return last_id

def add_player_stats(player_id, stats):
    """ Create a new stats entry into the stats table """
    if not player_id:
        raise ValueError(f"Invalid player_id: {player_id}")

    # Use safe lookups with defaults to avoid KeyError if fields are missing
    kills = stats.get('kills', 0)
    assists = stats.get('assists', 0)
    deaths = stats.get('deaths', 0)
    headshots = stats.get('headshots', 0)
    backstabs = stats.get('backstabs', 0)
    no_scopes = stats.get('no_scopes', 0)
    first_bloods = stats.get('first_bloods', 0)
    fire_kills = stats.get('fire_kills', 0)
    bot_kills = stats.get('bot_kills', 0)
    infected_kills = stats.get('infected_kills', 0)
    infected_rounds_won = stats.get('infected_rounds_won', 0)
    infected_matches_won = stats.get('infected_matches_won', 0)
    vehicle_kills = stats.get('vehicle_kills', 0)
    highest_kill_streak = stats.get('highest_kill_streak', 0)
    highest_death_streak = stats.get('highest_death_streak', 0)
    exp = stats.get('exp', 0)
    prestige = stats.get('prestige', 0)
    rifle_xp = stats.get('rifle_xp', 0)
    lt_rifle_xp = stats.get('lt_rifle_xp', 0)
    assault_xp = stats.get('assault_xp', 0)
    support_xp = stats.get('support_xp', 0)
    medic_xp = stats.get('medic_xp', 0)
    sniper_xp = stats.get('sniper_xp', 0)
    gunner_xp = stats.get('gunner_xp', 0)
    anti_tank_xp = stats.get('anti_tank_xp', 0)
    commander_xp = stats.get('commander_xp', 0)
    match_karma = stats.get('match_karma', 0)
    total_games = stats.get('total_games', 0)
    match_wins = stats.get('match_wins', 0)
    time_played = stats.get('time_played', 0)
    
    stat_values = (
        kills, assists, deaths, headshots, backstabs, no_scopes, 
        first_bloods, fire_kills, bot_kills, infected_kills, 
        infected_rounds_won, infected_matches_won, vehicle_kills, 
        highest_kill_streak, highest_death_streak, exp, prestige, 
        rifle_xp, lt_rifle_xp, assault_xp, support_xp, medic_xp, 
        sniper_xp, gunner_xp, anti_tank_xp, commander_xp, 
        match_karma, total_games, match_wins, time_played
    )

    with get_cursor() as cur:
        # 1. Fetch the last two entries for this player
        # We explicitly list the columns to avoid pulling 'date', 'kdr', and 'hskr' into the comparison
        cur.execute('''
            SELECT stat_id, kills, assists, deaths, headshots, backstabs, no_scopes, 
                   first_bloods, fire_kills, bot_kills, infected_kills, 
                   infected_rounds_won, infected_matches_won, vehicle_kills, 
                   highest_kill_streak, highest_death_streak, exp, prestige, 
                   rifle_xp, lt_rifle_xp, assault_xp, support_xp, medic_xp, 
                   sniper_xp, gunner_xp, anti_tank_xp, commander_xp, 
                   match_karma, total_games, match_wins, time_played
            FROM player_stats
            WHERE player_id = ?
            ORDER BY stat_id DESC LIMIT 2
        ''', (player_id,))
        
        last_two = cur.fetchall()

        # 2. Check if the incoming stats match BOTH of the last two records
        if len(last_two) == 2:
            # We convert the Row objects to tuples and slice off [1:] to drop the 'stat_id' 
            # so we are purely comparing the gameplay stats.
            last_row_stats = tuple(last_two[0])[1:] 
            prev_row_stats = tuple(last_two[1])[1:]

            if stat_values == last_row_stats and stat_values == prev_row_stats:
                # Duplicate streak confirmed! Delete the last row (which is the middle of the streak)
                # The incoming INSERT below will replace it, dragging the timestamp forward.
                cur.execute('DELETE FROM player_stats WHERE stat_id = ?', (last_two[0]['stat_id'],))

        # 3. Insert the new record
        sql = ''' INSERT INTO player_stats(
                    player_id, kills, assists, deaths, headshots, backstabs, no_scopes, 
                    first_bloods, fire_kills, bot_kills, infected_kills, infected_rounds_won, 
                    infected_matches_won, vehicle_kills, highest_kill_streak, highest_death_streak, 
                    exp, prestige, rifle_xp, lt_rifle_xp, assault_xp, support_xp, medic_xp, 
                    sniper_xp, gunner_xp, anti_tank_xp, commander_xp, match_karma, total_games, 
                    match_wins, time_played
                  ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        
        # Add the player_id to the front of our stat tuple and execute
        cur.execute(sql, (player_id,) + stat_values)
        
        return cur.lastrowid
    

def get_players_uuids():
    """ Query all rows in the players table """
    with get_cursor() as cur:
        cur.execute("SELECT uuid FROM players")
        rows = cur.fetchall()
        return rows
    
def get_players_names():
    """ Query all rows in the players table """
    with get_cursor() as cur:
        cur.execute("SELECT name FROM players")
        rows = cur.fetchall()
        return rows

def get_player_id_by_uuid(uuid):
    """Return the `id` of a player given their UUID, or None if not found."""
    with get_cursor() as cur:
        cur.execute("SELECT id FROM players WHERE uuid = ?", (uuid,))
        row = cur.fetchone()
        return row[0] if row else None
    
def get_player_id_by_name(name):
    """Return the `id` of a player given their name, or None if not found."""
    with get_cursor() as cur:
        cur.execute("SELECT id FROM players WHERE name COLLATE NOCASE = ?", (name,))
        row = cur.fetchone()
        return row[0] if row else None

def get_player_stats(player_id):
    """ Query all rows in the stats table """
    with get_cursor() as cur:
        cur.execute("SELECT * FROM player_stats WHERE player_id=?", (player_id,))
        rows = cur.fetchall()
        print(rows)
        return rows

def check_player(name):
    """ Query all rows in the players table """
    with get_cursor() as cur:
        cur.execute("SELECT * FROM players WHERE name COLLATE NOCASE = ?", (name,))
        rows = cur.fetchall()
        if len(rows) > 0:
            return True
        else:
            return False

def get_all_stats():
    """ Query all rows in the stats table """
    with get_cursor() as cur:
        cur.execute("SELECT * FROM cloud_stats")
        rows = cur.fetchall()
        return rows

def get_latest_stats():
    """ Query the latest row in the stats table """
    with get_cursor() as cur:
        cur.execute("SELECT * FROM cloud_stats ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        return row

def two_cols_of_stats():
    """ Query date and players_online columns from stats table """
    with get_cursor() as cur:
        cur.execute("SELECT date, players_online FROM cloud_stats")
        rows = cur.fetchall()
        formatted_entries = []
        for date_str, players in rows:
            formatted_entries.append(f'  {{Date: new Date("{date_str}"), Players: {players}}}')

        output = "[\n" + ",\n".join(formatted_entries) + "\n]" 
        return output

def graph_data():   
    """ Query date and players_online columns from cloud_stats table """
    with get_cursor() as cur:
        cur.execute("SELECT date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot FROM cloud_stats")
        rows = cur.fetchall()
        
    formatted_entries = []
    for date_str, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot in rows:
        formatted_entries.append(f'  {{Date: new Date("{date_str}"), Players: {players_online}, Dom: {players_in_dom}, TDM: {players_in_tdm}, Inf: {players_in_inf}, GG: {players_in_gg}, TTT: {players_in_ttt}, Boot: {players_in_boot}}}')

    output = "[\n" + ",\n".join(formatted_entries) + "\n]" 
    return output

def clear_cloud_stats():
    """ Delete all rows in the stats table """
    with get_cursor() as cur:
        cur = conn.cursor()
        cur.execute("DELETE FROM cloud_stats")

# Runable functions for testing/debugging
if __name__ == '__main__':
    print(f"Database Path: {DB_FILE}")
    print("Runable functions:\n1. Create Connection\n2. add_stats(stats_tuple)\n3. get_all_stats()\n4. get_latest_stats()\n5. two_cols_of_stats()\n6. clear_stats()")
    choice = input("Enter the number of the function you want to run: ")
    
    if choice == "1":
        conn = create_connection()
        if conn:
            print("Connection to database established.")
            conn.close()
        else:
            print("Failed to establish connection.")
            
    elif choice == "2":
        print("Enter stats as comma-separated values (date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot):")
        stats_input = input()
        # Basic error handling for manual input
        try:
            stats_tuple = tuple(stats_input.split(","))
            add_cloud_stats(stats_tuple)
            print("Stats added.")
        except Exception as e:
            print(f"Error adding stats: {e}")
            
    elif choice == "3":
        print("All stats:")
        for row in get_all_stats():
            print(row)
            
    elif choice == "4":
        print("Latest stats:")
        print(get_latest_stats())
        
    elif choice == "5":
        print("Two columns of stats:")
        print(two_cols_of_stats())
        
    elif choice == "6": 
        clear_cloud_stats()
        print("All stats cleared.")
        
    else:
        print("Invalid choice.")