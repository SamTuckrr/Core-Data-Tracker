import requests
from bs4 import BeautifulSoup
from typing import List, Dict

INDEED_URL = "https://uk.indeed.com/jobs"


def search_jobs(keyword: str, location: str) -> List[Dict]:
    params = {"q": keyword, "l": location}
    resp = requests.get(INDEED_URL, params=params, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    for card in soup.select("a.tapItem"):
        title = card.select_one("h2 span").get_text(strip=True)
        company = card.select_one("span.companyName")
        summary = card.select_one("div.job-snippet")
        link = "https://uk.indeed.com" + card.get("href")
        jobs.append({
            "title": title,
            "company": company.get_text(strip=True) if company else "",
            "summary": summary.get_text(" ", strip=True) if summary else "",
            "link": link,
        })
    return jobs
