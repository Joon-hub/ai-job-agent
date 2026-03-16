"""Entry point — run once or start the scheduler."""
import sys
from crew import run_pipeline

if __name__ == "__main__":
    if "--schedule" in sys.argv:
        from scheduler import main
        main()
    else:
        run_pipeline()
