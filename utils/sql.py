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
            cur.execute("CREATE TABLE cloud_stats (id integer PRIMARY KEY, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, players_online integer, players_in_dom integer, players_in_tdm integer, players_in_inf integer, players_in_gg integer, players_in_ttt integer, players_in_boot integer)")
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
                                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                                    assult_xp INTEGER ,
                                    support_xp INTEGER ,
                                    medic_xp INTEGER ,
                                    sinper_xp INTEGER ,
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
    #TODO please test
    connection = create_connection()
    try:
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    except:
        if connection:
            connection.rollback()
            raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def add_cloud_stats(stats):
    """ Create a new stats entry into the stats table """
    with get_cursor() as cur: #
        sql = ''' INSERT INTO cloud_stats(date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot)
                VALUES(?,?,?,?,?,?,?,?) '''
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
    with get_cursor() as cur:
        sql = ''' INSERT INTO player_stats(player_id, kills, assists, deaths, hskr, headshots, backstabs, no_scopes, first_bloods, fire_kills, bot_kills, infected_kills, infected_rounds_won, infected_matches_won, vehicle_kills, highest_kill_streak, highest_death_streak, exp, prestige, rifle_xp, lt_rifle_xp, assult_xp, support_xp, medic_xp, sinper_xp, gunner_xp, anti_tank_xp, commander_xp, match_karma, total_games, match_wins, time_played)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur.execute(sql, (player_id, stats['kills'], stats['assists'], stats['deaths'], stats['hskr'], stats['headshots'], stats['backstabs'], stats['no_scopes'], stats['first_bloods'], stats['fire_kills'], stats['bot_kills'], stats['infected_kills'], stats['infected_rounds_won'], stats['infected_matches_won'], stats['vehicle_kills'], stats['highest_kill_streak'], stats['highest_death_streak'], stats['exp'], stats['prestige'], stats['rifle_xp'], stats['lt_rifle_xp'], stats['assult_xp'], stats['support_xp'], stats['medic_xp'], stats['sinper_xp'], stats['gunner_xp'], stats['anti_tank_xp'], stats['commander_xp'], stats['match_karma'], stats['total_games'], stats['match_wins'], stats['time_played']))

def get_players_uuids():
    """ Query all rows in the players table """
    with get_cursor() as cur:
        cur.execute("SELECT uuid FROM players")
        rows = cur.fetchall()
        return rows

def get_player_stats(uuid):
    """ Query all rows in the stats table """
    with get_cursor() as cur:
        cur.execute("SELECT * FROM player_stats WHERE player_id=?", (uuid,))
        rows = cur.fetchall()
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