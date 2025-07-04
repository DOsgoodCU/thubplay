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
THUMBNAIL_BASE_DIR = "thumbnails" # Base directory for all thumbnail subfolders
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720
THUMBNAIL_CLIP_WIDTH = 200
THUMBNAIL_CLIP_HEIGHT = 200
PAGE_LOAD_WAIT_TIME = 20
POST_LOAD_SLEEP_TIME = 5

# Load CSV
df = pd.read_csv("dashboards.csv")
print(f"DEBUG: Initial DataFrame empty: {df.empty}, length: {len(df)}") # DEBUG PRINT

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
parser = argparse.ArgumentParser(description="Generate HTML dashboards based on filtered CSV data with cached, refreshed, or direct iframe content.")
parser.add_argument("--filter", nargs='*', help="Filter conditions as key-value pairs (e.g., --filter Country Mali Season JAS Type 'Design Dashboard'). For multiple values for a single column, use a comma-separated list (e.g., --filter Season JAS,OND).")
parser.add_argument("--output", help="Specify the output HTML filename (e.g., --output my_dashboards.html). If not specified, a filename will be generated based on filter criteria.")
parser.add_argument("--refresh-thumbnails", action="store_true", help="Force regeneration of all thumbnails, ignoring cached versions.")
# New command-line option for direct iframes
parser.add_argument("--direct-iframes", action="store_true", help="Generate HTML using iframes directly for all dashboards, skipping thumbnail generation/caching.")
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
            # Ensure column is string type for case-insensitive comparison
            df[column] = df[column].astype(str)
            df = df[df[column].str.lower().isin([v.lower() for v in values])]
        else:
            print(f"Warning: Column '{column}' not found in the CSV. Skipping this filter.")
    print(f"DEBUG: DataFrame empty after filters: {df.empty}, length: {len(df)}") # DEBUG PRINT
    if not df.empty:
        print(f"DEBUG: First 5 rows after filters:\n{df.head().to_string()}") # DEBUG PRINT
    else:
        print("DEBUG: No rows left after applying filters.")

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

# --- Add 'cached' to filename if cached option is used and not direct iframes ---
# 'cached' suffix implies that thumbnails are being used AND they are not forced to refresh
if not args.refresh_thumbnails and not args.direct_iframes:
    name, ext = os.path.splitext(output_filename)
    output_filename = f"{name}_cached{ext}"
    print(f"Using cached thumbnails. Output filename will be: {output_filename}")
elif args.direct_iframes:
    # If direct iframes are used, no cached suffix is relevant
    print("Generating HTML with direct iframe embeds (no thumbnails).")
else: # args.refresh_thumbnails is True
    print("Generating HTML with refreshed thumbnails.")

# --- Define unique thumbnail directory for this run ---
# Example: "all_dashboards_cached.html" -> "thumbnails/all_dashboards_cached/"
thumbnail_subdir_name = os.path.splitext(output_filename)[0]
CURRENT_THUMBNAIL_DIR = os.path.join(THUMBNAIL_BASE_DIR, thumbnail_subdir_name)
print(f"DEBUG: Thumbnails will be stored in: {os.path.abspath(CURRENT_THUMBNAIL_DIR)}") # DEBUG PRINT

# --- Thumbnail Generation Logic ---
# Ensure unique thumbnail subdirectory exists only if we are using thumbnails
if not args.direct_iframes:
    if not os.path.exists(CURRENT_THUMBNAIL_DIR):
        os.makedirs(CURRENT_THUMBNAIL_DIR)
        print(f"DEBUG: Created thumbnail directory: {CURRENT_THUMBNAIL_DIR}") # DEBUG PRINT
    else:
        print(f"DEBUG: Thumbnail directory already exists: {CURRENT_THUMBNAIL_DIR}") # DEBUG PRINT

# Setup Selenium WebDriver in headless mode if needed for thumbnail generation
# Driver is only initialized if we are NOT in direct-iframes mode AND
# either a refresh is forced OR some thumbnails are missing
driver = None
if not args.direct_iframes and df["CU URL"].any():
    should_initialize_driver = args.refresh_thumbnails
    if not should_initialize_driver: # If not forced refresh, check if any thumbnail is missing
        for _, row in df.iterrows():
            url = row["CU URL"] if "CU URL" in df.columns and pd.notna(row["CU URL"]) else None
            if url and url != "#":
                url_hash = hashlib.md5(str(url).encode('utf-8')).hexdigest()
                # Use CURRENT_THUMBNAIL_DIR for checking existence
                thumbnail_path = os.path.join(CURRENT_THUMBNAIL_DIR, f"{url_hash}.png")
                if not os.path.exists(thumbnail_path):
                    should_initialize_driver = True
                    break # Found a missing thumbnail, so driver is needed

    if should_initialize_driver:
        print("Initializing headless browser for thumbnail generation...")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument(f"--window-size={THUMBNAIL_WIDTH},{THUMBNAIL_HEIGHT}")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            print("Browser initialized.")
        except Exception as e:
            print(f"Error initializing browser: {e}")
            print("Thumbnails will NOT be generated. HTML will use iframes directly if CU URL exists.")
            driver = None # Set driver to None if initialization fails

