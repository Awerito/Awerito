#!/usr/bin/env python3
"""Update README.md with life progress bar."""

import os
import re
import urllib.request
import json
from datetime import date

# World Bank API for Chilean male life expectancy
WORLD_BANK_API = (
    "https://api.worldbank.org/v2/country/CL/indicator/SP.DYN.LE00.MA.IN"
    "?format=json&per_page=5"
)

# Fallback value if API fails (2023 data)
FALLBACK_LIFE_EXPECTANCY = 79.2

WEEKS_PER_YEAR = 52.1429

# Progress bar settings
BAR_LENGTH = 20
FILLED_CHAR = "\u2588"  # █
EMPTY_CHAR = "\u2591"  # ░

START_MARKER = "<!-- LIFE-PROGRESS:START -->"
END_MARKER = "<!-- LIFE-PROGRESS:END -->"


def fetch_life_expectancy() -> tuple[float, str | None]:
    """Fetch Chilean male life expectancy from World Bank API."""
    try:
        with urllib.request.urlopen(WORLD_BANK_API, timeout=10) as response:
            data = json.loads(response.read().decode())

        if not data[1]:
            return FALLBACK_LIFE_EXPECTANCY, None

        # Find the most recent non-null value
        for record in data[1]:
            if record["value"] is not None:
                return record["value"], record["date"]

        return FALLBACK_LIFE_EXPECTANCY, None
    except Exception as e:
        print(f"Warning: Could not fetch from World Bank API: {e}")
        print(f"Using fallback value: {FALLBACK_LIFE_EXPECTANCY}")
        return FALLBACK_LIFE_EXPECTANCY, None


def calculate_weeks_lived(birth_date: date) -> int:
    """Calculate the number of weeks lived since birth."""
    today = date.today()
    days_lived = (today - birth_date).days
    return days_lived // 7


def generate_progress_bar(current: int, total: int, data_year: str | None) -> str:
    """Generate a text-based progress bar."""
    percentage = (current / total) * 100
    filled = int((current / total) * BAR_LENGTH)
    empty = BAR_LENGTH - filled

    bar = FILLED_CHAR * filled + EMPTY_CHAR * empty
    year_info = f" (data: {data_year})" if data_year else ""

    return f"\u23f3 Week {current:,} of {total:,} | {bar} | {percentage:.1f}%{year_info}"


def update_readme(progress_line: str) -> None:
    """Update README.md with the progress line between markers."""
    readme_path = "README.md"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL,
    )

    replacement = f"{START_MARKER}\n{progress_line}\n{END_MARKER}"
    new_content = pattern.sub(replacement, content)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def main() -> None:
    """Main entry point."""
    birth_date_str = os.environ.get("BIRTH_DATE")

    if not birth_date_str:
        print("Error: BIRTH_DATE environment variable not set")
        print("Expected format: YYYY-MM-DD")
        exit(1)

    try:
        birth_date = date.fromisoformat(birth_date_str)
    except ValueError:
        print(f"Error: Invalid date format '{birth_date_str}'")
        print("Expected format: YYYY-MM-DD")
        exit(1)

    # Fetch life expectancy from World Bank
    life_expectancy, data_year = fetch_life_expectancy()
    total_weeks = int(life_expectancy * WEEKS_PER_YEAR)

    print(f"Life expectancy: {life_expectancy} years ({data_year or 'fallback'})")
    print(f"Total weeks: {total_weeks:,}")

    weeks_lived = calculate_weeks_lived(birth_date)
    progress_line = generate_progress_bar(weeks_lived, total_weeks, data_year)

    print(f"Progress: {progress_line}")
    update_readme(progress_line)
    print("README.md updated successfully")


if __name__ == "__main__":
    main()
