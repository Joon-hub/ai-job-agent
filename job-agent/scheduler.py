"""Runs the pipeline daily at 8am."""
import schedule
import time
from crew import run_pipeline


def main():
    print("[scheduler] Starting. Will run daily at 08:00.")
    schedule.every().day.at("08:00").do(run_pipeline)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
