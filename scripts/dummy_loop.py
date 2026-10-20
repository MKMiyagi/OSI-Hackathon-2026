"""Overnight-sleep test: 30 ticks a minute apart. Run under caffeinate -dims."""
import datetime
import time

for i in range(30):
    print(datetime.datetime.now().isoformat(), "tick", i, flush=True)
    time.sleep(60)
