import feedparser
import time
import os
import re
import urllib.request
from datetime import datetime

print("Starting bot...")

# === Dedicated folder (change only if you move the folder) ===
NEWS_FOLDER = r"C:\Users\mitch\OneDrive\Desktop\News Automation Folder"
os.makedirs(NEWS_FOLDER, exist_ok=True)
NEWS_FEED_HTML = os.path.join(NEWS_FOLDER, "news_feed.html")
INDEX_HTML = os.path.join(NEWS_FOLDER, "index.html")

# Keywords (whole words only) – unchanged from your last working version
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

# Sources (Google News workarounds only) – unchanged
SOURCES = [
    ("Global News", "https://news.google.com/rss/search?q=iran+OR+us+iran+OR+israel+iran+OR+hormuz+OR+khamenei+OR+hezbollah+OR+houthis&hl=en-US&gl=US&ceid=US:en"),
    ("AP via Google", "https://news.google.com/rss/search?q=site:apnews.com+iran&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters via Google", "https://news.google.com/rss/search?q=site:reuters.com+iran&hl=en-US&gl=US&ceid=US:en"),
    ("Times of Israel via Google", "https://news.google.com/rss/search?q=site:timesofisrael.com+iran&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera via Google", "https://news.google.com/rss/search?q=site:aljazeera.com+iran&hl=en-US&gl=US&ceid=US:en"),
]

matches = []
seen = set()
for source_name, url in SOURCES:
    for attempt in range(3):
        try:
            print(f"  Fetching {source_name}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
            for entry in feed.entries:
                title_lower = entry.title.lower()
                link = entry.link
                if any(kw in title_lower for kw in KEYWORDS) and (title_lower, link) not in seen:
                    seen.add((title_lower, link))
                    parsed = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)
                    ts = time.mktime(parsed) if parsed else time.time()
                    matches.append((ts, entry.title, source_name, link))
            break
        except Exception as e:
            print(f"    Attempt {attempt+1} failed: {e}")
            time.sleep(2)

matches.sort(reverse=True)

# === Build HTML with cache-busting and UTC time ===
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sean Mitchell's Middle East News Bot Alpha 1.0</title>
    <meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="pragma" content="no-cache">
    <meta http-equiv="expires" content="0">
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
    <p class="update">Updated at """ + datetime.utcnow().strftime("%H:%M:%S UTC") + """ (auto-refreshes every 5 min)</p>
    <hr class="top-divider">
    <h2 class="section-title">Breaking News</h2>
    <div id="breaking">
"""

# Top 20 Breaking News
for ts, title, source, link in matches[:20]:
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

html += """
    </div>
    <hr class="top-divider">
    <h2 class="section-title">All Recent Headlines</h2>
    <div id="feed">
"""

# Bottom 80
for ts, title, source, link in matches[:80]:
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

html += """
    </div>
</body>
</html>
"""

# Save both files
try:
    with open(NEWS_FEED_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"SUCCESS: news_feed.html saved to {NEWS_FEED_HTML}")
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"SUCCESS: index.html saved to {INDEX_HTML}")
except Exception as e:
    print(f"ERROR saving files: {str(e)}")

print("\nScript finished.")
print("Both files are in your News Automation Folder.")