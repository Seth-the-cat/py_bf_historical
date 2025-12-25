from flask import Flask, render_template, request
from fetchStats import fetchStats, fetchMatchStats
import utils.sql as sql
import bleach

app = Flask(__name__)

nav = open("templates/nav.html", "r").read()

@app.route("/")
def index():
    try:
        latest_stats = sql.get_latest_stats()
        players_online = latest_stats[2]
        last_updated = latest_stats[1]
        raw_data = sql.graph_data()
    except TypeError:
        fetchStats()
        latest_stats = sql.get_latest_stats()
        players_online = latest_stats[2]
        last_updated = latest_stats[1]
        raw_data = sql.graph_data()
    except Exception as e:
        return f"<p>Error retrieving stats: {e}</p>"
    return render_template('index.html',
    players_online=players_online,
    last_updated=last_updated,
    raw_data=raw_data
    )

@app.route("/match/<username>")
def playerStats(username):
    match_html, players_in_match = fetchMatchStats(username)
    return render_template('match.html', username=username, match_html=match_html, players_in_match=players_in_match)

@app.route("/match")
def find_match():
    return render_template('findmatch.html')

@app.route("/addplayer")
def add_player():
    return render_template('addplayer.html')

# Debug route to manually trigger stats fetch
@app.route("/stats_test")
def stats_test():
    fetchStats()
    return f'<p>Latest stats: {sql.get_latest_stats()[2]}</p>'

# Show players over time data
@app.route("/playersOverTime")
def players_over_time():
    return sql.two_cols_of_stats()

# Show chart page for testing. Maybe redo graph with d3.js later
@app.route("/chart")
def chartPage():
    return render_template('e.html', raw_data=sql.graph_data())

@app.route('/api/addplayer', methods=['POST'])
def track_player():
    if request.method == 'POST':
        username = request.form.get('username')
        try:
            sql.add_player(bleach.clean(username))
        except ValueError:
            return "Bad Request" , 400
        return "OK", 200

@app.route('/player/<username>')
def check_if_tracking(username):
    print(sql.check_player(username))
    if sql.check_player(username):
        return render_template('player.html', response="stats go here")
    else:
        return render_template('player.html', response=f"<i>{username}</i>'s stats are not being tracked")

@app.route('/findplayer')
def find_player():
    return render_template('findplayer.html')

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    # You can keep this specifically for local testing if you want
    app.run(debug=True, use_reloader=True)