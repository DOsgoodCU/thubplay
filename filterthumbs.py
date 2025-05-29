import pandas as pd

# Load CSV
df = pd.read_csv("dashboards.csv")

# Start HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Dashboard Links</title>
<style>
:root { --framewidth: 200px; --frameheight: 200px; --wrapperframeratiow2h: 2.00; --framemult: 7; }
.grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(var(--framewidth), 1fr)); gap: 10px; justify-content: center; padding: 10px; }
.iframe-wrapper { position: relative; width: var(--framewidth); height: var(--frameheight); overflow: hidden; display: inline-block; border: 1px solid black; border-radius: 8px; text-align: center; }
.iframe-wrapper iframe { width: calc(var(--framewidth) * var(--framemult)); height: calc(var(--framewidth) * var(--framemult) / var(--wrapperframeratiow2h)); transform: scale(0.3); transform-origin: top left; }
.clickable-overlay { position: absolute; width: 100%; height: 100%; top: 0; left: 0; z-index: 10; }
.iframe-title { position: absolute; top: 0; width: 100%; background-color: rgba(0, 0, 0, 0.7); color: white; text-align: center; padding: 5px; font-size: 16px; z-index: 15; }
.iframe-wrapper:hover { box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); transition: box-shadow 0.3s ease-in-out; }
</style>
<script>
function filterCards() {
    let country = document.getElementById("countryFilter").value.toLowerCase();
    let season = document.getElementById("seasonFilter").value.toLowerCase();
    let type = document.getElementById("typeFilter").value.toLowerCase();
    document.querySelectorAll(".iframe-wrapper").forEach(el => {
        let c = el.getAttribute("data-country").toLowerCase();
        let s = el.getAttribute("data-season").toLowerCase();
        let t = el.getAttribute("data-type").toLowerCase();
        el.style.display = (c.includes(country) && s.includes(season) && t.includes(type)) ? "inline-block" : "none";
    });
}
</script>
</head>
<body>
<h2>Filter</h2>
<input type="text" id="countryFilter" placeholder="Country" onkeyup="filterCards()">
<input type="text" id="seasonFilter" placeholder="Season" onkeyup="filterCards()">
<input type="text" id="typeFilter" placeholder="Type" onkeyup="filterCards()">
<div class="grid-container">
"""

# Add each iframe block
for _, row in df.iterrows():
    title = row["Title"]
    url = row["URL"]
    country = row["Country"]
    season = row["Season"]
    dtype = row["Type"]
    
    html += f"""
    <div class="iframe-wrapper" data-country="{country}" data-season="{season}" data-type="{dtype}">
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
with open("dashboards.html", "w", encoding="utf-8") as f:
    f.write(html)

