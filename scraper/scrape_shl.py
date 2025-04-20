import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://www.shl.com"
START_URL = f"{BASE_URL}/solutions/products/product-catalog/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_soup(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

def get_all_page_links():
    page_links = []
    url = START_URL
    while url:
        print(f"Scraping page: {url}")
        soup = get_soup(url)
        page_links.append(url)
        next_page = soup.select_one('.pagination__item.-arrow.-next > a')
        if next_page and next_page.get("href"):
            url = BASE_URL + next_page["href"]
        else:
            url = None
    return page_links

def parse_detail_page(url):
    soup = get_soup(url)
    data = {
        "url": url,
        "description": "",
        "duration": "",
        "test_type": "",
        "remote_support": "No",
    }

    # Description, duration, test type
    for row in soup.select("div.product-catalogue-training-calendar__row"):
        h4 = row.find("h4")
        if not h4:
            continue
        title = h4.text.strip()
        if "Description" in title:
            p = row.find("p")
            data["description"] = p.get_text(strip=True) if p else ""
        elif "Assessment length" in title:
            p = row.find("p")
            if p:
                match = re.search(r"(\d+)", p.get_text(strip=True))
                if match:
                    data["duration"] = int(match.group(1))  # just minutes
            types = row.select("span.product-catalogue__key")
            data["test_type"] = ", ".join(t.text.strip() for t in types)

    # Remote Testing (separate section)
    remote_tag = soup.select_one("p.product-catalogue__small-text span.catalogue__circle")
    if remote_tag and "-yes" in " ".join(remote_tag.get("class", [])):
        data["remote_support"] = "Yes"
    else:
        data["remote_support"] = "No"

    return data

def parse_table(soup):
    assessments = []
    for row in soup.select("tr[data-course-id]"):
        name_tag = row.select_one("td.custom__table-heading__title a")
        if not name_tag:
            continue
        relative_url = name_tag.get("href")
        full_url = BASE_URL + relative_url
        adaptive = "No"
        try:
            adaptive_tag = row.select("td")[2].select_one("span")
            if adaptive_tag and "-yes" in adaptive_tag.get("class", []):
                adaptive = "Yes"
        except IndexError:
            pass
        detail_data = parse_detail_page(full_url)
        detail_data["adaptive_support"] = adaptive
        assessments.append(detail_data)
        time.sleep(1)  # polite delay
    return assessments

def scrape_all():
    page_links = get_all_page_links()
    print(f"\n✅ Found {len(page_links)} pages to scrape.\n")
    all_assessments = []

    for i, url in enumerate(page_links):
        print(f"Scraping data from page {i+1}/{len(page_links)}")
        soup = get_soup(url)
        all_assessments.extend(parse_table(soup))
        time.sleep(2)

    import os
    output_path = os.path.join(os.path.dirname(__file__), "..","backend", "data", "shl_assessments.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_assessments, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(all_assessments)} assessments into 'shl_assessments.json'.")

if __name__ == "__main__":
    scrape_all()



