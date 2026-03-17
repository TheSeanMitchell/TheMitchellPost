import feedparser
import time
import os
import re
import urllib.request
from datetime import datetime
from collections import defaultdict

print("Starting bot...")

CURRENT_DIR = os.getcwd()
print(f"Saving files to current directory: {CURRENT_DIR}")

INDEX_HTML = os.path.join(CURRENT_DIR, "index.html")

# ====================== FRIENDLY SOURCE NAMES ======================
SOURCE_MAP = {
    "Reuters": "Reuters",
    "AP News": "AP News",
    "The New York Times": "NYT",
    "The Wall Street Journal": "WSJ",
    "The Washington Post": "Washington Post",
    "Politico": "Politico",
    "Axios": "Axios",
    "NPR": "NPR",
    "PBS": "PBS",
    "BBC": "BBC",
    "C-SPAN": "C-SPAN",
    "The Hill": "The Hill",
    "Al Jazeera": "Al Jazeera",
    "Times of Israel": "Times of Israel",
    "Financial Times": "Financial Times",
    "The Economist": "The Economist",
    "USA Today": "USA Today",
    "Sports Illustrated": "Sports Illustrated",
    "CBS Sports": "CBS Sports",
    "FOX Sports": "FOX Sports",
    "NCAA.com": "NCAA",
    "Global & Regional": "Global News",
    "US Politics Google": "US News",
    "Google US Politics": "US News",
}

def get_friendly_source(raw_name):
    for key in SOURCE_MAP:
        if key.lower() in raw_name.lower():
            return SOURCE_MAP[key]
    return raw_name.split(" - ")[-1].strip() if " - " in raw_name else raw_name

# ====================== KEYWORDS (expanded for volume) ======================
# Middle East
RAW_ME_KEYWORDS = ["middle east", "arab world", "gulf states", "gcc countries", "levant", "maghreb", "mena", "persian gulf", "arabian peninsula", "west asia", "red sea", "iran", "iranian", "tehran", "qom", "mashhad", "isfahan", "tabriz", "khuzestan", "israel", "israeli", "jerusalem", "tel aviv", "west bank", "gaza", "golan", "saudi arabia", "saudi", "riyadh", "jeddah", "neom", "uae", "emirates", "abu dhabi", "dubai", "sharjah", "qatar", "doha", "kuwait", "oman", "bahrain", "iraq", "syria", "lebanon", "jordan", "turkey", "egypt", "yemen", "palestine", "khamenei", "mojtabakhamenei", "ayatollah", "supreme leader", "pezeshkian", "netanyahu", "mohammed bin salman", "mbs", "mohammed bin zayed", "mbz", "erdogan", "el sisi", "tamim", "king abdullah", "bashar al assad", "hezbollah", "hamas", "irgc", "houthis", "pmf", "isis", "gaza war", "israel gaza", "gaza ceasefire", "israel lebanon", "yemen civil war", "red sea crisis", "syria civil war", "idlib", "iran proxy", "axis of resistance", "iran nuclear", "jcpoa", "snapback sanctions", "hormuz", "strait hormuz", "oil prices", "brent crude", "wti crude", "opec", "kharg island", "iran oil exports", "centcom"]
ME_KEYWORDS = set(word.lower() for kw in RAW_ME_KEYWORDS for word in kw.split())

# US Politics (expanded)
RAW_US_KEYWORDS = ["united states politics", "american politics", "us government", "federal government", "white house", "us congress", "us senate", "house of representatives", "supreme court", "us constitution", "bill of rights", "federal election", "presidential election", "midterm elections", "primary elections", "electoral college", "inauguration day", "state of the union", "campaign rally", "political campaign", "political debate", "voter turnout", "election day", "swing states", "battleground states", "donald trump", "trump campaign", "joe biden", "biden administration", "kamala harris", "vice president", "republican party", "democratic party", "gop", "democrat", "maga", "ron desantis", "gavin newsom", "greg abbott", "marco rubio", "ted cruz", "alexandria ocasio cortez", "aoc", "nancy pelosi", "mitch mcconnell", "chuck schumer", "hakeem jeffries", "supreme court ruling", "federal budget", "inflation united states", "us economy", "gun control", "immigration policy", "border security", "climate policy", "healthcare policy", "student loan", "abortion rights", "lgbtq rights", "culture wars", "election security", "misinformation campaigns", "political polling", "campaign finance", "super pac"]
US_KEYWORDS = set(word.lower() for kw in RAW_US_KEYWORDS for word in kw.split())

# Sports
RAW_SPORTS_KEYWORDS = ["march madness", "college basketball", "arizona wildcats", "purdue boilermakers", "miami hurricanes", "villanova wildcats", "utah state aggies", "ncaa tournament", "college basketball crown", "ncaa bracket", "march madness bracket"]
SPORTS_KEYWORDS = set(word.lower() for kw in RAW_SPORTS_KEYWORDS for word in kw.split())

# ====================== BLOCKLISTS ======================
ME_BLOCKLIST = {"trump", "harris", "biden", "congress", "senate", "house", "supreme court", "election", "midterm", "presidential", "republican", "democrat", "maga", "white house", "capitol", "washington dc"}
US_BLOCKLIST = {"iran", "israel", "gaza", "hezbollah", "hamas", "hormuz", "khamenei", "netanyahu", "mbs", "mbz", "saudi", "uae", "qatar", "lebanon", "syria", "yemen", "palestine", "irgc", "houthis", "axis of resistance", "jcpoa", "snapback sanctions", "strait of hormuz"}
SPORTS_BLOCKLIST = ME_BLOCKLIST.union(US_BLOCKLIST)