# Start HTML
html = """<!DOCTYPE HTML>
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
        /* Style for thumbnail images to match scaled iframes */
        .thumbnail-image {
            width: calc(var(--framewidth) * var(--framemult));
            height: calc(var(--framewidth) * var(--framemult) / var(--wrapperframeratiow2h));
            transform: scale(0.3);
            transform-origin: top left;
            display: block;
            /* object-fit: cover; -- You can uncomment this if you prefer the image to cover the scaled area,
                                  -- but it might crop if aspect ratios differ significantly after scaling. */
        }
        /* Style for iframes inside iframe-wrapper (used for direct iframes and fallbacks) */
        .iframe-wrapper iframe {
            width: calc(var(--framewidth) * var(--framemult));
            height: calc(var(--framewidth) * var(--framemult) / var(--wrapperframeratiow2h));
            transform: scale(0.3);
            transform-origin: top left;
            border: none; /* Keep border none for a cleaner look */
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
if df.empty:
    print("DEBUG: DataFrame is empty, no dashboard blocks will be added.") # DEBUG PRINT
else:
    for index, row in df.iterrows():
        # --- Title Generation Logic ---
        title = ""
        # Check if 'Title' column exists and is not blank
        if "Title" in df.columns and pd.notna(row["Title"]) and str(row["Title"]).strip() != '':
            title = str(row["Title"]).strip()
        else:
            # Fallback to dynamic generation if 'Title' column is absent or blank
            title_parts = []
            for col in df.columns:
                if col not in EXCLUDE_FROM_TITLE_COLUMNS and pd.notna(row[col]) and str(row[col]).strip() != '':
                    title_parts.append(str(row[col]).strip())

            if not title_parts:
                title = "Untitled Dashboard"
            else:
                title = " ".join(title_parts).strip()

        url = row["CU URL"] if "CU URL" in df.columns and pd.notna(row["CU URL"]) else "#"

        display_content = ""
        if args.direct_iframes:
            # Mode: Direct Iframes with old scaling formatting
            if url != '#':
                display_content = f'<iframe src="{url}"></iframe>'
            else:
                display_content = '<div style="background-color:#ccc; color:#666; width:100%; height:100%; display:flex; align-items:center; justify-content:center;">No Content</div>'
        else:
            # Mode: Thumbnails (cached or refreshed)
            thumbnail_src = ""
            # Use CURRENT_THUMBNAIL_DIR for saving/loading thumbnails
            if driver and url != "#": # Only try to generate if driver is initialized and URL is valid
                url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
                thumbnail_filename = f"{url_hash}.png"
                thumbnail_path = os.path.join(CURRENT_THUMBNAIL_DIR, thumbnail_filename)

                if args.refresh_thumbnails or not os.path.exists(thumbnail_path):
                    try:
                        print(f"DEBUG: Generating thumbnail for: {url}") # DEBUG PRINT
                        driver.get(url)
                        WebDriverWait(driver, PAGE_LOAD_WAIT_TIME).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        time.sleep(POST_LOAD_SLEEP_TIME)

                        driver.save_screenshot(thumbnail_path)
                        print(f"DEBUG: Thumbnail saved: {thumbnail_path}") # DEBUG PRINT

                    except Exception as e:
                        print(f"ERROR: Could not generate thumbnail for {url}: {e}") # DEBUG PRINT
                        thumbnail_path = None
                
                if thumbnail_path and os.path.exists(thumbnail_path):
                    # CORRECTED: Use THUMBNAIL_BASE_DIR AND thumbnail_subdir_name for the HTML src attribute to make it relative to the HTML file
                    thumbnail_src = os.path.join(THUMBNAIL_BASE_DIR, thumbnail_subdir_name, thumbnail_filename)
                    print(f"DEBUG: Thumbnail SRC in HTML will be: {thumbnail_src}") # DEBUG PRINT
            
            if thumbnail_src:
                display_content = f'<img src="{thumbnail_src}" alt="{title}" class="thumbnail-image">'
            elif url != '#':
                print(f"DEBUG: Falling back to iframe for {url} due to missing/failed thumbnail or driver issue.") # DEBUG PRINT
                display_content = f'<iframe src="{url}"></iframe>' # Fallback uses direct iframe without extra class
            else:
                display_content = '<div style="background-color:#ccc; color:#666; width:100%; height:100%; display:flex; align-items:center; justify-content:center;">No Content</div>'

        print(f"DEBUG: Processing row {index}, Title: '{title}', URL: '{url}'. Display content starts with: '{display_content[:50]}...'") # DEBUG PRINT
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
print(f"DEBUG: HTML content length before writing: {len(html)}") # DEBUG PRINT
if len(html) < 200: # A very rough check for "empty" content beyond boilerplate
    print("WARNING: Generated HTML content appears unusually short, it might be empty or nearly empty.") # DEBUG PRINT

try:
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {output_filename}")
except Exception as e:
    print(f"ERROR: Could not write HTML file {output_filename}: {e}") # DEBUG PRINT
