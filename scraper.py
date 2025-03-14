import logging
import json
import os
from datetime import datetime, timedelta
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, OnSiteOrRemoteFilters

# Set logging level
logging.basicConfig(level=logging.INFO)

# List of job titles
JOB_TITLES = [
    "Software Engineer",
    "Intern Full Stack Developer",
    "Full Stack Developer",
    "Software Development Engineer (SDE)",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Intern",
    "Backend Intern",
    "Frontend Intern",
    "SDE Intern",
    "Junior Full Stack Developer",
    "Junior Software Engineer",
    "Junior Backend Developer",
    "Junior Frontend Developer",
    "Entry Level Full Stack Developer",
    "Entry Level Backend Developer",
    "Entry Level Frontend Developer",
    "Part-time Software Engineer",
    "Contract Full Stack Developer",
    "Temporary Backend Developer"
]

# File paths
DATA_FILE = 'job_listings.json'
TIMESTAMP_FILE = 'last_reset.json'

# Load job data
def load_job_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"jobs": [], "links": []}

# Load last reset timestamp
def load_last_reset():
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, 'r') as f:
            return datetime.fromisoformat(json.load(f))
    return datetime.now() - timedelta(days=4)

# Save job data
def save_job_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Save reset timestamp
def save_last_reset(timestamp):
    with open(TIMESTAMP_FILE, 'w') as f:
        json.dump(timestamp.isoformat(), f)

# Event handlers
def on_data(data: EventData):
    job_data = load_job_data()
    job_entry = {"title": data.title, "company": data.company, "link": data.link}
    
    if data.link not in job_data["links"]:
        job_data["jobs"].append(job_entry)
        job_data["links"].append(data.link)
        save_job_data(job_data)
        print('[ON_DATA]', data.title, data.company, data.link)

def on_error(error):
    print('[ON_ERROR]', error)
    if "authentication" in str(error).lower() or "429" in str(error):  # Possible cookie issue
        with open('error.log', 'a') as f:
            f.write(f"[{datetime.now()}] Possible cookie expiration: {error}\n")

def on_end():
    print('[ON_END]')

# Reset data every 3 days
def check_and_reset():
    last_reset = load_last_reset()
    now = datetime.now()
    if (now - last_reset).days >= 3:
        print('[RESET] Clearing job data after 3 days')
        save_job_data({"jobs": [], "links": []})
        save_last_reset(now)

# Initialize scraper
scraper = LinkedinScraper(
    chrome_executable_path=None,
    headless=True,
    max_workers=1,
    slow_mo=1.0,  # Increased to avoid detection
    page_load_timeout=40
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

# Define common query options
common_options = QueryOptions(
    locations=['India'],
    apply_link=True,
    skip_promoted_jobs=True,
    limit=5,
    filters=QueryFilters(
        relevance=RelevanceFilters.RECENT,
        time=TimeFilters.MONTH,
        type=[TypeFilters.PART_TIME, TypeFilters.CONTRACT, TypeFilters.TEMPORARY, TypeFilters.FULL_TIME],
        on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE, OnSiteOrRemoteFilters.HYBRID, OnSiteOrRemoteFilters.ON_SITE],
        experience=[ExperienceLevelFilters.INTERNSHIP, ExperienceLevelFilters.ENTRY_LEVEL],
    )
)

# Create queries
queries = [Query(query=job_title, options=common_options) for job_title in JOB_TITLES]

# Set LinkedIn cookie
os.environ['LI_AT_COOKIE'] = os.getenv('LI_AT_COOKIE')

# Run with reset check
check_and_reset()
scraper.run(queries)
