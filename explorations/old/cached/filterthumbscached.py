import pandas as pd
import argparse
import sys
import re
import os
import hashlib
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration for Thumbnails ---
THUMBNAIL_DIR = "thumbnails"
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720
THUMBNAIL_CLIP_WIDTH = 200
THUMBNAIL_CLIP_HEIGHT = 200
PAGE_LOAD_WAIT_TIME = 20
POST_LOAD_SLEEP_TIME = 5

# Load CSV
df = pd.read_csv("dashboards.csv")

# Define columns to EXCLUDE from the dynamic thumbnail title
EXCLUDE_FROM_TITLE_COLUMNS = [
    "CU URL",
    "Local Host URL",
    "Comment",
    "Draft or released",
    "Inactive (I)",
    "Specific date?",
    "Behind VPN?",
    "User",
    "Password"
]

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate HTML dashboards based on filtered CSV data with cached thumbnails.")
parser.add_argument("--filter", nargs='*', help="Filter conditions as key-value pairs (e.g., --filter Country Mali Season JAS Type 'Design Dashboard'). For multiple values for a single column, use a comma-separated list (e.g., --filter Season JAS,OND).")
parser.add_argument("--output", help="Specify the output HTML filename (e.g., --output my_dashboards.html). If not specified, a filename will be generated based on filter criteria.")
args = parser.parse_args()

# Apply filters
filter_summary = []
if args.filter:
    filter_dict = {}
    it = iter(args.filter)
    for x in it:
        try:
            key = x
            value = next(it)
            if ',' in value:
                filter_dict[key] = value.split(',')
                filter_summary.append(f"{key}_{'_'.join(value.split(','))}")
            else:
                filter_dict[key] = [value]
                filter_summary.append(f"{key}_{value}")
        except StopIteration:
            print(f"Warning: Missing value for filter key '{x}'. Skipping.")
            break

    for column, values in filter_dict.items():
        if column in df.columns:
            df[column] = df[column].astype(str)
            df = df[df[column].str.lower().isin([v.lower() for v in values])]
        else:
            print(f"Warning: Column '{column}' not found in the CSV. Skipping this filter.")

# Determine the output filename
output_filename = args.output
if not output_filename:
    if filter_summary:
        base_name = "_".join(filter_summary)
        base_name = re.sub(r'[^\w-]', '', base_name)
        base_name = re.sub(r'__+', '_', base_name)
        base_name = base_name.strip('_')
        output_filename = f"{base_name}_dashboards.html".lower()
    else:
        output_filename = "all_dashboards.html"

# --- Thumbnail Generation Logic ---
# Ensure thumbnail directory exists
if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

# Setup Selenium WebDriver in headless mode
print("Initializing headless browser for thumbnail generation...")
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument(f"--window-size={THUMBNAIL_WIDTH},{THUMBNAIL_HEIGHT}")
options.add_argument("--hide-scrollbars")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = None
try:
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    print("Browser initialized.")
except Exception as e:
    print(f"Error initializing browser: {e}")
    print("Thumbnails will NOT be generated. HTML will use iframes directly if CU URL exists.")

# Start HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Links</title>
    <style>
        :root {
            --framewidth: 200px;
            --frameheight: 200px;
            --wrapperframeratiow2h: 2.00;
            --framemult: 7;
        }

        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(var(--framewidth), 1fr));
            gap: 10px;
            justify-content: center;
            padding: 10px;
        }
        .iframe-wrapper {
            position: relative;
            width: var(--framewidth);
            height: var(--frameheight);
            overflow: hidden;
            display: inline-block;
            border: 1px solid black;
            border-radius: 8px;
            text-align: center;
        }
        .thumbnail-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .clickable-overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: 10;
        }
        .iframe-title {
            position: absolute;
            top: 0;
            width: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            text-align: center;
            padding: 5px;
            font-size: 16px;
            z-index: 15;
        }
        .iframe-wrapper:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: box-shadow 0.3s ease-in-out;
        }
    </style>
</head>
<body>
<div class="grid-container">
"""

# Add each iframe block for filtered rows
for index, row in df.iterrows():
    title_parts = []
    for col in df.columns:
        if col not in EXCLUDE_FROM_TITLE_COLUMNS and pd.notna(row[col]) and str(row[col]).strip() != '':
            title_parts.append(str(row[col]).strip())

    if not title_parts:
        title = "Untitled Dashboard"
    else:
        title = " ".join(title_parts).strip()

    url = row["CU URL"] if "CU URL" in df.columns and pd.notna(row["CU URL"]) else "#"

    thumbnail_src = ""
    if driver and url != "#":
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        thumbnail_filename = f"{url_hash}.png"
        thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)

        # Removed the 'if not os.path.exists(thumbnail_path):' check
        # This forces regeneration of all thumbnails every time the script runs
        try:
            print(f"Generating thumbnail for: {url}")
            driver.get(url)
            WebDriverWait(driver, PAGE_LOAD_WAIT_TIME).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(POST_LOAD_SLEEP_TIME)

            driver.save_screenshot(thumbnail_path)
            print(f"Thumbnail saved: {thumbnail_path}")

        except Exception as e:
            print(f"Could not generate thumbnail for {url}: {e}")
            thumbnail_path = None
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            thumbnail_src = thumbnail_path
    
    if thumbnail_src:
        display_content = f'<img src="{thumbnail_src}" alt="{title}" class="thumbnail-image">'
    elif url != '#':
        print(f"Falling back to iframe for {url} due to missing/failed thumbnail.")
        display_content = f'<iframe src="{url}"></iframe>'
    else:
        display_content = '<div style="background-color:#ccc; color:#666; width:100%; height:100%; display:flex; align-items:center; justify-content:center;">No Content</div>'


    html += f"""
    <div class="iframe-wrapper">
        <div class="iframe-title">{title}</div>
        <a href="{url}" target="_blank" class="clickable-overlay"></a>
        {display_content}
    </div>
    """

# Close WebDriver
if driver:
    print("Closing browser.")
    driver.quit()

# Close HTML
html += """
</div>
</body>
</html>
"""

# Save to file using the determined filename
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Generated {output_filename}")
