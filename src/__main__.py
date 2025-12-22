from flask import Flask, render_template
from fetchStats import fetchStats, fetchMatchStats
import utils.sql as sqlUtils

from apscheduler.schedulers.blocking import BlockingScheduler

# Use BlockingScheduler so the script stays alive
sched = BlockingScheduler()

# Schedule the job
sched.add_job(fetchStats, 'interval', minutes=10)

print("Worker started. Running initial fetch...")
try:
    fetchStats() # Run once on startup
except Exception as e:
    print(f"Error in initial fetch: {e}")

# Start the scheduler (this will block and keep the container running)
sched.start()

app = Flask(__name__)

@app.route("/")
def index():
    try:
        latest_stats = sqlUtils.get_latest_stats()
        players_online = latest_stats[2]
        last_updated = latest_stats[1]
        raw_data = sqlUtils.graph_data()
    except TypeError:
        fetchStats()
        latest_stats = sqlUtils.get_latest_stats()
        players_online = latest_stats[2]
        last_updated = latest_stats[1]
        raw_data = sqlUtils.graph_data()
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

@app.route("/addplayer")
def add_player():
    return render_template('addplayer.html')

# Debug route to manually trigger stats fetch
@app.route("/stats_test")
def stats_test():
    fetchStats()
    return f'<p>Latest stats: {sqlUtils.get_latest_stats()[2]}</p>'

# Show players over time data
@app.route("/playersOverTime")
def players_over_time():
    return sqlUtils.two_cols_of_stats()

# Show chart page for testing. Maybe redo graph with d3.js later
@app.route("/chart")
def chartPage():
    return render_template('e.html', raw_data=sqlUtils.graph_data())

if __name__ == '__main__':
    # You can keep this specifically for local testing if you want
    app.run(debug=True, use_reloader=True)