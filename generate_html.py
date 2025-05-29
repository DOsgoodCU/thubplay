import pandas as pd
import argparse
import fnmatch
import os

def matches(row, filters):
    for column, pattern in filters.items():
        value = str(row.get(column, ''))
        if not fnmatch.fnmatch(value, pattern):
            return False
    return True

def generate_html(df, output_file):
    with open(output_file, 'w') as f:
        f.write('<html><body>\n')
        f.write('<table style="border-collapse: collapse;"><tr>\n')
        for i, url in enumerate(df['CU URL']):
            f.write(f'<td style="padding: 10px;"><a href="{url}" target="_blank">'
                    f'<img src="{url}" width="320" height="180"></a></td>\n')
            if (i + 1) % 4 == 0:
                f.write('</tr><tr>\n')
        f.write('</tr></table>\n</body></html>')

def parse_filters(filter_args):
    filters = {}
    for f in filter_args:
        if '=' not in f:
            raise ValueError(f"Invalid filter format: {f}. Use COLUMN=VALUE (wildcards allowed).")
        key, value = f.split('=', 1)
        filters[key] = value
    return filters

def main():
    parser = argparse.ArgumentParser(description='Generate HTML from filtered dashboards CSV.')
    parser.add_argument('--csv', default='dashboards.csv', help='Path to the dashboards CSV file')
    parser.add_argument('--output', default='filtered_dashboards.html', help='Output HTML file')
    parser.add_argument('--filter', action='append', default=[], help='Filter in the format COLUMN=VALUE (wildcards allowed)')

    args = parser.parse_args()

    df = pd.read_csv(args.csv)

    filters = parse_filters(args.filter)
    filtered_df = df[df.apply(lambda row: matches(row, filters), axis=1)]

    if filtered_df.empty:
        print("No matching dashboards found.")
    else:
        generate_html(filtered_df, args.output)
        print(f"Generated HTML with {len(filtered_df)} entries: {args.output}")

if __name__ == '__main__':
    main()