# ====================== SECTION-SPECIFIC SOURCES (prioritized reputable first + expanded) ======================
MIDDLE_EAST_SOURCES = [
    ("Reuters", "https://feeds.reuters.com/reuters/worldNews"),
    ("AP News", "https://feeds.apnews.com/rss/apf-topnews"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Times of Israel", "https://www.timesofisrael.com/feed/"),
    ("Global Regional", "https://news.google.com/rss/search?q=middle+east+OR+iran+OR+israel+OR+gulf+OR+hezbollah+OR+hamas+OR+saudi+OR+uae+OR+qatar+OR+syria+OR+lebanon+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NYT WSJ FT Economist", "https://news.google.com/rss/search?q=when:1d+site:nytimes.com+OR+site:wsj.com+OR+site:ft.com+OR+site:economist.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
]

US_POLITICS_SOURCES = [
    ("AP News", "https://feeds.apnews.com/rss/apf-topnews"),
    ("Reuters Politics", "https://feeds.reuters.com/reuters/politicsNews"),
    ("NYT Politics", "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"),
    ("WSJ Politics", "https://feeds.wsj.com/wsj/us/politics"),
    ("Washington Post Politics", "https://feeds.washingtonpost.com/rss/politics"),
    ("Politico", "https://www.politico.com/rss/politicopicks.xml"),
    ("Axios", "https://www.axios.com/feed"),
    ("NPR Politics", "https://feeds.npr.org/1019/rss.xml"),
    ("PBS NewsHour", "https://www.pbs.org/newshour/feeds/rss/headlines"),
    ("BBC US", "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
    ("C-SPAN", "https://www.c-span.org/rss/latestClips/"),
    ("Google US Politics", "https://news.google.com/rss/search?q=donald+trump+OR+us+election+OR+congress+OR+kamala+harris+OR+joe+biden+OR+republican+OR+democrat+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

SPORTS_SOURCES = [
    ("College Sports", "https://news.google.com/rss/search?q=march+madness+OR+college+basketball+OR+ncaa+tournament+OR+arizona+wildcats+OR+purdue+boilermakers+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Broad Sports", "https://news.google.com/rss/search?q=when:1d+sports+OR+ncaa+OR+college+basketball+OR+football&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== FETCH FUNCTION (5-per-source + no consecutive + reputable priority) ======================
def normalize_title(title):
    if " - " in title:
        title = title.rsplit(" - ", 1)[0]
    return title.strip().lower()

def fetch_section(sources, keywords, blocklist):
    matches = []
    seen_title = set()
    source_count = defaultdict(int)
    last_source = None
    
    for source_name, url in sources:
        if source_count[source_name] >= 5:
            continue
        for attempt in range(3):
            try:
                print(f"  Fetching {source_name}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
                if feed.bozo: break
                for entry in feed.entries:
                    if source_count[source_name] >= 5:
                        break
                    raw_title = entry.title.strip()
                    norm_title = normalize_title(raw_title)
                    link = entry.get('link', '#')
                    
                    if norm_title in seen_title:
                        continue
                    if blocklist and any(block in raw_title.lower() for block in blocklist):
                        continue
                    if any(kw in raw_title.lower() for kw in keywords):
                        if source_name == last_source:
                            continue
                        ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                        ts = time.mktime(ts_struct) if ts_struct else time.time()
                        matches.append((ts, raw_title, source_name, link))
                        seen_title.add(norm_title)
                        source_count[source_name] += 1
                        last_source = source_name
                break
            except Exception as e:
                print(f"    Attempt {attempt+1} failed: {str(e)}")
                time.sleep(2)
    matches.sort(reverse=True, key=lambda x: x[0])
    return matches

# Fetch sections
middle_matches = fetch_section(MIDDLE_EAST_SOURCES, ME_KEYWORDS, US_BLOCKLIST)
us_matches = fetch_section(US_POLITICS_SOURCES, US_KEYWORDS, ME_BLOCKLIST)
sports_matches = fetch_section(SPORTS_SOURCES, SPORTS_KEYWORDS, ME_BLOCKLIST.union(US_BLOCKLIST))

# Time split (still 6h / 24h)
current_ts = time.time()
six_hours_ago = current_ts - 21600

middle_breaking = [item for item in middle_matches if item[0] >= six_hours_ago][:30]
middle_recent = [item for item in middle_matches if item not in middle_breaking][:30]

us_breaking = [item for item in us_matches if item[0] >= six_hours_ago][:30]
us_recent = [item for item in us_matches if item not in us_breaking][:30]

sports_breaking = [item for item in sports_matches if item[0] >= six_hours_ago][:30]
sports_recent = [item for item in sports_matches if item not in sports_breaking][:30]

# ====================== BUILD HTML (friendly source + 30 per column) ======================
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

    <!-- US -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Breaking US News</h2>
"""

if us_breaking:
    for ts, title, source, link in us_breaking:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking US news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">Today's US Headlines</h2>
"""

if us_recent:
    for ts, title, source, link in us_recent:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No additional US headlines right now.</p>\n'

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
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">Today's Middle East Headlines</h2>
"""

if middle_recent:
    for ts, title, source, link in middle_recent:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
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
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking sports news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">Today's Sports Headlines</h2>
"""

if sports_recent:
    for ts, title, source, link in sports_recent:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
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
print("Files saved to current directory.")