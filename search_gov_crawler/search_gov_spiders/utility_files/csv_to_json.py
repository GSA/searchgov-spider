import csv
import json
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timedelta
import tldextract

def extract_domain(url: str) -> str:
    """Extracts the domain from a URL, removing www and ensuring consistency."""
    parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'https://{url}')
    extracted = tldextract.extract(parsed.netloc)
    domain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}".lstrip('.').replace("www.", "")
    return domain

def generate_cron_schedules(start_time="01:01 FRI", count=100, minute_interval=10):
    cron_schedules = []
    time_part, day_part = start_time.split()
    start_dt = datetime.strptime(time_part, "%M:%H")
    weekdays = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    start_day_index = weekdays.index(day_part.upper())
    
    for i in range(count):
        total_minutes = i * minute_interval
        new_dt = start_dt + timedelta(minutes=total_minutes)
        new_day_index = (start_day_index + (new_dt.day - 1)) % 7
        cron_schedules.append(f"{new_dt.minute:02} {new_dt.hour:02} * * {weekdays[new_day_index]}")
    
    return cron_schedules

def process_csv(input_csv, output_json, existing_entries=None, seen_domains=None):
    """Processes a CSV file, extracts domains, and generates a JSON file with scraping configurations."""
    input_path = Path(__file__).parent / input_csv
    output_path = Path(__file__).parent / output_json
    existing_entries = existing_entries or []
    seen_domains = seen_domains or set()
    
    with input_path.open(mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        domains = [row["x"].strip() for row in reader if row.get("x")]
    
    schedules = generate_cron_schedules(start_time="01:00 FRI", count=len(domains), minute_interval=1)
    
    new_entries = [
        {
            "name": f"modules.BWEB affiliate: {domain}",
            "allow_query_string": False,
            "allowed_domains": domain,
            "handle_javascript": False,
            "schedule": schedules[i],
            "output_target": "elasticsearch",
            "starting_urls": f"https://{raw_domain}/"
        }
        for i, raw_domain in enumerate(domains)
        if (domain := extract_domain(raw_domain)) not in seen_domains and not seen_domains.add(domain)
    ]
    
    with output_path.open("w", encoding='utf-8') as f:
        json.dump(existing_entries + new_entries, f, indent=4)

if __name__ == "__main__":
    scrutiny_json_path = Path(__file__).parent / "crawl-sites-production-scrutiny.json"
    
    with scrutiny_json_path.open() as f:
        existing_data = json.load(f)
    
    seen_domains = {extract_domain(entry["starting_urls"]) for entry in existing_data}
    
    process_csv("domains_bing_all.csv", "crawl-sites-production.json", existing_data, seen_domains)
