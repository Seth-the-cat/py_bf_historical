from flask import Flask, render_template
from flask_apscheduler import APScheduler
import sched, time
from fetchStats import fetchStats
# from debugUtils import saysomething
import sqlUtils
from minutesSince import minutesSince

app = Flask(__name__)

scheduler = APScheduler()
scheduler.init_app(app)

# run function

@app.route("/")
def index():
    return render_template('index.html', players_online=sqlUtils.get_latest_stats()[2], last_updated=minutesSince(sqlUtils.get_latest_stats()[1]))

@app.route("/player/<username>")
def playerStats(username):
    return f'<p>Stats for player <strong>{username}<strong></p>'

@app.route("/stats_test")
def stats_test():
    fetchStats()
    return f'<p>Latest stats: {sqlUtils.get_latest_stats()[2]}</p>'

if __name__ == '__main__':
    # Add the job
    scheduler.add_job(id='Scheduled Task', func=fetchStats, trigger='interval', minutes=10)
    
    # Start the scheduler
    scheduler.start()
    
    # Start the Flask server
    # use_reloader=False is important! Otherwise, the scheduler might run twice.
    app.run(debug=True, use_reloader=False)