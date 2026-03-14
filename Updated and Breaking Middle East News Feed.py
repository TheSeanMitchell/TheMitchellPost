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

# Safe HTML path
DOCS_FOLDER = os.path.join(os.path.expanduser("~"), "Documents")
HTML_FILE = os.path.join(DOCS_FOLDER, "news_feed.html")

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

html = """
<div style="background:#000000; color:#ffffff; font-family:Arial,sans-serif; padding:20px; margin:0; line-height:1.5;">
    <!-- Breaking News top section – top 20 most recent -->
    <h2 style="color:#FF0000; font-size:1.6em; font-weight:bold; margin:30px 0 10px;">Breaking News</h2>
    <div id="top-feed">
"""

if all_matches:
    for ts, title, source, link in all_matches[:20]:
        highlighted_title = title
        for kw in RAW_KEYWORDS:
            if ' ' in kw:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span style="color:#00FFFF; font-weight:bold; text-decoration:underline;">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        for kw in KEYWORDS:
            if ' ' not in kw and len(kw) > 2:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span style="color:#00FFFF; font-weight:bold; text-decoration:underline;">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        html += f'<div class="headline" style="margin-bottom:18px; padding-bottom:10px; border-bottom:1px solid #222222;"><span class="title" style="color:#ffffff;">{highlighted_title}</span> <a class="link" href="{link}" target="_blank" style="color:#003300; text-decoration:none; margin-left:10px; font-size:0.9em;">[Read Article]</a></div>\n'
else:
    html += '<p>No breaking news available right now.</p>\n'

html += """
    </div>
    <hr style="border:0; height:3px; background:#FF0000; margin:25px 0 35px;">

    <!-- Main balanced feed – top 80 -->
    <h2 style="color:#FF0000; font-size:1.6em; font-weight:bold; margin:30px 0 10px;">All Recent Headlines</h2>
    <div id="feed">
"""

if all_matches:
    for ts, title, source, link in all_matches[:80]:
        highlighted_title = title
        for kw in RAW_KEYWORDS:
            if ' ' in kw:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span style="color:#00FFFF; font-weight:bold; text-decoration:underline;">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        for kw in KEYWORDS:
            if ' ' not in kw and len(kw) > 2:
                pattern = r'\b' + re.escape(kw) + r'\b'
                highlighted_title = re.sub(pattern, f'<span style="color:#00FFFF; font-weight:bold; text-decoration:underline;">{kw}</span>', highlighted_title, flags=re.IGNORECASE)
        html += f'<div class="headline" style="margin-bottom:18px; padding-bottom:10px; border-bottom:1px solid #222222;"><span class="title" style="color:#ffffff;">{highlighted_title}</span> <a class="link" href="{link}" target="_blank" style="color:#003300; text-decoration:none; margin-left:10px; font-size:0.9em;">[Read Article]</a></div>\n'
else:
    html += '<p>No additional headlines right now.</p>\n'

html += """
    </div>
</div>
"""

try:
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Feed saved to: {HTML_FILE}")
except Exception as e:
    print(f"Save failed: {str(e)}")
    input("Press Enter to exit...")
    exit()

file_url = f"file:///{HTML_FILE.replace('\\', '/')}"
webbrowser.open_new_tab(file_url)
print("Opened in browser (new tab). Close console when done.")

input("Press Enter in this window to close when finished...\n")