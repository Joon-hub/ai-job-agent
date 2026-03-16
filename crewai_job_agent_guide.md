AI Job Hunting Agent with CrewAI A Beginner's Complete Guide ---
Prototype to Production

# 1. What is CrewAI and why use it?

CrewAI is a Python framework that lets you create a team of AI agents,
each with a specific role, set of tools, and goal. Instead of writing
one giant script, you define agents like you would assign tasks to
colleagues --- and CrewAI handles how they pass information between each
other and in what order they work.

## Why CrewAI over alternatives?

# 2. Environment setup (do this first)

Follow these steps exactly before writing any agent code. Getting the
environment right saves hours of debugging later. \## Step 1 --- Install
Python 3.11+ Check your Python version first: python --version If it
shows 3.10 or lower, download Python 3.11 from python.org. On Windows,
make sure to tick 'Add to PATH' during installation. \## Step 2 ---
Create a virtual environment A virtual environment keeps this project's
packages separate from everything else on your computer. mkdir job-agent
&& cd job-agent python -m venv venv \# On Mac/Linux: source
venv/bin/activate \# On Windows: venv`\Scripts`{=tex}`\activate`{=tex}
You should see (venv) at the start of your terminal prompt. Always
activate this before working on the project. \## Step 3 --- Install core
dependencies pip install crewai crewai-tools pip install playwright
beautifulsoup4 requests pip install anthropic python-dotenv pip install
sentence-transformers chromadb pip install python-docx apscheduler
playwright install chromium \## Step 4 --- Set up your API key Create a
file called .env in your project root:
ANTHROPIC_API_KEY=sk-ant-your-key-here \## Step 5 --- Project folder
structure Create this folder layout before starting: job-agent/ agents/
\# One file per agent tools/ \# Custom tools agents can call data/ \#
SQLite database + ChromaDB outputs/ \# Generated CVs and daily digests
resumes/ \# Your master resume (PDF or DOCX) .env \# API keys (never
commit this) main.py \# Entry point crew.py \# Crew assembly
scheduler.py \# Daily job runner

# 3. Phase 1 --- Build the prototype (Week 1-2)

The prototype proves the pipeline works end-to-end with simple, fake
data before you invest time in real scraping. This is the right beginner
approach --- get something running first, then improve it.

## 3.1 --- Create your first agent: Resume Analyser

Create the file agents/resume_analyser.py: from crewai import Agent,
Task from anthropic import Anthropic

