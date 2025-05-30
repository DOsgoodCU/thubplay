def generate_html(df, output_file):
    with open(output_file, 'w') as f:
        f.write("""<!DOCTYPE html>
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
""")
        for _, row in df.iterrows():
            title = row.get('Title', 'Dashboard')  # You may need to change 'Title' to the actual column name
            url = row['url'] if 'url' in row else row['URL']
            f.write(f"""
    <div class="iframe-wrapper">
        <div class="iframe-title">{title}</div>
        <a href="{url}" target="_blank" class="clickable-overlay"></a>
        <iframe src="{url}"></iframe>
    </div>
""")
        f.write("</body>\n</html>")

