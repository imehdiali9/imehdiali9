from pathlib import Path
from datetime import date, timedelta
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup


USERNAME = "imehdiali9"
OUTPUT = Path("github-contributions.svg")

WIDTH = 860
HEIGHT = 150

# GitHub's contribution-calendar endpoint
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_contributions():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    }

    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    cells = soup.select(
        "td.ContributionCalendar-day[data-date]"
    )

    contributions = {}

    for cell in cells:
        day = cell.get("data-date")
        level = cell.get("data-level")

        if not day:
            continue

        try:
            level = int(level or 0)
        except ValueError:
            level = 0

        contributions[day] = level

    if not contributions:
        raise RuntimeError(
            "Could not find GitHub contribution data."
        )

    return contributions


def build_svg(contributions):
    # Keep the most recent ~1 year
    today = date.today()
    start = today - timedelta(days=364)

    # Move start back to Sunday so the calendar begins cleanly
    start -= timedelta(days=(start.weekday() + 1) % 7)

    days = []

    current = start

    while current <= today:
        key = current.isoformat()
        level = contributions.get(key, 0)

        days.append((current, level))
        current += timedelta(days=1)

    # Calendar geometry
    cell_size = 12
    gap = 3
    step = cell_size + gap

    left = 40
    top = 38

    # GitHub-like levels
    levels = {
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353",
    }

    parts = []

    parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{WIDTH}"
     height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}">

    <rect
        width="{WIDTH}"
        height="{HEIGHT}"
        rx="14"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="1.5"/>

    <!-- Header -->
    <text
        x="24"
        y="25"
        fill="#c9d1d9"
        font-family="monospace"
        font-size="12">
        GitHub Contributions
    </text>

    <text
        x="836"
        y="25"
        text-anchor="end"
        fill="#8b949e"
        font-family="monospace"
        font-size="10">
        {escape(USERNAME)}
    </text>

    <!-- Weekday labels -->
    <text x="8" y="53"
          fill="#8b949e"
          font-family="monospace"
          font-size="9">M</text>

    <text x="8" y="81"
          fill="#8b949e"
          font-family="monospace"
          font-size="9">W</text>

    <text x="8" y="109"
          fill="#8b949e"
          font-family="monospace"
          font-size="9">F</text>
''')

    # Organize days into calendar columns
    for index, (day, level) in enumerate(days):

        # Sunday = 0 ... Saturday = 6
        weekday = (day.weekday() + 1) % 7

        # Convert to Monday-first for our labels/layout
        row = day.weekday()

        column = index // 7

        x = left + column * step
        y = top + row * step

        fill = levels.get(level, levels[0])

        # Slight staggered entrance animation
        delay = min(index * 0.008, 2.5)

        parts.append(f'''
    <rect
        x="{x}"
        y="{y}"
        width="{cell_size}"
        height="{cell_size}"
        rx="2"
        fill="{fill}"
        opacity="0">

        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.25s"
            begin="{delay:.3f}s"
            fill="freeze"/>
    </rect>
''')

    # Legend
    legend_y = 128

    parts.append(f'''
    <text
        x="665"
        y="{legend_y + 9}"
        fill="#8b949e"
        font-family="monospace"
        font-size="9">
        Less
    </text>
''')

    for i in range(5):
        x = 700 + i * 15
        fill = levels[i]

        parts.append(f'''
    <rect
        x="{x}"
        y="{legend_y}"
        width="10"
        height="10"
        rx="2"
        fill="{fill}"/>
''')

    parts.append(f'''
    <text
        x="780"
        y="{legend_y + 9}"
        fill="#8b949e"
        font-family="monospace"
        font-size="9">
        More
    </text>

</svg>
''')

    return "".join(parts)


def main():
    print("Fetching GitHub contributions...")

    contributions = fetch_contributions()

    print(f"Found {len(contributions)} contribution days.")

    svg = build_svg(contributions)

    OUTPUT.write_text(svg, encoding="utf-8")

    print(f"Created: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()