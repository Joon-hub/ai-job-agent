"""Scrapes job listings from Indeed RSS and RemoteOK."""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time


def scrape_indeed(title: str, location: str = "remote", num_results: int = 10) -> List[Dict]:
    """Fetch jobs from Indeed via RSS feed."""
    query = title.replace(" ", "+")
    url = f"https://www.indeed.com/rss?q={query}&l={location}&sort=date"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; JobAgentBot/1.0)"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")[:num_results]
        jobs = []
        for item in items:
            jobs.append({
                "title": item.find("title").text if item.find("title") else "",
                "company": item.find("source").text if item.find("source") else "Unknown",
                "location": location,
                "url": item.find("link").text if item.find("link") else "",
                "description": BeautifulSoup(
                    item.find("description").text if item.find("description") else "", "html.parser"
                ).get_text()[:500],
                "source": "indeed",
            })
        return jobs
    except Exception as e:
        print(f"[scraper] Indeed error: {e}")
        return []


def scrape_remoteok(title: str, num_results: int = 10) -> List[Dict]:
    """Fetch jobs from RemoteOK JSON API."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; JobAgentBot/1.0)"}
    try:
        resp = requests.get("https://remoteok.com/api", headers=headers, timeout=10)
        data = resp.json()
        # First item is a legal notice, skip it
        jobs_raw = [j for j in data[1:] if isinstance(j, dict)]
        title_lower = title.lower()
        matched = [
            j for j in jobs_raw
            if title_lower in j.get("position", "").lower()
            or title_lower in " ".join(j.get("tags", [])).lower()
        ][:num_results]

        jobs = []
        for j in matched:
            jobs.append({
                "title": j.get("position", ""),
                "company": j.get("company", "Unknown"),
                "location": "Remote",
                "url": j.get("url", ""),
                "description": BeautifulSoup(j.get("description", ""), "html.parser").get_text()[:500],
                "source": "remoteok",
            })
        return jobs
    except Exception as e:
        print(f"[scraper] RemoteOK error: {e}")
        return []


def fetch_all_jobs(titles: List[str], location: str = "remote") -> List[Dict]:
    """Aggregate jobs from all sources for given titles."""
    all_jobs = []
    for title in titles:
        print(f"[scraper] Searching: {title}")
        all_jobs.extend(scrape_remoteok(title))
        time.sleep(1)
        all_jobs.extend(scrape_indeed(title, location))
        time.sleep(1)
    # Deduplicate by URL
    seen = set()
    unique = []
    for job in all_jobs:
        if job["url"] not in seen and job["url"]:
            seen.add(job["url"])
            unique.append(job)
    return unique
