from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT = Path("source-photo.jpg")
OUTPUT = Path("source-prepped.png")


# --------------------------------------------------
# Check input
# --------------------------------------------------

if not INPUT.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT}. "
        "Make sure source-photo.jpg is in the project folder."
    )


print("Reading photo...")
print(f"Input:  {INPUT}")


# --------------------------------------------------
# 1. Remove background
# --------------------------------------------------

print("Removing background...")
print("(The first run may download a rembg model.)")

input_image = Image.open(INPUT).convert("RGBA")

cutout = remove(input_image)

# Save temporary transparent cutout
cutout_path = Path("subject-cutout.png")
cutout.save(cutout_path)

print(f"Saved transparent subject: {cutout_path}")


# --------------------------------------------------
# 2. Composite subject onto white
# --------------------------------------------------

print("Creating white background...")

rgba = np.array(cutout)

rgb = rgba[:, :, :3]
alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0

white = np.full_like(rgb, 255)

composited = (
    rgb.astype(np.float32) * alpha
    + white.astype(np.float32) * (1.0 - alpha)
).astype(np.uint8)


# --------------------------------------------------
# 3. Convert to grayscale
# --------------------------------------------------

gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)


# --------------------------------------------------
# 4. Improve local contrast
# --------------------------------------------------

print("Improving contrast...")

clahe = cv2.createCLAHE(
    clipLimit=2.5,
    tileGridSize=(8, 8)
)

gray = clahe.apply(gray)


# --------------------------------------------------
# 5. Slightly increase contrast
# --------------------------------------------------

gray = cv2.normalize(
    gray,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)


# --------------------------------------------------
# 6. Save
# --------------------------------------------------

Image.fromarray(gray).save(OUTPUT)

print()
print("======================================")
print("Done!")
print("======================================")
print(f"Output: {OUTPUT}")
print()