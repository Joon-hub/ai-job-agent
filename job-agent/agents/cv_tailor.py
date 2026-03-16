"""CV Tailor Agent — rewrites master resume for a specific job."""
import anthropic
from tools.cv_generator import load_master_resume, save_tailored_cv
from tools.database import save_cv_output


def run(client: anthropic.Anthropic, job: dict) -> str:
    master = load_master_resume()
    if not master:
        return "[cv_tailor] Add a master resume (.txt or .md) to resumes/"

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": (
            f"Rewrite this resume for the job below. Keep truthful, ATS-optimized, Markdown format.\n\n"
            f"Job: {job['title']} @ {job['company']}\n{job['description'][:400]}\n\n"
            f"Resume:\n{master[:1500]}"
        )}],
    )

    content = message.content[0].text.strip()
    out_path = save_tailored_cv(job["company"], job["title"], content)
    save_cv_output(job["url"], str(out_path))
    return str(out_path)
