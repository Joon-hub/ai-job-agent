# AI Job Agent

An autonomous job search agent that scrapes remote job listings daily, scores them against your profile using Claude AI, tailors your resume for top matches, and produces a daily digest.

---

## What It Does

1. **Scrapes** job listings from RemoteOK and Indeed RSS
2. **Scores** each job 0–10 based on fit with your candidate profile (Claude Haiku)
3. **Tailors** your master resume for every job scoring 7+ (outputs `.docx`)
4. **Writes** a daily digest Markdown file with a ranked job table and top picks

---

## Project Structure

```
job-agent/
  agents/
    job_searcher.py   # scores jobs with Claude AI
    cv_tailor.py      # rewrites resume per job
    digest_writer.py  # writes daily summary
  tools/
    job_scraper.py    # scrapes RemoteOK + Indeed
    database.py       # SQLite deduplication
    cv_generator.py   # exports tailored .docx CVs
  data/               # SQLite database (auto-created)
  outputs/            # generated CVs + digests
  resumes/            # your master resume (not committed)
  .env                # API keys (never committed)
  main.py             # entry point
  crew.py             # pipeline assembly
  scheduler.py        # daily 8am runner
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ai-job-agent.git
cd ai-job-agent
```

### 2. Install dependencies

```bash
pip3 install anthropic python-dotenv requests beautifulsoup4 python-docx schedule chromadb
```

### 3. Configure environment

```bash
cp .env.example .env
```

Open `.env` and add your [Anthropic API key](https://console.anthropic.com) and job search preferences:

```env
ANTHROPIC_API_KEY=sk-ant-...
JOB_TITLES=Software Engineer,Backend Engineer
JOB_LOCATION=Remote
```

### 4. Add your master resume

Create `resumes/resume.txt` or `resumes/resume.md` with your full resume in plain text.

### 5. Update your candidate profile

Open `crew.py` and edit `CANDIDATE_PROFILE` (line ~14) with a short description of your experience and what you're looking for.

---

## Usage

**Run once:**
```bash
python3 main.py
```

**Run on a daily schedule (8am):**
```bash
python3 main.py --schedule
```

---

## Output

| File | Description |
|------|-------------|
| `outputs/digest_YYYY-MM-DD.md` | Daily ranked job list with top picks |
| `outputs/CV_Company_Role.docx` | Tailored resume per top job |

---

## Cost

Uses Claude Haiku — the cheapest Claude model.

| Task | Approx. cost per run |
|------|----------------------|
| Score 20 jobs | ~$0.001 |
| Tailor 3 CVs | ~$0.003 |
| Write digest | ~$0.001 |
| **Total/day** | **~$0.005** |

Running daily for a month ≈ **$0.15**

---

## Tech Stack

- [Anthropic Claude](https://anthropic.com) — AI scoring and CV tailoring
- [RemoteOK API](https://remoteok.com/api) — remote job listings
- Indeed RSS — additional job listings
- SQLite — job deduplication and storage
- python-docx — DOCX resume generation

---

## Roadmap

- [ ] Email digest delivery
- [ ] LinkedIn job scraping
- [ ] Cover letter generation
- [ ] ChromaDB semantic deduplication
- [ ] Web dashboard

---

## Security

- `.env` is in `.gitignore` — your API key is never committed
- Copy `.env.example` to `.env` and fill in your own keys
- `resumes/` and `outputs/` are also excluded from git
