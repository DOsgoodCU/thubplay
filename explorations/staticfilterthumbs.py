# example use:
# python filterthumbs.py --filter Country Mali Season JAS Type "Design Dashboard"
# Example output filename: country_mali_season_jas_type_designdashboard_dashboards.html
# python filterthumbs.py
# Output filename: all_dashboards.html
# python filterthumbs.py --filter Country Ethiopia --output my_ethiopia_report.html
# Output filename: my_ethiopia_report.html
# python filterthumbs.py --filter Country Ethiopia Season MAM,OND Type "Design Dashboard","Public Monitoring Dashboard"

#old, might still work, but might need tweaking
# python filterthumbs.py --filter Country Mali Season JAS Type "Design Dashboard", --output my_filtered_dashboards.html
# python filterthumbs.py --filter Country Ethiopia
# This will still generate filtered_dashboards.html
# python filterthumbs.py --filter Country Ethiopia Season MAM,OND --output ethiopia_mam_ond.html

import pandas as pd
import argparse
import sys
import re # Import regex module for cleaning filenames

# Load CSV
df = pd.read_csv("dashboards.csv")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate HTML dashboards based on filtered CSV data.")
parser.add_argument("--filter", nargs='*', help="Filter conditions as key-value pairs (e.g., --filter Country Mali Season JAS Type 'Design Dashboard'). For multiple values for a single column, use a comma-separated list (e.g., --filter Season JAS,OND).")
parser.add_argument("--output", help="Specify the output HTML filename (e.g., --output my_dashboards.html). If not specified, a filename will be generated based on filter criteria.")
args = parser.parse_args()

# Apply filters
filter_summary = [] # To build a summary for the default filename
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
            # Ensure the column in DataFrame is of string type for case-insensitive comparison if necessary
            df[column] = df[column].astype(str)
            # Filter rows where the column value is in the list of specified values (case-insensitive)
            df = df[df[column].str.lower().isin([v.lower() for v in values])]
        else:
            print(f"Warning: Column '{column}' not found in the CSV. Skipping this filter.")

# Determine the output filename
output_filename = args.output
if not output_filename: # If output was not explicitly provided
    if filter_summary:
        # Create a clean, snake_case filename from the filter summary
        base_name = "_".join(filter_summary)
        # Remove any characters that are not alphanumeric, underscore, or hyphen
        base_name = re.sub(r'[^\w-]', '', base_name)
        # Replace multiple underscores with a single one
        base_name = re.sub(r'__+', '_', base_name)
        # Trim leading/trailing underscores
        base_name = base_name.strip('_')
        output_filename = f"{base_name}_dashboards.html".lower()
    else:
        output_filename = "all_dashboards.html" # Default if no filters are applied

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
        .iframe-wrapper iframe {
            width: calc(var(--framewidth) * var(--framemult));
            height: calc(var(--framewidth) * var(--framemult) / var(--wrapperframeratiow2h));
            transform: scale(0.3);
            transform-origin: top left;
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
for _, row in df.iterrows():
    # Construct a meaningful title for the dashboard
    title_parts = []
    if pd.notna(row["Country"]):
        title_parts.append(row["Country"])
    if pd.notna(row["SubRegion"]):
        title_parts.append(row["SubRegion"])
    if pd.notna(row["Season"]):
        title_parts.append(row["Season"])
    if pd.notna(row["Type"]):
        title_parts.append(row["Type"])

    # Fallback if no specific parts are available to form a title
    if not title_parts:
        title = "Untitled Dashboard"
    else:
        title = " ".join(title_parts).strip()


    url = row["CU URL"] # Use the "CU URL" column for the link

    html += f"""
    <div class="iframe-wrapper">
        <div class="iframe-title">{title}</div>
        <a href="{url}" target="_blank" class="clickable-overlay"></a>
        <iframe src="{url}"></iframe>
    </div>
    """

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
