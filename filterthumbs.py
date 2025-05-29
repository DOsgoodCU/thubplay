import pandas as pd
import sys

# Load CSV
df = pd.read_csv("dashboards.csv")

# --- USER CONFIGURATION START ---
# Define your filters here.
# For a single value: "Column Name": "Value"
# For multiple values: "Column Name": ["Value1", "Value2"]
# Example:
filters = {
    "Type": "Design Dashboard",
     "Country": ["Ethiopia", "Niger"],
     "Season": ["MAM", "OND", "JAS"]
}
# --- USER CONFIGURATION END ---

# Apply filters
if filters:
    for column, values in filters.items():
        # Ensure values is always a list for consistent iteration
        if not isinstance(values, list):
            values = [values]

        if column in df.columns:
            # Ensure the column in DataFrame is of string type for case-insensitive comparison if necessary
            df[column] = df[column].astype(str)
            # Filter rows where the column value is in the list of specified values (case-insensitive)
            df = df[df[column].str.lower().isin([str(v).lower() for v in values])]
        else:
            print(f"Warning: Column '{column}' not found in the CSV. Skipping this filter.")

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
    if pd.notna(row["SubRegion (if applicable)"]):
        title_parts.append(row["SubRegion (if applicable)"])
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

# Save to file
with open("filtered_dashboards.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Generated filtered_dashboards.html")
