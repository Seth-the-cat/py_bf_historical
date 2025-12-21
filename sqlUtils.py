import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')

# Ensure the 'data' directory exists before we try to connect
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists('stats.db'):
    try:
        conn = sqlite3.connect('stats.db')
    except sqlite3.Error as e:
        print(f"Error connecting to database at stats.db: {e}")

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
    conn.close() # Good practice to close connections
    return last_id

def get_all_stats():
    conn = create_connection("stats.db")
    """
    Query all rows in the stats table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM cloud_stats")

    rows = cur.fetchall()

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
    conn = create_connection("stats.db")
    """
    Query date and players_online columns from stats table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT date, players_online FROM cloud_stats")

    rows = cur.fetchall()

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
    conn = create_connection("stats.db")
    """
    Delete all rows in the stats table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("DELETE FROM cloud_stats")
    conn.commit()

if __name__ == '__main__':
    print("Runable functions:\n1. Create Connection\n2. add_stats(stats_tuple)\n3. get_all_stats()\n4. get_latest_stats()\n5. two_cols_of_stats()\n6. clear_stats()")
    choice = input("Enter the number of the function you want to run: ")
    if choice == "1":
        conn = create_connection("stats.db")
        if conn:
            print("Connection to database established.")
        else:
            print("Failed to establish connection.")
    if choice == "2":
        print("Enter stats as comma-separated values (date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot):")
        stats_input = input()
        stats_tuple = tuple(stats_input.split(","))
        add_stats(stats_tuple)
        print("Stats added.")
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