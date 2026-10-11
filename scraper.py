
import json
import os
import sys
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

SOURCE_URL = os.getenv(
    "SOURCE_URL",
    "https://www.livescore.com/en-za/betting-sites/offers/"
)
API_KEY = os.getenv("GEMINI_API_KEY")

HEADERS = {"User-Agent": "StudentBonusResearch/1.0"}


def check_robots(url):
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"

    response = requests.get(robots_url, headers=HEADERS, timeout=15)

    if response.status_code in (401, 403, 429):
        raise RuntimeError("Access to robots.txt is restricted. Choose another source.")

    if response.status_code == 404:
        print("robots.txt was not found; check the website terms before proceeding.")
        return

    response.raise_for_status()

    parser = urllib.robotparser.RobotFileParser()
    parser.parse(response.text.splitlines())

    if not parser.can_fetch(HEADERS["User-Agent"], url):
        raise RuntimeError("robots.txt disallows this page. Choose another source.")

    print("Crawling rules permit the selected URL.")


def main():
    if not API_KEY:
        sys.exit("GEMINI_API_KEY is missing from .env.")

    print("1. Checking website rules...")
    check_robots(SOURCE_URL)

    print("2. Downloading public page...")
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=20)

    if response.status_code in (401, 403, 429):
        raise RuntimeError(
            f"Website returned HTTP {response.status_code}. "
            "Stop and select another permitted source."
        )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer"]):
        tag.decompose()

    page_text = soup.get_text(" ", strip=True)

    if len(page_text) < 200:
        raise RuntimeError("Not enough readable page text. Choose another public source.")

    print("3. Asking Gemini to structure the extracted data...")
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
Extract exactly three distinct casino offers from the page text below.
Return JSON with a "casinos" array. Each object must contain:
casino_name, welcome_bonus, wagering_requirement, minimum_deposit, source_url.

wagering_requirement must be a number (e.g. 35 for 35x) or null.
For missing bonus or deposit values, use "Not stated".
Do not guess or invent information.
source_url must equal: {SOURCE_URL}

Page text:
{page_text[:15000]}
"""

    result = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0,
        },
    )

    data = json.loads(result.text or "{}")
    casinos = data.get("casinos", [])

    required = {
        "casino_name", "welcome_bonus", "wagering_requirement",
        "minimum_deposit", "source_url"
    }

    valid = []
    seen = set()

    for item in casinos:
        if not isinstance(item, dict) or not required.issubset(item):
            continue
        name = str(item["casino_name"]).strip()
        if not name or name.lower() in seen:
            continue
        if item["source_url"] != SOURCE_URL:
            continue

        multiplier = item["wagering_requirement"]
        if multiplier is not None and (
            isinstance(multiplier, bool)
            or not isinstance(multiplier, (int, float))
        ):
            continue

        seen.add(name.lower())
        valid.append(item)

    if len(valid) != 3:
        raise RuntimeError(
            f"Only {len(valid)} valid records found. "
            "Do not fill in missing data by hand; choose a better source."
        )

    output = {
        "source_url": SOURCE_URL,
        "casinos": valid,
    }

    output_path = PROJECT_DIR / "bonuses.json"
    output_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Success! Saved three records to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        sys.exit(f"Scraper failed: {error}")