import logging
from datetime import datetime
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

# Event handler to process job data
def on_data(data: EventData):
    # Extract job information, filling missing fields with empty strings if necessary
    title = data.title if data.title else ""
    company = data.company if data.company else ""
    link = data.link if data.link else ""
    date_text = data.date_text if data.date_text else ""

    # Format the job information and append to the text file
    job_info = f"{title:<40} {company:<30} {link:<80} {date_text}\n"
    
    # Open file in append mode to save job data
    with open("job_listings.txt", "a") as f:
        f.write(job_info)
    
    print(f"[ON_DATA] Saved: {title} at {company} - {link} (Posted: {date_text})")

# Handle errors during scraping
def on_error(error):
    print(f'[ERROR] An error occurred: {error}')

# Handle the end of the scraping process
def on_end():
    print('[INFO] Scraping completed.')

# Scrape jobs
def scrape_jobs():
    scraper = LinkedinScraper(
        chrome_executable_path=None,
        headless=True,
        max_workers=1,
        slow_mo=1.0,
        page_load_timeout=40
    )

    # Set up event handlers
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    # Define search options
    common_options = QueryOptions(
        locations=['India'],
        apply_link=True,
        skip_promoted_jobs=True,
        limit=20,
        filters=QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            type=[TypeFilters.PART_TIME, TypeFilters.CONTRACT, TypeFilters.TEMPORARY, TypeFilters.FULL_TIME],
            on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE, OnSiteOrRemoteFilters.HYBRID, OnSiteOrRemoteFilters.ON_SITE],
            experience=[ExperienceLevelFilters.INTERNSHIP, ExperienceLevelFilters.ENTRY_LEVEL],
        )
    )

    queries = [Query(query=job_title, options=common_options) for job_title in JOB_TITLES]
    scraper.run(queries)

# Main function to start scraping
def main():
    # Print the start of the process
    print("LinkedIn Job Listings")
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create or clear the job listings text file and write headers
    with open("job_listings.txt", "w") as f:
        f.write(f"{'Job Title':<40} {'Company Name':<30} {'Job Link':<80} {'Posted Time'}\n")
        f.write("="*150 + "\n")

    print("Scraping jobs...")
    scrape_jobs()

if __name__ == "__main__":
    main()
