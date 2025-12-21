import json
import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    try:
        conn.cursor().execute("CREATE TABLE cloud_stats (id integer PRIMARY KEY, date text, players_online integer, players_in_dom integer, players_in_tdm integer, players_in_inf integer, players_in_gg integer, players_in_ttt integer, players_in_boot integer)")
    except sqlite3.Error as e:
        print(e)

    return conn

def add_stats(stats):
    conn = create_connection("stats.db")
    """
    Create a new stats entry into the stats table
    :param conn:
    :param stats:
    :return: stats id
    """
    sql = ''' INSERT INTO cloud_stats(date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, stats)
    conn.commit()
    return cur.lastrowid

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
    conn = create_connection("stats.db")
    """
    Query the latest row in the stats table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM cloud_stats ORDER BY id DESC LIMIT 1")

    row = cur.fetchone()

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
    conn = create_connection("stats.db")
    """
    Query date and players_online columns from cloud_stats table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot FROM stats")

    rows = cur.fetchall()
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
    print("Runable functions:\n1. add_stats(stats_tuple)\n2. get_all_stats()\n3. get_latest_stats()\n4. two_cols_of_stats()\n5. clear_stats()")
    choice = input("Enter the number of the function you want to run: ")
    if choice == "1":
        print("Enter stats as comma-separated values (date, players_online, players_in_dom, players_in_tdm, players_in_inf, players_in_gg, players_in_ttt, players_in_boot):")
        stats_input = input()
        stats_tuple = tuple(stats_input.split(","))
        add_stats(stats_tuple)
        print("Stats added.")
    elif choice == "2":
        print("All stats:")
        for row in get_all_stats():
            print(row)
    elif choice == "3":
        print("Latest stats:")
        print(get_latest_stats())
    elif choice == "4":
        print("Two columns of stats:")
        print(two_cols_of_stats())
    elif choice == "5": 
        clear_stats()
        print("All stats cleared.")
    else:
        print("Invalid choice.")