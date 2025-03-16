import logging
import csv
import os
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
    # Write the job data to the CSV file
    with open('job_listings.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data.title, data.company, data.link, data.date_text])
        print(f"[ON_DATA] Saved: {data.title} at {data.company} - {data.link} (Posted: {data.date_text})")

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
    # Write CSV header if the file is empty
    if not os.path.exists('job_listings.csv'):
        with open('job_listings.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Company', 'Link', 'Posted Time'])

    # Print the start of the process
    print("LinkedIn Job Listings")
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("Scraping jobs...")
    scrape_jobs()

if __name__ == "__main__":
    main()
