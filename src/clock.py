from apscheduler.schedulers.blocking import BlockingScheduler
from fetchStats import fetchStats

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