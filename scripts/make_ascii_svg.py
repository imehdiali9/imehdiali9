from pathlib import Path
from PIL import Image
from xml.sax.saxutils import escape


INPUT = Path("source-prepped.png")
OUTPUT = Path("imehdiali9-ascii.svg")

COLUMNS = 90

# Light -> dark
RAMP = " .`:-=+*#%@"

BACKGROUND = "#0d1117"
FOREGROUND = "#c9d1d9"

CHAR_WIDTH = 8
CHAR_HEIGHT = 14

ROW_DURATION = 0.32
ROW_DELAY = 0.055


if not INPUT.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT}"
    )


print("Reading prepared image...")

image = Image.open(INPUT).convert("L")


# ------------------------------------------------------------
# Crop around the actual subject
# ------------------------------------------------------------

print("Finding subject...")

pixels = image.load()
width, height = image.size

threshold = 245

xs = []
ys = []

for y in range(height):
    for x in range(width):
        if pixels[x, y] < threshold:
            xs.append(x)
            ys.append(y)

if not xs:
    raise RuntimeError("Could not detect the subject.")

left = min(xs)
right = max(xs)
top = min(ys)
bottom = max(ys)

crop_width = right - left + 1
crop_height = bottom - top + 1

padding_x = int(crop_width * 0.04)
padding_y = int(crop_height * 0.04)

left = max(0, left - padding_x)
right = min(width - 1, right + padding_x)
top = max(0, top - padding_y)
bottom = min(height - 1, bottom + padding_y)

image = image.crop(
    (left, top, right + 1, bottom + 1)
)

print(
    f"Cropped subject: "
    f"{image.width} × {image.height}px"
)


# ------------------------------------------------------------
# Resize for ASCII
# ------------------------------------------------------------

aspect_ratio = image.height / image.width

rows = max(
    1,
    round(COLUMNS * aspect_ratio * 0.52)
)

image = image.resize(
    (COLUMNS, rows),
    Image.Resampling.LANCZOS
)

print(
    f"ASCII grid: "
    f"{COLUMNS} × {rows}"
)


# ------------------------------------------------------------
# Convert image to ASCII
# ------------------------------------------------------------

ascii_rows = []

for y in range(rows):

    row = []

    for x in range(COLUMNS):

        brightness = image.getpixel((x, y))

        index = int(
            (255 - brightness)
            / 255
            * (len(RAMP) - 1)
        )

        row.append(RAMP[index])

    ascii_rows.append("".join(row))


# ------------------------------------------------------------
# SVG dimensions
# ------------------------------------------------------------

svg_width = COLUMNS * CHAR_WIDTH
svg_height = rows * CHAR_HEIGHT


svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{svg_width}"
height="{svg_height}"
viewBox="0 0 {svg_width} {svg_height}"
role="img"
aria-label="Animated ASCII portrait">
'''
)


# Background

svg.append(
    f'<rect width="100%" height="100%" '
    f'fill="{BACKGROUND}"/>\n'
)


# ------------------------------------------------------------
# Definitions
# ------------------------------------------------------------

svg.append("<defs>\n")


for y in range(rows):

    delay = y * ROW_DELAY

    svg.append(
        f'''
<clipPath id="clip-row-{y}">
    <rect
        x="0"
        y="{y * CHAR_HEIGHT}"
        width="0"
        height="{CHAR_HEIGHT}">
        <animate
            attributeName="width"
            from="0"
            to="{svg_width}"
            dur="{ROW_DURATION}s"
            begin="{delay:.3f}s"
            fill="freeze"/>
    </rect>
</clipPath>
'''
    )


svg.append("</defs>\n")


# ------------------------------------------------------------
# Render ASCII rows
# ------------------------------------------------------------

for y, row in enumerate(ascii_rows):

    # XML-safe text.
    safe_row = escape(row)

    y_position = (
        (y + 1) * CHAR_HEIGHT - 2
    )

    svg.append(
        f'''
<g clip-path="url(#clip-row-{y})">
    <text
        x="0"
        y="{y_position}"
        font-family="monospace"
        font-size="{CHAR_HEIGHT}px"
        font-weight="500"
        fill="{FOREGROUND}"
        xml:space="preserve">{safe_row}</text>
</g>
'''
    )


# ------------------------------------------------------------
# Final SVG
# ------------------------------------------------------------

svg.append("</svg>\n")


OUTPUT.write_text(
    "".join(svg),
    encoding="utf-8"
)


print()
print("======================================")
print("ASCII SVG generated successfully!")
print("======================================")
print(f"Output: {OUTPUT}")
print(f"Size:   {svg_width} × {svg_height}")
print(f"Rows:   {rows}")