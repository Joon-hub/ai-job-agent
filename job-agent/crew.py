"""Assembles and runs the full agent pipeline."""
import os
import anthropic
from dotenv import load_dotenv

from tools.job_scraper import fetch_all_jobs
from tools.database import init_db, save_jobs, get_unseen_jobs, update_score, mark_seen
from agents import job_searcher, cv_tailor, digest_writer

load_dotenv()

CANDIDATE_PROFILE = """
Experienced software engineer with 3+ years in Python, REST APIs, and cloud services.
Comfortable with Django, FastAPI, AWS. Looking for remote roles.
"""


def run_pipeline():
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    titles = [t.strip() for t in os.getenv("JOB_TITLES", "Software Engineer").split(",")]
    location = os.getenv("JOB_LOCATION", "remote")

    # 1. Scrape
    print("[crew] Scraping jobs...")
    raw_jobs = fetch_all_jobs(titles, location)
    new = save_jobs(raw_jobs)
    print(f"[crew] {new} new jobs saved.")

    # 2. Score
    unseen = get_unseen_jobs(limit=20)
    if not unseen:
        print("[crew] No new jobs to process.")
        return

    print(f"[crew] Scoring {len(unseen)} jobs...")
    scored = job_searcher.run(client, unseen, CANDIDATE_PROFILE)

    for j in scored:
        if j.get("id"):
            update_score(j["id"], j.get("score", 0))

    mark_seen([j["id"] for j in scored if j.get("id")])

    # 3. Tailor CVs for top 3
    top = [j for j in scored if j.get("score", 0) >= 7][:3]
    for job in top:
        print(f"[crew] Tailoring CV for: {job['title']} @ {job['company']}")
        path = cv_tailor.run(client, job)
        print(f"[crew] Saved: {path}")

    # 4. Digest
    print("[crew] Writing digest...")
    digest_path = digest_writer.run(client, scored[:10])
    print(f"[crew] Digest: {digest_path}")
