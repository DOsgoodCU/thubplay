# How to Generate HTML with Live vs. Cached Dashboard Data

You can control how the HTML is generated, including whether it uses live URLs directly or cached thumbnail images, using specific command-line options.

---

### 1. Generate HTML with Live Versions of URLs (Direct Iframes)

This option makes the generated HTML directly embed each dashboard using an `<iframe>` tag. This means no thumbnail images are generated or used. Every time the HTML page is opened, your browser will fetch and render the live content of each dashboard URL.

* **When to Use:** When you want to ensure users always see the most current version of the dashboards, or if you encounter issues with thumbnail generation.
* **Command:** Include the `--direct-iframes` flag.
    ```bash
    python filterthumbs.py --direct-iframes [your other filter/output options]
    ```
* **Example Usage:**
    ```bash
    python filterthumbs.py --direct-iframes --output live_dashboards.html
    ```
* **HTML Filename:** The output filename will **not** include `_cached`. For example:
    * If you specify `--output my_dashboards.html`, it will be `my_dashboards.html`.
    * If you don't specify an output name (e.g., `python filterthumbs.py --direct-iframes`), it will be `all_dashboards.html` (or a filter-based name like `country_mali_season_jas_dashboards.html`).

---

### 2. Generate HTML with Cached Versions of URLs (Thumbnails)

This is the default behavior when you do not specify either `--direct-iframes` or `--refresh-thumbnails`. The script will use a headless browser to take screenshots of your dashboard URLs, save these screenshots as thumbnail images in the `thumbnails/` folder, and then embed these images in the HTML.

* **How it Works:**
    * For each dashboard URL, the script first checks if a thumbnail image already exists in the `thumbnails/` directory.
    * If a cached thumbnail is found, it will use that image directly in the HTML.
    * If a thumbnail does not exist (or if it was not successfully generated in a previous run), a new one will be generated and saved for future use.
* **When to Use:** When you want faster loading times for your HTML page, as it displays static images initially, while still allowing users to click on them to open the live dashboards in a new browser tab.
* **Command:** Simply run the script without `--direct-iframes` or `--refresh-thumbnails`.
    ```bash
    python filterthumbs.py [your other filter/output options]
    ```
* **Example Usage:**
    ```bash
    python filterthumbs.py --output my_report.html
    ```
* **HTML Filename:** The output filename will have `_cached` appended before the `.html` extension. For example: `my_report_cached.html` or `all_dashboards_cached.html`.

---

### 3. Generate HTML with Forced Refresh of Thumbnails

This option is used when you want to regenerate *all* thumbnail images, even if cached versions already exist. This is particularly useful if the content of your dashboards has changed and you need to ensure the thumbnails in your HTML are completely up-to-date.

* **When to Use:** When your dashboard content has been updated and you need the thumbnails to reflect the latest state.
* **Command:** Include the `--refresh-thumbnails` flag (and ensure `--direct-iframes` is *not* included).
    ```bash
    python filterthumbs.py --refresh-thumbnails [your other filter/output options]
    ```
* **Example Usage:**
    ```bash
    python filterthumbs.py --refresh-thumbnails --output updated_thumbs.html
    ```
* **HTML Filename:** The output filename will **not** include `_cached`. For example: `updated_thumbs.html` or `all_dashboards.html`.

---

### Summary of Filename Differences

| Command Line Option(s)          | Content in Generated HTML           | Filename Suffix |
| :------------------------------ | :---------------------------------- | :-------------- |
| (None)                          | Cached Thumbnails (if available, otherwise generated) | `_cached`       |
| `--refresh-thumbnails`          | Freshly Generated Thumbnails      | (None)          |
| `--direct-iframes`              | Live Iframes (No Thumbnails)      | (None)          |

* ** More Examples From old Versions that probably dont completely work **
python filterthumbs.py --filter Country Mali Season JAS Type "Design Dashboard"
Example output filename: country_mali_season_jas_type_designdashboard_dashboards.html

python filterthumbs.py
Output filename: all_dashboards.html

python filterthumbs.py --filter Country Ethiopia --output my_ethiopia_report.html
Output filename: my_ethiopia_report.html

python filterthumbs.py --filter Country Ethiopia Season MAM,OND Type "Design Dashboard","Public Monitoring Dashboard"

python filterthumbs.py --filter Country Mali Season JAS Type "Design Dashboard", --output my_filtered_dashboards.html
python filterthumbs.py --filter Country Ethiopia

This will still generate filtered_dashboards.html
python filterthumbs.py --filter Country Ethiopia Season MAM,OND --output ethiopia_mam_ond.html

