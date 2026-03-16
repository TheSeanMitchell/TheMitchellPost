import feedparser
import time
import os
import re
import urllib.request
from datetime import datetime

print("Starting bot...")

CURRENT_DIR = os.getcwd()
print(f"Saving files to current directory: {CURRENT_DIR}")

INDEX_HTML = os.path.join(CURRENT_DIR, "index.html")

# ====================== KEYWORDS ======================
# Middle East (your full list)
RAW_ME_KEYWORDS = [
    "middle east", "arab world", "gulf states", "gcc countries", "levant region", "maghreb region", "mena region",
    "persian gulf", "arabian peninsula", "west asia", "red sea region", "iran", "iranian", "tehran", "qom", "mashhad",
    "isfahan", "tabriz", "khuzestan", "israel", "israeli", "jerusalem", "tel aviv", "west bank", "gaza strip",
    "golan heights", "saudi arabia", "saudi", "riyadh", "jeddah", "neom", "vision 2030", "united arab emirates",
    "uae", "emirates", "abu dhabi", "dubai", "sharjah", "qatar", "doha", "kuwait", "oman", "bahrain", "iraq", "syria",
    "lebanon", "jordan", "turkey", "egypt", "yemen", "palestine", "khamenei", "mojtabakhamenei", "ayatollah",
    "supreme leader iran", "president iran", "pezeshkian", "netanyahu", "mohammed bin salman", "mbs", "mohammed bin zayed",
    "mbz", "erdogan", "el sisi", "tamim bin hamad", "king abdullah jordan", "bashar al assad", "hezbollah", "hamas",
    "irgc", "houthis", "pmf iraq", "isis", "gaza war", "israel gaza war", "gaza ceasefire", "israel lebanon conflict",
    "yemen civil war", "red sea crisis", "syria civil war", "idlib offensive", "iran proxy network", "axis of resistance",
    "iran nuclear program", "jcpoa", "snapback sanctions", "hormuz blockade", "strait hormuz", "oil prices", "brent crude",
    "wti crude", "opec", "kharg island", "iran oil exports", "us centcom", "russia syria", "china iran", "abraham accords",
    "saudi israel normalization", "iran protest", "iran unrest", "middle east war", "regional escalation", "proxy war",
    "missile defense israel", "iron dome", "neom", "qatar world cup legacy", "middle east infrastructure", "refugee crisis",
    "gaza humanitarian crisis", "yemen famine", "climate change middle east"
]
ME_KEYWORDS = set(word.lower() for kw in RAW_ME_KEYWORDS for word in kw.split())

# US Politics (unchanged)
RAW_US_KEYWORDS = ["donald trump", "jd vance", "marco rubio", "kamala harris", "gavin newsom", "steve hilton", "joe biden",
                   "alexandria ocasio-cortez", "nancy pelosi"]
US_KEYWORDS = set(word.lower() for kw in RAW_US_KEYWORDS for word in kw.split())

# Sports (unchanged)
RAW_SPORTS_KEYWORDS = ["march madness", "college basketball", "arizona wildcats", "purdue boilermakers", "miami hurricanes",
                       "villanova wildcats", "utah state aggies"]
SPORTS_KEYWORDS = set(word.lower() for kw in RAW_SPORTS_KEYWORDS for word in kw.split())