def create_resume_agent(): return Agent( role='Resume Analyst',
goal='Extract skills, tools, experience, and gaps from a resume',
backstory='Expert HR analyst specialising in data science hiring in
Germany', verbose=True, llm='claude-haiku-4-5' )

def create_analysis_task(agent, resume_text): return Task(
description=f''' Analyse this resume and return a JSON object with: -
skills (list of technical skills) - tools (specific software, libraries,
frameworks) - education (degree, field, university) - years_experience
(number, 0 if student) - languages (programming and spoken languages) -
gaps (missing skills common in German DS jobs) Resume: {resume_text}
''', agent=agent, expected_output='JSON object with resume analysis' )

## 3.2 --- Create the Job Matcher agent

Create agents/job_matcher.py: from crewai import Agent, Task

def create_matcher_agent(): return Agent( role='Job Compatibility
Analyst', goal='Score how well a candidate matches a job description',
backstory='Specialist in German tech recruitment and data science hiring
criteria', verbose=True, llm='claude-haiku-4-5' )

def create_match_task(agent, resume_json, job_description): return Task(
description=f''' Given this candidate profile: {resume_json} And this
job description: {job_description} Return a JSON with: - match_score
(0-100) - strengths (list of matching skills) - gaps (missing
requirements) - likelihood (low/medium/high) - recommendation
(apply/skip/borderline) ''', agent=agent, expected_output='JSON match
assessment' ) \## 3.3 --- Assemble the prototype crew Create crew.py to
wire the agents together: from crewai import Crew, Process from
agents.resume_analyser import create_resume_agent, create_analysis_task
from agents.job_matcher import create_matcher_agent, create_match_task

SAMPLE_JOB = ''' Junior Data Scientist --- Berlin Requirements: Python,
pandas, scikit-learn, SQL, basic ML knowledge. German B2 preferred.
Experience: 0-2 years. Master's degree preferred. '''

def run_prototype(resume_text): \# Create agents analyser =
create_resume_agent() matcher = create_matcher_agent()

# Create tasks

analysis_task = create_analysis_task(analyser, resume_text) match_task =
create_match_task(matcher, '{analysis_result}', SAMPLE_JOB)

# Assemble crew (sequential: analysis runs first, then matching)

crew = Crew( agents=\[analyser, matcher\], tasks=\[analysis_task,
match_task\], process=Process.sequential, verbose=True )

return crew.kickoff() \## 3.4 --- Run the prototype Create main.py and
test with your resume: from dotenv import load_dotenv from crew import
run_prototype

load_dotenv()

MY_RESUME = ''' Paste your resume text here... '''

if **name** == '**main**': result = run_prototype(MY_RESUME)
print(result)

python main.py

# 4. Phase 2 --- Add real job scraping (Week 3-4)

## 4.1 --- Build the StepStone scraper tool

CrewAI agents use 'tools' --- Python functions decorated with @tool.
Create tools/job_scraper.py: from crewai.tools import tool from
playwright.sync_api import sync_playwright import sqlite3, hashlib, json

@tool def scrape_stepstone(search_query: str) -\> str: '''Scrapes
entry-level data science jobs from StepStone Germany.''' results = \[\]
with sync_playwright() as p: browser = p.chromium.launch(headless=True)
page = browser.new_page() url =
f'https://www.stepstone.de/jobs/data-scientist?q={search_query}'
page.goto(url, timeout=30000) page.wait_for_timeout(3000) jobs =
page.query_selector_all('article.job-element') for job in jobs\[:20\]:
title = job.query_selector('h2') company =
job.query_selector('\[data-at=job-item-company-name\]') if title and
company: results.append({ 'title': title.inner_text(), 'company':
company.inner_text(), 'source': 'stepstone' }) browser.close() return
json.dumps(results)

## 4.2 --- Set up SQLite storage

Create tools/database.py to store jobs and track duplicates: import
sqlite3

def init_db(): conn = sqlite3.connect('data/jobs.db') conn.execute('''
CREATE TABLE IF NOT EXISTS jobs ( id TEXT PRIMARY KEY, title TEXT,
company TEXT, location TEXT, description TEXT, url TEXT, source TEXT,
scraped_date TEXT, match_score REAL, status TEXT DEFAULT 'new' ) ''')
conn.execute(''' CREATE TABLE IF NOT EXISTS applications ( id INTEGER
PRIMARY KEY AUTOINCREMENT, job_id TEXT, applied_date TEXT, cv_version
TEXT, status TEXT, response_date TEXT, outcome TEXT ) ''') conn.commit()
return conn \## 4.3 --- Add the scraper agent to your crew Update
crew.py to include a dedicated scraper agent that uses your tool: from
agents.job_scraper_agent import create_scraper_agent, create_scrape_task
from tools.job_scraper import scrape_stepstone

def create_scraper_agent(): return Agent( role='Job Market Researcher',
goal='Find entry-level data science jobs in Germany daily',
backstory='Expert in navigating German tech job portals',
tools=\[scrape_stepstone\], verbose=True, llm='claude-haiku-4-5' )

# 5. Phase 3 --- CV tailoring and application (Week 5-6)

## 5.1 --- CV tailoring agent

This is the most important agent --- it rewrites your CV to match each
job's keywords without fabricating experience. Create
agents/cv_tailor.py: from crewai import Agent, Task

def create_cv_agent(): return Agent( role='Professional CV Writer',
goal='Tailor a CV for each specific job without fabricating experience',
backstory=''' Expert career coach specialising in data science roles in
Germany. Knows exactly which keywords German ATS systems scan for. Never
invents experience but expertly reframes real experience. ''',
verbose=True, llm='claude-sonnet-4-5' \# Use Sonnet here --- quality
matters )

def create_cv_task(agent, master_cv, job_description, company): return
Task( description=f''' Rewrite the candidate's CV for this specific role
at {company}. Master CV: {master_cv} Job description: {job_description}
Rules: 1. Mirror keywords from the job description naturally 2. Reorder
bullet points to highlight most relevant experience first 3. Rewrite the
professional summary for this specific role 4. NEVER fabricate skills,
experience, or qualifications 5. Keep it to one page if possible 6.
Output the full revised CV text ''', agent=agent, expected_output='Full
tailored CV text ready for formatting' ) \## 5.2 --- Generate a DOCX
file Create tools/cv_generator.py to convert the tailored CV text into a
proper Word document: from docx import Document from docx.shared import
Pt, RGBColor

def generate_cv_docx(cv_text, output_path): doc = Document() \# Set font
style = doc.styles\['Normal'\] style.font.name = 'Arial' style.font.size
= Pt(11)

# Parse and add sections

for line in cv_text.split('`\n`{=tex}'): if line.startswith('\#'): \#
Main heading p = doc.add_heading(line\[2:\], level=1) elif
line.startswith('\##'): \# Section heading p =
doc.add_heading(line\[3:\], level=2) elif line.startswith('-'): \#
Bullet doc.add_paragraph(line\[2:\], style='List Bullet') elif
line.strip(): doc.add_paragraph(line)

doc.save(output_path) return output_path \## 5.3 --- Human approval via
Telegram bot Before any application is submitted, you review and approve
it. A Telegram bot is the simplest way to do this. Install it: pip
install python-telegram-bot

Create a bot by messaging @BotFather on Telegram, then add to .env:
TELEGRAM_BOT_TOKEN=your-token-here TELEGRAM_CHAT_ID=your-chat-id-here

Create tools/approval_bot.py: import asyncio from telegram import Bot,
InlineKeyboardButton, InlineKeyboardMarkup

async def send_approval_request(job, cv_path, match_score): bot =
Bot(token=os.getenv('TELEGRAM_BOT_TOKEN')) chat_id =
os.getenv('TELEGRAM_CHAT_ID')

message = f''' New application ready for review: {job\['title'\]} at
{job\['company'\]} Match score: {match_score}% Location:
{job\['location'\]} '''

keyboard = InlineKeyboardMarkup(\[\[ InlineKeyboardButton('Approve',
callback_data=f'approve\_{job\["id"\]}'), InlineKeyboardButton('Skip',
callback_data=f'skip\_{job\["id"\]}'),\]\])

await bot.send_document(chat_id, open(cv_path, 'rb')) await
bot.send_message(chat_id, message, reply_markup=keyboard)

# 6. Phase 4 --- Full automation and tracking (Week 7-8)

## 6.1 --- Daily scheduler

Create scheduler.py to run the full pipeline every morning: from
apscheduler.schedulers.blocking import BlockingScheduler from crew
import run_daily_pipeline

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=7, minute=30) def
daily_job_hunt(): print('Starting daily job search...')
run_daily_pipeline()

if **name** == '**main**': scheduler.start() \## 6.2 --- Outcome tracker
After you receive replies (or silence), update the database. Create
tools/tracker.py: import sqlite3

def update_application_status(job_id, status, notes=''): conn =
sqlite3.connect('data/jobs.db') conn.execute(''' UPDATE applications SET
status=?, response_date=date('now'), outcome=? WHERE job_id=? ''',
(status, notes, job_id)) conn.commit()

# Status options: 'applied', 'viewed', 'rejected',

# 'phone_screen', 'interview', 'offer', 'ghosted'

## 6.3 --- Learning loop agent

After 4 weeks, run this agent to analyse your outcomes and suggest
improvements: def create_learner_agent(): return Agent(
role='Application Strategy Analyst', goal='Identify patterns in
successful and unsuccessful applications', backstory='Data-driven career
coach who improves job search strategy through outcome analysis',
verbose=True, llm='claude-sonnet-4-5' )

def create_learning_task(agent, applications_data): return Task(
description=f''' Analyse these job application outcomes:
{applications_data} Identify: which job types get responses, which
companies reply, which CV phrases correlate with interviews, what
match_score threshold predicts success. Recommend adjustments to
scoring, targeting, and CV language for the next 4 weeks. ''',
agent=agent, expected_output='Strategy report with actionable
recommendations' )

# 7. Scaling beyond the prototype

## 7.1 --- Add more job sources

Once StepStone scraping is stable, add these German portals in order of
effort: \## 7.2 --- Upgrade to multilingual embeddings When you are
ready to match jobs in German as well as English, swap the matching
logic from pure LLM to a hybrid embedding + LLM approach: from
sentence_transformers import SentenceTransformer import chromadb

# Load once at startup

model = SentenceTransformer('intfloat/multilingual-e5-large') client =
chromadb.Client() collection = client.create_collection('jobs')

def embed_and_store_job(job): embedding =
model.encode(job\['description'\]) collection.add(
embeddings=\[embedding.tolist()\], documents=\[job\['description'\]\],
ids=\[job\['id'\]\] )

def find_similar_jobs(resume_text, top_k=20): query_embedding =
model.encode(resume_text) results =
collection.query(query_embeddings=\[query_embedding.tolist()\],
n_results=top_k) return results \## 7.3 --- Move to a cloud server To
run the agent 24/7 without keeping your laptop on, deploy to a Hetzner
VPS (cheapest option for Germany): Sign up at hetzner.com --- choose the
CX21 plan (\~€3.79/month, Germany region) SSH into your server and clone
your Git repo Install Python 3.11, create the virtual environment,
install dependencies Copy your .env file securely using scp or Hetzner's
cloud console Run the scheduler with nohup so it survives SSH
disconnects: nohup python scheduler.py \> logs/scheduler.log 2\>&1 & Set
up log rotation so the log file does not grow forever: pip install
loguru \# Better logging with automatic rotation \## 7.4 --- Add a
Anschreiben (cover letter) agent Most German companies still expect a
formal cover letter. Add a dedicated agent: def
create_cover_letter_agent(): return Agent( role='German Business Letter
Writer', goal='Write a formal German-style Anschreiben for each
application', backstory=''' Expert in German business correspondence and
Bewerbungsschreiben conventions. Knows that German cover letters should
be formal, specific to the company, and no longer than one page. ''',
verbose=True, llm='claude-sonnet-4-5' )

# 8. The complete production crew

Once all phases are complete, your final crew.py assembles all agents:
from crewai import Crew, Process

def run_daily_pipeline(master_cv_text): \# Agents scraper =
create_scraper_agent() analyser = create_resume_agent() matcher =
create_matcher_agent() portfolio = create_portfolio_agent() cv_tailor =
create_cv_agent() tracker = create_learner_agent()

# Tasks (run in sequence)

tasks = \[ create_scrape_task(scraper), create_analysis_task(analyser,
master_cv_text), create_match_tasks(matcher), \# runs once per job found
create_portfolio_task(portfolio), create_daily_digest_task(), \# top 10
selection\]

crew = Crew( agents=\[scraper, analyser, matcher, portfolio, cv_tailor,
tracker\], tasks=tasks, process=Process.sequential, verbose=True,
memory=True \# Agents remember context across tasks )

result = crew.kickoff()

# CV tailoring + approval happens separately, triggered by user

# selection from the daily digest

return result

# 9. Common issues and fixes

# 10. Recommended learning roadmap

If you are new to Python and AI agents, follow this order:

Week 1: Set up environment, run the prototype (Section 3). Goal: see
CrewAI work. Week 2: Add SQLite storage and a second agent. Goal: data
persists across runs. Week 3: Add Playwright scraping for one portal.
Goal: real jobs in the database. Week 4: Add the CV tailor and generate
your first tailored DOCX. Goal: end-to-end pipeline. Week 5: Add
Telegram approval bot. Goal: you control every submission. Week 6:
Deploy to Hetzner VPS. Goal: runs automatically every morning. Week 7+:
Add more portals, cover letter agent, and outcome tracking. Month 3+:
Run the learning agent on your outcomes and iterate.
