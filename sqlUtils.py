import sqlite3
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')

# Ensure the 'data' directory exists before we try to connect
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

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
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cloud_stats';")
        if cur.fetchone() is None:
            print("Table 'cloud_stats' not found. Creating it...")
            cur.execute("CREATE TABLE cloud_stats (id integer PRIMARY KEY, date text, players_online integer, players_in_dom integer, players_in_tdm integer, players_in_inf integer, players_in_gg integer, players_in_ttt integer, players_in_boot integer)")
            conn.commit()
        if cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players';").fetchone() is None:
            print("Table 'players' not found. Creating it...")
            cur.execute("CREATE TABLE players (id integer PRIMARY KEY, uuid text UNIQUE, name text UNIQUE)")
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

    return conn

def add_stats(stats):
    """ Create a new stats entry into the stats table """
    conn = create_connection()
    if conn is None: return
    
    sql = ''' INSERT INTO cloud_stats(date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, stats)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def add_player(username):
    """ Create a new player entry into the players table """
    uuid=requests.get("https://api.mojang.com/users/profiles/minecraft/" + username).json()['id']
    conn = create_connection()
    if conn is None: return
    sql = ''' INSERT INTO players(uuid, name)
              VALUES(?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (uuid, username))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def get_players():
    """ Query all rows in the players table """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    rows = cur.fetchall()
    conn.close()
    return rows

def check_player(name):
    """ Query all rows in the players table """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE name=?", (name,))
    rows = cur.fetchall()
    conn.close()
    if len(rows) > 0:
        return True
    else:
        return False

def get_all_stats():
    """ Query all rows in the stats table """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cloud_stats")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_latest_stats():
    """ Query the latest row in the stats table """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cloud_stats ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row

def two_cols_of_stats():
    """ Query date and players_online columns from stats table """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT date, players_online FROM cloud_stats")
    rows = cur.fetchall()
    conn.close()
    formatted_entries = []
    for date_str, players in rows:
        formatted_entries.append(f'  {{Date: new Date("{date_str}"), Players: {players}}}')

    output = "[\n" + ",\n".join(formatted_entries) + "\n]" 
    return output

def graph_data():   
    """ Query date and players_online columns from cloud_stats table """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot FROM cloud_stats")
    rows = cur.fetchall()
    conn.close()
    
    formatted_entries = []
    for date_str, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot in rows:
        formatted_entries.append(f'  {{Date: new Date("{date_str}"), Players: {players_online}, Dom: {players_in_dom}, TDM: {players_in_tdm}, Inf: {players_in_inf}, GG: {players_in_gg}, TTT: {players_in_ttt}, Boot: {players_in_boot}}}')

    output = "[\n" + ",\n".join(formatted_entries) + "\n]" 
    return output

def clear_stats():
    """ Delete all rows in the stats table """
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cloud_stats")
    conn.commit()
    conn.close()

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
            add_stats(stats_tuple)
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
        clear_stats()
        print("All stats cleared.")
        
    else:
        print("Invalid choice.")