import argparse
import json
import plistlib
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlparse

# manually filter these scrutiny records by id
FILTER_IDS = (
    "20220616-073159",  # NOAA CoastWatch Central Pacific
    "20220411-163415",  # US Committee on the Marine Transportation System
    "20220712-164738",  # NASA James Webb Space Telescope
    "20190619-065717",  # NRCS WCC portal
    "20220615-165843",  # "NOAA Coastwatch Caribbean
)


def create_allowed_domain(starting_url: str) -> str:
    """Create allowed_domains value based on starting_url"""

    domain_netloc = urlparse(starting_url).netloc
    domain_substrs = domain_netloc.split(".")

    if domain_substrs[0].startswith("www"):
        return ".".join(domain_substrs[1:])

    return domain_netloc


def apply_manual_updates(input_record: dict) -> dict:
    """Fixes issues found in scrutiny file so that the json file is reproducable."""
    match input_record:
        case {"starting_urls": "https://www.dantes.mil/"}:
            output_record = input_record | {"name": "DOD DANTES"}
        case {"starting_urls": "https://www.cfm.va.gov/til/"}:
            output_record = input_record | {"allowed_domains": "cfm.va.gov/til/"}
        case {"starting_urls": "https://www.va.gov/accountability/"}:
            output_record = input_record | {"allowed_domains": "va.gov/accountability/"}
        case {"starting_urls": "https://www.va.gov/resources/"}:
            output_record = input_record | {"allowed_domains": "va.gov/resources/"}
        case {"starting_urls": "https://www.herc.research.va.gov/"}:
            output_record = input_record | {"allow_query_string": True, "name": "VA HERC Research"}
        case _:
            output_record = input_record

    return output_record


def convert_plist_to_json(input_file: str, output_file: str, write_full_output: bool):
    """Convert scrutiny plist into filterd json for search.gov crawling."""

    scrutity_plist_file = Path(input_file).resolve()
    if not scrutity_plist_file.exists():
        raise FileNotFoundError(f"Input file {scrutity_plist_file} does not exist!")

    # read input plist file
    input_scrutiny_records = plistlib.loads(scrutity_plist_file.read_text("UTF-8").encode())

    # transform data
    transformed_scrutiny_records = []
    for input_record in input_scrutiny_records:
        date_stamp = input_record.get("dateStamp", None)
        if isinstance(date_stamp, (datetime, date)):
            input_record["dateStamp"] = date_stamp.isoformat()

        transformed_scrutiny_records.append(input_record)

    if write_full_output:
        # write full json output
        scrutiy_json_file = Path(__file__).parent / scrutity_plist_file.with_suffix(".json").name
        with scrutiy_json_file.open("w", encoding="UTF-8") as output:
            json.dump(transformed_scrutiny_records, output, indent=4)

    # filter and write fields we need
    search_gov_records = [
        {
            "name": str(record["name"]).lstrip("_"),
            "allow_query_string": False,
            "allowed_domains": create_allowed_domain(record["startingUrl"]),
            "handle_javascript": record["runJS"],
            "starting_urls": record["startingUrl"],
        }
        for record in transformed_scrutiny_records
        if record["scheduleCalendarIntervalMatrix"] > 0 and record["id"] not in FILTER_IDS
    ]

    # apply manual fixes
    final_search_gov_records = [apply_manual_updates(record) for record in search_gov_records]
    search_gov_json_file = Path(__file__).parent / output_file
    with search_gov_json_file.open("w", encoding="UTF-8") as output:
        json.dump(final_search_gov_records, output, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process plist files from scrutiny.")
    parser.add_argument("--input_file", type=str, help="path to input file")
    parser.add_argument("--output_file", type=str, default="crawl-sites.json", help="name of file")
    parser.add_argument("--full_output", help="Also output the full json file", action="store_true")
    args = parser.parse_args()

    convert_plist_to_json(input_file=args.input_file, output_file=args.output_file, write_full_output=args.full_output)
