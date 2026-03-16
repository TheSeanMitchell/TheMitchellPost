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
RAW_ME_KEYWORDS = ["middle east", "arab world", "gulf states", "gcc countries", "levant region", "maghreb region", "mena region",
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
                   "gaza humanitarian crisis", "yemen famine", "climate change middle east"]
ME_KEYWORDS = set(word.lower() for kw in RAW_ME_KEYWORDS for word in kw.split())

# US Politics (your expanded list)
RAW_US_KEYWORDS = ["united states politics", "american politics", "us government", "federal government", "white house", "us congress", "us senate",
                   "house of representatives", "supreme court", "us constitution", "bill of rights", "federal election", "presidential election",
                   "midterm elections", "primary elections", "electoral college", "inauguration day", "state of the union", "campaign rally",
                   "political campaign", "political debate", "voter turnout", "voter registration", "absentee ballot", "mail in voting", "early voting",
                   "election day", "swing states", "battleground states", "red states", "blue states", "purple states", "democracy in america",
                   "constitutional law", "executive order", "federal legislation", "government shutdown", "filibuster", "senate majority leader",
                   "house speaker", "cabinet secretary", "national security council", "supreme court ruling", "federal budget", "national debt",
                   "government spending", "tax reform", "immigration policy", "border security", "border wall", "southern border crisis",
                   "us mexico border", "immigration reform", "asylum policy", "daca", "dreamers policy", "federal reserve", "inflation united states",
                   "us economy", "unemployment rate us", "federal interest rates", "federal reserve policy", "stock market news usa", "wall street",
                   "nasdaq", "dow jones", "s&p 500", "tech industry usa", "silicon valley", "big tech regulation", "antitrust lawsuits tech",
                   "ai regulation usa", "climate policy usa", "energy policy usa", "oil production usa", "gas prices america", "renewable energy usa",
                   "infrastructure bill", "infrastructure spending usa", "healthcare policy usa", "medicare", "medicaid", "affordable care act",
                   "obamacare debate", "pharmaceutical prices usa", "gun control debate", "second amendment rights", "gun legislation usa",
                   "police reform usa", "criminal justice reform", "supreme court nominations", "judicial appointments", "federal judges usa",
                   "donald trump", "trump campaign", "trump rally", "trump indictment", "trump trial", "trump supporters", "maga movement",
                   "joe biden", "biden administration", "biden speech", "biden policy agenda", "kamala harris", "vice president united states",
                   "republican party", "democratic party", "libertarian party usa", "green party usa", "gop leadership", "democrat leadership",
                   "senate republicans", "senate democrats", "house republicans", "house democrats", "presidential candidates 2028",
                   "potential presidential candidates usa", "republican primary candidates", "democratic primary candidates", "governor elections usa",
                   "senate races usa", "house races usa", "state legislatures usa", "state governors usa", "ron desantis", "gavin newsom",
                   "greg abbott", "kathy hochul", "josh shapiro", "gretchen whitmer", "brian kemp", "glenn youngkin", "pete buttigieg",
                   "bernie sanders", "elizabeth warren", "marco rubio", "ted cruz", "rand paul", "mitt romney", "lindsey graham", "chuck schumer",
                   "mitch mcconnell", "hakeem jeffries", "kevin mccarthy", "nancy pelosi", "alexandria ocasio cortez", "aoc", "ilhan omar",
                   "rashida tlaib", "ayanna pressley", "marjorie taylor greene", "lauren boebert", "matt gaetz", "elon musk", "tesla ceo",
                   "spacex launches", "starlink satellites", "x platform news", "twitter politics", "mark zuckerberg", "meta platforms",
                   "facebook news", "instagram trends", "jeff bezos", "amazon news", "bill gates", "microsoft founder", "sam altman",
                   "openai leadership", "artificial intelligence debate usa", "ai ethics debate", "tech billionaires politics", "celebrity politics usa",
                   "hollywood politics", "entertainment industry activism", "taylor swift news", "kanye west controversy", "kim kardashian news",
                   "beyonce news", "jay z news", "oprah winfrey news", "joe rogan podcast", "famous podcasts usa", "podcast politics usa",
                   "american influencers", "social media influencers usa", "youtube creators usa", "twitch streamers usa", "tiktok trends usa",
                   "viral videos usa", "american pop culture", "celebrity scandals usa", "celebrity activism usa", "hollywood strikes",
                   "writers guild strike", "actors strike hollywood", "film industry usa", "box office usa", "streaming wars usa", "netflix news",
                   "disney news", "apple tv plus news", "sports politics usa", "nfl news", "super bowl", "nba finals", "mlb world series",
                   "college football playoff", "olympics usa team", "college sports nil rules", "college campus protests usa", "university politics usa",
                   "student loan forgiveness", "student loan policy", "campus free speech debate", "academic freedom usa", "culture wars usa",
                   "free speech debate usa", "cancel culture debate", "woke culture debate", "identity politics usa", "civil rights movement history",
                   "racial justice protests", "black lives matter movement", "police brutality protests", "immigration protests usa", "labor unions usa",
                   "union strikes usa", "workers rights usa", "minimum wage debate", "gig economy workers", "uber drivers protests", "amazon labor unionization",
                   "tech layoffs usa", "housing crisis usa", "real estate market usa", "mortgage rates usa", "rent prices usa", "homelessness crisis usa",
                   "climate protests usa", "environmental activism usa", "national parks usa", "wildfire crisis california", "hurricane season usa",
                   "disaster response usa", "fema response", "emergency management usa", "public health policy usa", "pandemic response usa",
                   "vaccine policy usa", "cdc guidelines usa", "public school policy", "education reform usa", "charter schools debate", "teacher strikes usa",
                   "school board politics", "parental rights movement", "book bans schools usa", "library censorship debate", "religious freedom usa",
                   "church and state debate", "abortion rights debate", "roe v wade overturn", "supreme court abortion ruling", "planned parenthood policy",
                   "pro life movement", "pro choice movement", "lgbtq rights usa", "transgender rights debate", "same sex marriage law", "pride month events usa",
                   "fourth of july celebrations", "independence day usa", "memorial day usa", "veterans day usa", "thanksgiving holiday usa", "labor day usa",
                   "martin luther king day", "presidents day usa", "juneteenth holiday", "halloween usa traditions", "christmas usa traditions",
                   "new years celebrations usa", "american traditions", "american culture", "american dream debate", "patriotism usa", "national anthem protests",
                   "pledge of allegiance debate", "flag controversy usa", "military spending usa", "pentagon budget", "us armed forces", "us navy deployments",
                   "us army operations", "us air force strategy", "space force missions", "defense contractors usa", "lockheed martin news",
                   "boeing defense contracts", "raytheon technologies", "military aid ukraine", "foreign aid debate usa", "nato alliance politics",
                   "us china relations", "us russia relations", "trade war china usa", "tariffs policy usa", "supply chain issues usa",
                   "semiconductor industry usa", "chips act implementation", "manufacturing policy usa", "reshoring industry usa",
                   "american innovation policy", "startup ecosystem usa", "venture capital usa", "small business policy", "chamber of commerce usa",
                   "consumer protection usa", "federal trade commission cases", "department of justice antitrust", "supreme court antitrust cases",
                   "media bias debate usa", "press freedom usa", "journalism ethics usa", "investigative journalism usa", "whistleblower cases usa",
                   "freedom of information act requests", "government transparency usa", "campaign finance law", "citizens united ruling", "super pac spending",
                   "political donations usa", "lobbying in washington", "k street lobbying", "political polling usa", "election forecasts usa",
                   "demographic trends usa", "census data usa", "population shifts usa", "urban politics usa", "rural politics", "suburban voting trends",
                   "generational voting trends", "gen z politics usa", "millennial voters usa", "baby boomer voters", "religion in politics usa",
                   "evangelical voters usa", "catholic voters usa", "jewish voters usa", "muslim voters usa", "latino voters usa", "black voters usa",
                   "asian american voters", "native american voters", "immigration demographics usa", "american identity debate", "national security policy usa",
                   "homeland security alerts", "cybersecurity usa", "cyber attacks infrastructure", "election security usa", "misinformation campaigns usa",
                   "disinformation social media", "political advertising usa", "campaign strategy usa", "grassroots movements usa", "protest movements usa",
                   "grassroots fundraising", "town hall meetings usa", "political conventions usa", "republican national convention",
                   "democratic national convention", "presidential transition process", "cabinet nominations usa", "senate confirmation hearings",
                   "congressional investigations", "special counsel investigations", "impeachment proceedings usa", "supreme court ethics debate",
                   "judicial reform debate", "constitutional amendments debate", "states rights debate", "federalism debate usa"]
