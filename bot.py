import feedparser
import time
import os
import re
import urllib.request
from datetime import datetime

print("Starting bot...")

# Save to CURRENT DIRECTORY (repo root in GitHub Actions, Desktop folder locally)
CURRENT_DIR = os.getcwd()
print(f"Saving files to current directory: {CURRENT_DIR}")

NEWS_FEED_HTML = os.path.join(CURRENT_DIR, "news_feed.html")
INDEX_HTML = os.path.join(CURRENT_DIR, "index.html")

# ====================== MIDDLE EAST KEYWORDS ======================
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

# ====================== US POLITICS KEYWORDS ======================
RAW_US_KEYWORDS = ["donald trump", "jd vance", "marco rubio", "kamala harris", "gavin newsom", 
                   "steve hilton", "joe biden", "alexandria ocasio-cortez", "nancy pelosi"]
US_KEYWORDS = set()
for kw in RAW_US_KEYWORDS:
    US_KEYWORDS.update(word.lower() for word in kw.split())
US_KEYWORDS = list(US_KEYWORDS)

# Sources (same for both sections)
ALL_SOURCES = [
    ("Global News", "https://news.google.com/rss/search?q=iran+OR+us+iran+OR+israel+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP via Google", "https://news.google.com/rss/search?q=site:apnews.com+iran+OR+us+iran+OR+israel+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters via Google", "https://news.google.com/rss/search?q=site:reuters.com+iran+OR+us+iran+OR+israel+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Times of Israel via Google", "https://news.google.com/rss/search?q=site:timesofisrael.com+iran+OR+israel+OR+gaza+OR+hezbollah+OR+hamas+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera via Google", "https://news.google.com/rss/search?q=site:aljazeera.com+iran+OR+israel+OR+gaza+OR+hezbollah+OR+hamas+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== FETCH MIDDLE EAST ======================
middle_matches = []
seen = set()
for source_name, url in ALL_SOURCES:
    for attempt in range(3):
        try:
            print(f"  Fetching {source_name} (Middle East)...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
            if feed.bozo: break
            for entry in feed.entries:
                title = entry.title.strip()
                title_lower = title.lower()
                link = entry.get('link', '#')
                dedup_key = (title_lower, link)
                if dedup_key in seen: continue
                seen.add(dedup_key)
                if any(kw in title_lower for kw in KEYWORDS):
                    ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    ts = time.mktime(ts_struct) if ts_struct else time.time()
                    middle_matches.append((ts, title, source_name, link))
            break
        except Exception as e:
            print(f"    Attempt {attempt+1} failed: {str(e)}")
            time.sleep(2)

middle_matches.sort(reverse=True, key=lambda x: x[0])

# Time split for Middle East
current_ts = time.time()
six_hours_ago = current_ts - 21600
middle_breaking = [item for item in middle_matches if item[0] >= six_hours_ago][:20]
middle_recent = [item for item in middle_matches if item not in middle_breaking][:20]

# ====================== FETCH US POLITICS ======================
us_matches = []
seen_us = set()
for source_name, url in ALL_SOURCES:
    for attempt in range(3):
        try:
            print(f"  Fetching {source_name} (US Politics)...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
            if feed.bozo: break
            for entry in feed.entries:
                title = entry.title.strip()
                title_lower = title.lower()
                link = entry.get('link', '#')
                dedup_key = (title_lower, link)
                if dedup_key in seen_us: continue
                seen_us.add(dedup_key)
                if any(kw in title_lower for kw in US_KEYWORDS):
                    ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    ts = time.mktime(ts_struct) if ts_struct else time.time()
                    us_matches.append((ts, title, source_name, link))
            break
        except Exception as e:
            print(f"    Attempt {attempt+1} failed: {str(e)}")
            time.sleep(2)

us_matches.sort(reverse=True, key=lambda x: x[0])

# Time split for US Politics
us_breaking = [item for item in us_matches if item[0] >= six_hours_ago][:20]
us_recent = [item for item in us_matches if item not in us_breaking][:20]

# ====================== BUILD HTML ======================
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Mitchell Post</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        body { background: #121212; color: #FFFFFF; font-family: Arial, sans-serif; margin: 20px; line-height: 1.5; }
        h1 { color: #FFFFFF; margin-bottom: 5px; text-decoration: underline; }
        .byline { color: #aaaaaa; font-size: 1.1em; margin-bottom: 30px; }
        .update { color: #aaaaaa; font-size: 0.9em; margin-bottom: 20px; }
        .section-title { color: #FF0000; font-size: 1.6em; margin: 30px 0 10px; font-weight: bold; text-decoration: underline; text-decoration-color: #FFFFFF; }
        .top-divider { border: 0; height: 3px; background: #FF0000; margin: 25px 0 35px; }
        .headline { margin-bottom: 18px; padding-bottom: 10px; border-bottom: 1px solid #222222; }
        .title { color: #FFFFFF; }
        .keyword { color: #F6CB2F; font-weight: bold; }
        .link { color: #B0B0B0; text-decoration: none; margin-left: 10px; font-size: 0.9em; }
        .link:hover { text-decoration: underline; }

        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .column { flex: 1; min-width: 300px; }
        @media (max-width: 768px) { .container { flex-direction: column; } }
    </style>
</head>
<body>
    <h1>The Mitchell Post</h1>
    <p class="byline">By Sean Mitchell</p>
    <p class="update">Last updated at """ + datetime.utcnow().strftime("%H:%M:%S UTC") + """ (auto-refreshes every few hours)</p>

    <!-- ====================== MIDDLE EAST SECTION ====================== -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Middle East Breaking News</h2>
            <div id="middle-breaking">
"""

if middle_breaking:
    for ts, title, source, link in middle_breaking:
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
    html += '<p>No breaking news in the last 6 hours.</p>\n'

html += """
            </div>
        </div>

        <div class="column">
            <h2 class="section-title">Middle East Headlines</h2>
            <div id="middle-recent">
"""

if middle_recent:
    for ts, title, source, link in middle_recent:
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
        </div>
    </div>

    <hr class="top-divider">

    <!-- ====================== US POLITICS SECTION ====================== -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">US Politics Breaking News</h2>
            <div id="us-breaking">
"""

if us_breaking:
    for ts, title, source, link in us_breaking:
        highlighted_title = title
        for kw in RAW_US_KEYWORDS:
            if ' ' in kw:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        for kw in US_KEYWORDS:
            if ' ' not in kw and len(kw) > 2:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        html += f'<div class="headline"><span class="title">{highlighted_title}</span> <a class="link" href="{link}" target="_blank">[Read Article]</a></div>\n'
else:
    html += '<p>No breaking US politics news in the last 6 hours.</p>\n'

html += """
            </div>
        </div>

        <div class="column">
            <h2 class="section-title">US Politics Headlines</h2>
            <div id="us-recent">
"""

if us_recent:
    for ts, title, source, link in us_recent:
        highlighted_title = title
        for kw in RAW_US_KEYWORDS:
            if ' ' in kw:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        for kw in US_KEYWORDS:
            if ' ' not in kw and len(kw) > 2:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span class="keyword">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        html += f'<div class="headline"><span class="title">{highlighted_title}</span> <a class="link" href="{link}" target="_blank">[Read Article]</a></div>\n'
else:
    html += '<p>No additional US politics headlines right now.</p>\n'

html += """
            </div>
        </div>
    </div>
</body>
</html>
"""

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
print("Files saved to current directory.")