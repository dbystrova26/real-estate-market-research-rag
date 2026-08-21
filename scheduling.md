# Scheduling the Autonomous Agent

`run_autonomous_report.py` discovers what's new, drafts it, charts it, fact-checks it,
and either ships it (auto mode, self-gated) or asks you (review mode).

## Windows — Task Scheduler

1. Open **Task Scheduler** → **Create Basic Task**
2. Set a trigger (e.g. weekly, Monday 7:00 AM)
3. Action: **Start a program**
   - Program/script: your Python executable (e.g. `C:\Users\<you>\miniconda3\python.exe`)
   - Add arguments: `run_autonomous_report.py --mode auto`
   - Start in: your repo folder
4. Finish — `--mode auto` never blocks waiting for input and self-gates on grounding.

## macOS / Linux — cron

```bash
crontab -e
```
```
0 7 * * 1 cd /path/to/repo && /usr/bin/python3 run_autonomous_report.py --mode auto >> logs/cron.log 2>&1
```

## Simpler alternative — a Python daemon (any OS)

```python
# scheduler.py
import subprocess, schedule, time

def run_report():
    subprocess.run(["python", "run_autonomous_report.py", "--mode", "auto"])

schedule.every().monday.at("07:00").do(run_report)
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Auto vs. review

- **`--mode auto`** for scheduled/unattended runs — self-gates, drops anything not
  100% grounded, logs drops to `run_log_<date>.json`.
- **`--mode review`** for when you're at the keyboard and want to approve each
  section before it ships.

## Live search reliability

The default DuckDuckGo backend can be rate-limited or return fewer results on some
runs. For a truly unattended weekly job, `TAVILY_API_KEY` in `.env` is more reliable.
