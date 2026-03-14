import feedparser
import time
import webbrowser
import os
import re
import urllib.request

# Keywords (whole words only) – unchanged
RAW_KEYWORDS = ["iran", "iranian", "tehran", "qom",
                "khamenei", "mojtabakhamenei", "ayatollah", "supreme leader", "president iran", "pezeshkian",
                "iran war", "israel iran", "us iran", "iran israel war", "iran attack", "iran strike", "iran missile", "iran drone",
                "idf iran", "centcom iran", "us strikes iran", "israel strikes iran", "hormuz blockade", "strait hormuz", "mine laying iran", "irgc", "revolutionary guard",
                "oil prices", "brent crude", "wti crude", "opec iran", "kharg island", "iran oil export", "oil tanker attack", "sanctions iran", "us sanctions iran",
                "regime change iran", "iran collapse", "iran revolution", "iran protest", "iran unrest", "mojta ba khamenei", "khamenei successor",
                "axis resistance", "hezbollah iran", "houthis iran", "iraq iran", "syria iran", "russia iran", "china iran",
                "nuclear iran", "uranium iran", "enrichment iran", "jcpoa", "snapback sanctions",
                "u.s."]
KEYWORDS = set()
for kw in RAW_KEYWORDS:
    KEYWORDS.update(word.lower() for word in kw.split())
KEYWORDS = list(KEYWORDS)

# All sources (used for both top & main feed)
ALL_SOURCES = [
    ("Global News", "https://news.google.com/rss/search?q=iran+OR+us+iran+OR+israel+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP via Google", "https://news.google.com/rss/search?q=site:apnews.com+iran+OR+us+iran+OR+israel+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters via Google", "https://news.google.com/rss/search?q=site:reuters.com+iran+OR+us+iran+OR+israel+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Times of Israel via Google", "https://news.google.com/rss/search?q=site:timesofisrael.com+iran+OR+israel+OR+gaza+OR+hezbollah+OR+hamas+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera via Google", "https://news.google.com/rss/search?q=site:aljazeera.com+iran+OR+israel+OR+gaza+OR+hezbollah+OR+hamas+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

# Both files go to Documents (safe, always works)
DOCS_FOLDER = os.path.join(os.path.expanduser("~"), "Documents")
NEWS_FEED_HTML = os.path.join(DOCS_FOLDER, "news_feed.html")
INDEX_HTML = os.path.join(DOCS_FOLDER, "index.html")

print("Sean Mitchell's Middle East News Bot Alpha 1.0 - Starting...")

# Collect all matches from every source
all_matches = []
seen = set()  # Deduplication

for source_name, url in ALL_SOURCES:
    count = 0
    for attempt in range(3):
        try:
            print(f"  Fetching {source_name} (attempt {attempt+1})...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
            if feed.bozo:
                break
            for entry in feed.entries:
                if count >= 20:
                    break
                title = entry.title.strip()
                title_lower = title.lower()
                link = entry.get('link', '#')
                
                dedup_key = (title_lower, link)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                
                if any(kw in title_lower for kw in KEYWORDS):
                    ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    ts = time.mktime(ts_struct) if ts_struct else time.time()
                    all_matches.append((ts, title, source_name, link))
                    count += 1
            break
        except Exception as e:
            print(f"    Attempt {attempt+1} failed: {str(e)}")
            time.sleep(2)

# Strict sort by timestamp (newest first)
all_matches.sort(reverse=True, key=lambda x: x[0])

print(f"Found {len(all_matches)} unique matching headlines after deduplication.")

# Generate HTML (your exact last working version)
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sean Mitchell's Middle East News Bot Alpha 1.0</title>
    <style>
        body { background: #000000; color: #ffffff; font-family: Arial, sans-serif; margin: 20px; line-height: 1.5; }
        h1 { color: #ffffff; margin-bottom: 10px; }
        .update { color: #aaaaaa; font-size: 0.9em; margin-bottom: 20px; }
        .section-title { color: #FF0000; font-size: 1.6em; margin: 30px 0 10px; font-weight: bold; }
        .top-divider { border: 0; height: 3px; background: #FF0000; margin: 25px 0 35px; }
        .headline { margin-bottom: 18px; padding-bottom: 10px; border-bottom: 1px solid #222222; }
        .title { color: #ffffff; }
        .keyword { color: #00FFFF; font-weight: bold; text-decoration: underline; }
        .link { color: #003300; text-decoration: none; margin-left: 10px; font-size: 0.9em; }
        .link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Sean Mitchell's Middle East News Bot Alpha 1.0</h1>
    <p class="update">Last updated at """ + time.strftime("%H:%M:%S") + """</p>

    <!-- Breaking News top section – top 20 most recent -->
    <h2 class="section-title">Breaking News</h2>
    <div id="top-feed">
"""

if all_matches:
    for ts, title, source, link in all_matches[:20]:
        highlighted_title = title
        for kw in RAW_KEYWORDS:
            if ' ' in kw:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        for kw in KEYWORDS:
            if ' ' not in kw and len(kw) > 2:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        html += f'<div class="headline"><span class="title">{highlighted_title}</span> <a class="link" href="{link}" target="_blank">[Read Article]</a></div>\n'
else:
    html += '<p>No breaking news available right now.</p>\n'

html += """
    </div>
    <hr class="top-divider">

    <!-- Main balanced feed – top 80 -->
    <h2 class="section-title">All Recent Headlines</h2>
    <div id="feed">
"""

if all_matches:
    for ts, title, source, link in all_matches[:80]:
        highlighted_title = title
        for kw in RAW_KEYWORDS:
            if ' ' in kw:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        for kw in KEYWORDS:
            if ' ' not in kw and len(kw) > 2:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        html += f'<div class="headline"><span class="title">{highlighted_title}</span> <a class="link" href="{link}" target="_blank">[Read Article]</a></div>\n'
else:
    html += '<p>No additional headlines right now.</p>\n'

html += """
    </div>
</body>
</html>
"""

# Write BOTH files to Documents (safe place)
try:
    with open(NEWS_FEED_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved news_feed.html to: {NEWS_FEED_HTML}")

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved index.html to: {INDEX_HTML}")
    print("You can now copy index.html from Documents to upload to GitHub.")
except Exception as e:
    print(f"Error saving files: {str(e)}")

# Open the news_feed.html in browser
file_url = f"file:///{NEWS_FEED_HTML.replace('\\', '/')}"
webbrowser.open_new_tab(file_url)
print("Opened news_feed.html in browser.")

print("\nDone. Press Enter to close.")
input()