# ====================== SOURCES (broadened queries) ======================
MIDDLE_EAST_SOURCES = [
    ("Global & Analysis", "https://news.google.com/rss/search?q=middle+east+OR+iran+OR+israel+OR+gulf+OR+hezbollah+OR+hamas+OR+saudi+OR+uae+OR+qatar+OR+syria+OR+lebanon+OR+foreign+affairs+OR+carnegie+OR+atlantic+council+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters & AP", "https://news.google.com/rss/search?q=when:1d+site:reuters.com+OR+site:apnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("FT, Economist, WSJ, NYT", "https://news.google.com/rss/search?q=when:1d+site:ft.com+OR+site:economist.com+OR+site:wsj.com+OR+site:nytimes.com+middle+east+OR+iran+OR+gulf&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera & Regional", "https://news.google.com/rss/search?q=when:1d+site:aljazeera.com+OR+site:timesofisrael.com+OR+site:arabnews.com+OR+site:thenationalnews.com+iran+OR+israel+OR+gulf&hl=en-US&gl=US&ceid=US:en"),
]

US_POLITICS_SOURCES = [
    ("US Politics & Analysis", "https://news.google.com/rss/search?q=donald+trump+OR+us+election+OR+congress+OR+kamala+harris+OR+joe+biden+OR+republican+OR+democrat+OR+foreign+policy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Major Outlets", "https://news.google.com/rss/search?q=when:1d+site:nytimes.com+OR+site:washingtonpost.com+OR+site:wsj.com+OR+site:politico.com+trump+OR+harris+OR+biden&hl=en-US&gl=US&ceid=US:en"),
]

SPORTS_SOURCES = [
    ("Sports & College", "https://news.google.com/rss/search?q=march+madness+OR+college+basketball+OR+ncaa+tournament+OR+arizona+wildcats+OR+purdue+boilermakers+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Broad Sports", "https://news.google.com/rss/search?q=when:1d+sports+OR+ncaa+OR+college+basketball&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== FETCH FUNCTION ======================
def fetch_section(sources, keywords):
    matches = []
    seen_title = set()  # New: deduplicate by exact title (case-insensitive)
    for source_name, url in sources:
        for attempt in range(3):
            try:
                print(f"  Fetching {source_name}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
                if feed.bozo: break
                for entry in feed.entries:
                    title = entry.title.strip()
                    title_lower = title.lower()
                    link = entry.get('link', '#')
                    if title_lower in seen_title: continue  # Skip if same title already seen
                    if any(kw in title_lower for kw in keywords):
                        ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                        ts = time.mktime(ts_struct) if ts_struct else time.time()
                        matches.append((ts, title, source_name, link))
                        seen_title.add(title_lower)
                break
            except Exception as e:
                print(f"    Attempt {attempt+1} failed: {str(e)}")
                time.sleep(2)
    matches.sort(reverse=True, key=lambda x: x[0])
    return matches

# Fetch each section
middle_matches = fetch_section(MIDDLE_EAST_SOURCES, ME_KEYWORDS)
us_matches = fetch_section(US_POLITICS_SOURCES, US_KEYWORDS)
sports_matches = fetch_section(SPORTS_SOURCES, SPORTS_KEYWORDS)

# Time split
current_ts = time.time()
six_hours_ago = current_ts - 21600

middle_breaking = [item for item in middle_matches if item[0] >= six_hours_ago][:20]
middle_recent = [item for item in middle_matches if item not in middle_breaking][:20]

us_breaking = [item for item in us_matches if item[0] >= six_hours_ago][:20]
us_recent = [item for item in us_matches if item not in us_breaking][:20]

sports_breaking = [item for item in sports_matches if item[0] >= six_hours_ago][:20]
sports_recent = [item for item in sports_matches if item not in sports_breaking][:20]

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
        .header { margin-bottom: 30px; text-align: left; }
        h1 { color: #FFFFFF; margin: 0; text-decoration: underline; font-size: 2.2em; }
        .byline { color: #aaaaaa; font-size: 1.05em; margin: 5px 0 0 0; }
        .update { color: #aaaaaa; font-size: 0.85em; margin: 5px 0 0 0; }
        .section-title { color: #FF0000; font-size: 1.6em; margin: 30px 0 10px; font-weight: bold; text-decoration: underline; text-decoration-color: #FF0000; }
        .top-divider { border: 0; height: 3px; background: #FF0000; margin: 35px 0; }
        .headline { margin-bottom: 18px; padding-bottom: 10px; border-bottom: 1px solid #222222; }
        .title { color: #FFFFFF; }
        .link { color: #F6CB2F; text-decoration: underline; font-size: 0.85em; margin-left: 10px; }
        .link:hover { color: #FFFFFF; }
        .container { display: flex; flex-wrap: wrap; gap: 30px; max-width: 1400px; margin: 0 auto; }
        .column { flex: 1; min-width: 300px; }
        @media (max-width: 768px) { .container { flex-direction: column; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>The Mitchell Post</h1>
        <span class="byline">By Sean Mitchell</span>
        <span class="update">updated at """ + datetime.utcnow().strftime("%H:%M:%S UTC") + """</span>
    </div>

    <!-- US POLITICS -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">US Politics Breaking News</h2>
"""

if us_breaking:
    for ts, title, source, link in us_breaking:
        html += f'<div class="headline"><span class="title">{title}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking US politics news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">US Politics Headlines</h2>
"""

if us_recent:
    for ts, title, source, link in us_recent:
        html += f'<div class="headline"><span class="title">{title}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No additional US politics headlines right now.</p>\n'

html += """
        </div>
    </div>

    <hr class="top-divider">

    <!-- MIDDLE EAST -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Middle East Breaking News</h2>
"""

if middle_breaking:
    for ts, title, source, link in middle_breaking:
        html += f'<div class="headline"><span class="title">{title}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">Middle East Headlines</h2>
"""

if middle_recent:
    for ts, title, source, link in middle_recent:
        html += f'<div class="headline"><span class="title">{title}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No additional headlines right now.</p>\n'

html += """
        </div>
    </div>

    <hr class="top-divider">

    <!-- SPORTS -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Sports Breaking News</h2>
"""

if sports_breaking:
    for ts, title, source, link in sports_breaking:
        html += f'<div class="headline"><span class="title">{title}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking sports news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">Sports Headlines</h2>
"""

if sports_recent:
    for ts, title, source, link in sports_recent:
        html += f'<div class="headline"><span class="title">{title}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No additional sports headlines right now.</p>\n'

html += """
        </div>
    </div>
</body>
</html>
"""

try:
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"SUCCESS: index.html saved to {INDEX_HTML}")
except Exception as e:
    print(f"ERROR saving file: {str(e)}")

print("\nScript finished.")
print("index.html saved to current directory.")