US_KEYWORDS = set(word.lower() for kw in RAW_US_KEYWORDS for word in kw.split())

# Sports (unchanged)
RAW_SPORTS_KEYWORDS = ["march madness", "college basketball", "arizona wildcats", "purdue boilermakers", "miami hurricanes",
                       "villanova wildcats", "utah state aggies"]
SPORTS_KEYWORDS = set(word.lower() for kw in RAW_SPORTS_KEYWORDS for word in kw.split())

# ====================== SECTION-SPECIFIC SOURCES ======================
MIDDLE_EAST_SOURCES = [
    ("Global & Regional", "https://news.google.com/rss/search?q=middle+east+OR+iran+OR+israel+OR+gulf+OR+hezbollah+OR+hamas+OR+saudi+OR+uae+OR+qatar+OR+syria+OR+lebanon+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters & AP", "https://news.google.com/rss/search?q=when:1d+site:reuters.com+OR+site:apnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("FT, Economist, WSJ, NYT", "https://news.google.com/rss/search?q=when:1d+site:ft.com+OR+site:economist.com+OR+site:wsj.com+OR+site:nytimes.com+middle+east+OR+iran+OR+gulf&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera & Regional", "https://news.google.com/rss/search?q=when:1d+site:aljazeera.com+OR+site:timesofisrael.com+OR+site:arabnews.com+OR+site:thenationalnews.com+iran+OR+israel+OR+gulf&hl=en-US&gl=US&ceid=US:en"),
]

US_POLITICS_SOURCES = [
    ("US Politics & Congress", "https://news.google.com/rss/search?q=donald+trump+OR+us+election+OR+congress+OR+kamala+harris+OR+joe+biden+OR+republican+OR+democrat+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Major US Outlets", "https://news.google.com/rss/search?q=when:1d+site:nytimes.com+OR+site:washingtonpost.com+OR+site:wsj.com+OR+site:politico.com+OR+site:axios.com+trump+OR+harris+OR+biden+OR+congress&hl=en-US&gl=US&ceid=US:en"),
    ("Analysis & Policy", "https://news.google.com/rss/search?q=when:1d+site:thehill.com+OR+site:foreignaffairs.com+OR+site:foreignpolicy.com+us+politics+OR+white+house+OR+supreme+court&hl=en-US&gl=US&ceid=US:en"),
]

SPORTS_SOURCES = [
    ("College Sports", "https://news.google.com/rss/search?q=march+madness+OR+college+basketball+OR+ncaa+tournament+OR+arizona+wildcats+OR+purdue+boilermakers+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Broad Sports", "https://news.google.com/rss/search?q=when:1d+sports+OR+ncaa+OR+college+basketball+OR+football&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== FETCH FUNCTION (with title-only dedup) ======================
def fetch_section(sources, keywords):
    matches = []
    seen_title = set()  # Deduplicate by exact title (case-insensitive)
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
                    if title_lower in seen_title: 
                        continue  # Skip if same title already seen in this section
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
print("Files saved to current directory.")