from flask import Flask, render_template
from fetchStats import fetchStats, fetchMatchStats
import sqlUtils
from minutesSince import minutesSince

app = Flask(__name__)

@app.route("/")
def index():
    try:
        latest_stats = sqlUtils.get_latest_stats()
        players_online = latest_stats[2]
        last_updated = minutesSince(latest_stats[1])
        raw_data = sqlUtils.graph_data()
    except TypeError:
        fetchStats()
        latest_stats = sqlUtils.get_latest_stats()
        players_online = latest_stats[2]
        last_updated = minutesSince(latest_stats[1])
        raw_data = sqlUtils.graph_data()
    except Exception as e:
        return f"<p>Error retrieving stats: {e}</p>"
    return render_template('index.html',
    players_online=players_online,
    last_updated=last_updated,
    raw_data=raw_data
    )

@app.route("/player/<username>")
def playerStats(username):
    match_html, players_in_match = fetchMatchStats(username)
    return render_template('player.html', username=username, match_html=match_html, players_in_match=players_in_match)

@app.route("/stats_test")
def stats_test():
    fetchStats()
    return f'<p>Latest stats: {sqlUtils.get_latest_stats()[2]}</p>'

@app.route("/playersOverTime")
def players_over_time():
    return sqlUtils.two_cols_of_stats()

@app.route("/chart")
def chartPage():
    return render_template('e.html', raw_data=sqlUtils.graph_data())

if __name__ == '__main__':
    # You can keep this specifically for local testing if you want
    app.run(debug=True, use_reloader=True)