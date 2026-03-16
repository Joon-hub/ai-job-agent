"""Digest Writer Agent — compiles a daily job digest."""
import anthropic
from datetime import date
from pathlib import Path
from typing import List, Dict

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


def run(client: anthropic.Anthropic, jobs: List[Dict]) -> str:
    if not jobs:
        return "[digest] No jobs to summarize."

    jobs_text = "\n".join(
        f"- {j['title']} @ {j['company']} | Score:{j.get('score','?')} | {j['url']}"
        for j in jobs
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": (
            f"Write a brief daily job digest in Markdown.\n"
            f"Top picks + ranked table (Title|Company|Score|URL).\n\nJobs:\n{jobs_text}"
        )}],
    )

    digest = message.content[0].text.strip()
    today = date.today().isoformat()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUTS_DIR / f"digest_{today}.md"
    out_path.write_text(digest)
    print(f"\n{'='*50}\n{digest}\n{'='*50}")
    return str(out_path)
