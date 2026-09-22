from pathlib import Path
from xml.sax.saxutils import escape


OUTPUT = Path("info-card.svg")

WIDTH = 490
HEIGHT = 370

# Information taken from your portfolio
NAME = "MEHDI ALI"

ROWS = [
    ("ROLE", "IT / Software Developer"),
    ("LOCATION", "Kochi, Kerala, IN"),
    ("EDUCATION", "B.Tech IT @ CUSAT"),
    ("STACK", "JS / C / Python / Shell"),
    ("WEB", "React / A-Frame / Tailwind"),
    ("SYSTEMS", "Linux / AOSP / Android"),
    ("FOCUS", "WebVR / ROM Development"),
    ("STATUS", "ONLINE • AVAILABLE"),
]


def esc(text):
    return escape(str(text))


def build_svg():
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

    <!-- Terminal top bar -->
    <circle cx="22" cy="22" r="5" fill="#ff5f56"/>
    <circle cx="40" cy="22" r="5" fill="#ffbd2e"/>
    <circle cx="58" cy="22" r="5" fill="#27c93f"/>

    <text
        x="78"
        y="27"
        fill="#8b949e"
        font-family="monospace"
        font-size="12">
        mehdi@github: ~
    </text>

    <!-- Prompt -->
    <text
        x="28"
        y="65"
        fill="#39d353"
        font-family="monospace"
        font-size="13">
        $ whoami
    </text>

    <!-- Name -->
    <text
        x="28"
        y="94"
        fill="#f0f6fc"
        font-family="monospace"
        font-size="23"
        font-weight="bold">
        {esc(NAME)}
    </text>

    <!-- Divider -->
    <line
        x1="28"
        y1="112"
        x2="462"
        y2="112"
        stroke="#30363d"
        stroke-width="1"/>

    <!-- neofetch-style rows -->
''')

    start_y = 140
    spacing = 25

    for i, (key, value) in enumerate(ROWS):
        y = start_y + i * spacing
        delay = 0.15 + i * 0.12

        parts.append(f'''
    <g opacity="0">
        <text
            x="30"
            y="{y}"
            fill="#8b949e"
            font-family="monospace"
            font-size="12"
            font-weight="bold">
            {esc(key)}
        </text>

        <text
            x="150"
            y="{y}"
            fill="#c9d1d9"
            font-family="monospace"
            font-size="12">
            {esc(value)}
        </text>

        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.35s"
            begin="{delay:.2f}s"
            fill="freeze"/>
    </g>
''')

    parts.append('''
    <!-- Bottom prompt -->
    <text
        x="30"
        y="345"
        fill="#39d353"
        font-family="monospace"
        font-size="12">
        $
    </text>

    <rect
        x="43"
        y="333"
        width="7"
        height="15"
        fill="#c9d1d9">
        <animate
            attributeName="opacity"
            values="1;0;1"
            dur="1s"
            repeatCount="indefinite"/>
    </rect>

</svg>
''')

    return "".join(parts)


OUTPUT.write_text(build_svg(), encoding="utf-8")

print(f"Created: {OUTPUT.resolve()}")