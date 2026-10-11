
# Casino Bonus Scraper

A small Python project that extracts welcome bonus information from a public casino offers page, uses Google's Gemini model to structure the extracted text, saves the result to JSON, and displays the data on a responsive web page.

## Features

- Retrieves page content from a configured public source.
- Checks the source's robots.txt rules before fetching the page.
- Uses a language model to structure bonus information.
- Saves records to `bonuses.json`.
- Displays the JSON records in `index.html`.

## Project files

- `scraper.py` — scraper and AI extraction step.
- `bonuses.json` — output from the scraper.
- `index.html` — responsive comparison page.
- `.env` — local configuration and API key (not committed).
- `.gitignore` — excludes secrets and the virtual environment.

## Requirements

- Python 3
- Internet access
- A Gemini API key with access to an available model

## Installation

Open a terminal in the project folder.

Create a virtual environment if you do not already have one:

```bash
python -m venv .venv
```

Install the packages:

```bash
python -m pip install requests beautifulsoup4 python-dotenv google-genai
```

Create a `.env` file in the project folder:

```text
GEMINI_API_KEY=your_key_here
SOURCE_URL=https://www.livescore.com/en-za/betting-sites/offers/
```

Replace `your_key_here` with your own API key. Never commit `.env` to Git.

## Run the scraper

On Windows, run:

```powershell
.\.venv\Scripts\python.exe scraper.py
```

The script should write the extracted records to `bonuses.json`.

## Run the web page locally

Start a local web server:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000
```

Open http://localhost:8000 in your browser.

## Data and limitations

The extracted information depends on the source page's publicly accessible content and the language model's extraction quality. Verify the results against the source. Missing values must not be guessed.

The scraper may need maintenance if the source changes, blocks access, or changes its published offer terms. Respect robots.txt and the source's terms. Do not bypass access restrictions.

The static web page displays the JSON file included in the published project. It does not run the scraper automatically.