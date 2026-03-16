"""Job Searcher Agent — scores job listings against candidate profile."""
import anthropic
from typing import List, Dict


def run(client: anthropic.Anthropic, jobs: List[Dict], profile: str) -> List[Dict]:
    if not jobs:
        return []

    jobs_text = "\n".join(
        f"[{i}] {j['title']} @ {j['company']}: {j['description'][:150]}"
        for i, j in enumerate(jobs)
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": (
            f"Score each job 0-10 for this candidate. Reply only as: [index] score reason\n\n"
            f"Candidate: {profile}\n\nJobs:\n{jobs_text}"
        )}],
    )

    for line in message.content[0].text.strip().split("\n"):
        if not line.startswith("["):
            continue
        try:
            idx = int(line.split("]")[0][1:])
            parts = line.split("]")[1].strip().split(None, 1)
            jobs[idx]["score"] = float(parts[0])
            jobs[idx]["score_reason"] = parts[1] if len(parts) > 1 else ""
        except (ValueError, IndexError):
            pass

    return sorted(jobs, key=lambda j: j.get("score", 0), reverse=True)
