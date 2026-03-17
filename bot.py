import feedparser
import time
import os
import re
from datetime import datetime
from collections import defaultdict

print("=== The Mitchell Post Refresh Started ===")

INDEX_HTML = "index.html"

# ====================== FRIENDLY SOURCE NAMES ======================
SOURCE_MAP = {
    "Reuters": "Reuters", "AP News": "AP News", "The New York Times": "NYT",
    "The Wall Street Journal": "WSJ", "The Washington Post": "Washington Post",
    "Politico": "Politico", "Axios": "Axios", "NPR": "NPR", "PBS": "PBS",
    "BBC": "BBC", "C-SPAN": "C-SPAN", "The Hill": "The Hill",
    "Al Jazeera": "Al Jazeera", "Times of Israel": "Times of Israel",
    "Financial Times": "Financial Times", "The Economist": "The Economist",
    "USA Today": "USA Today", "CBS Sports": "CBS Sports", "FOX Sports": "FOX Sports",
    "NCAA.com": "NCAA"
}

def get_friendly_source(raw_name):
    for key in SOURCE_MAP:
        if key.lower() in raw_name.lower():
            return SOURCE_MAP[key]
    return raw_name.split(" - ")[-1].strip() if " - " in raw_name else raw_name

# ====================== FULL KEYWORDS (all your lists) ======================
# Middle East keywords
RAW_ME_KEYWORDS = ["middle east", "middle east news", "arab world", "gulf states", "gcc countries", "levant region", "maghreb region", "mena region", "persian gulf", "arabian peninsula", "west asia", "red sea region", "iran", "iranian", "tehran", "qom", "mashhad", "isfahan", "tabriz", "khuzestan", "israel", "israeli", "jerusalem", "tel aviv", "west bank", "gaza strip", "golan heights", "saudi arabia", "saudi", "riyadh", "jeddah", "neom", "vision 2030", "united arab emirates", "uae", "emirates", "abu dhabi", "dubai", "sharjah", "qatar", "doha", "kuwait", "kuwait city", "oman", "muscat", "bahrain", "manama", "iraq", "iraqi", "baghdad", "basra", "mosul", "kurdistan iraq", "erbil", "syria", "syrian", "damascus", "aleppo", "idlib", "lebanon", "lebanese", "beirut", "jordan", "amman", "turkey", "turkish", "ankara", "istanbul", "egypt", "egyptian", "cairo", "alexandria", "yemen", "yemeni", "sanaa", "aden", "palestine", "palestinian", "ramallah", "khamenei", "mojtabakhamenei", "mojta ba khamenei", "ayatollah", "supreme leader iran", "president iran", "pezeshkian", "benjamin netanyahu", "netanyahu government", "israeli war cabinet", "mohammed bin salman", "mbs saudi", "saudi crown prince", "mohammed bin zayed", "mbz", "recep tayyip erdogan", "abdel fattah el sisi", "tamim bin hamad al thani", "king abdullah jordan", "bashar al assad", "middle east war", "regional war middle east", "military escalation middle east", "proxy war middle east", "militia middle east", "airstrike middle east", "drone strike middle east", "missile attack middle east", "ballistic missile middle east", "naval clash middle east", "red sea shipping attack", "military buildup middle east", "troop deployment middle east", "hezbollah", "hamas", "palestinian islamic jihad", "irgc", "islamic revolutionary guard corps", "houthis", "ansar allah", "popular mobilization forces", "pmf iraq", "al qaeda arabian peninsula", "aqap", "isis", "isis-k", "islamic state", "gaza war", "israel gaza war", "gaza ceasefire", "israel lebanon border conflict", "israel hezbollah conflict", "yemen civil war", "red sea crisis", "syria civil war", "idlib offensive", "iraq militia attacks", "iran israel shadow war", "iran nuclear program", "uranium iran", "uranium enrichment", "nuclear breakout time", "iran centrifuges", "natanz nuclear facility", "fordow nuclear facility", "iaea iran", "nuclear inspections iran", "jcpoa", "iran nuclear deal", "snapback sanctions", "ballistic missile program iran", "hypersonic missile iran", "brent crude", "wti crude", "oil supply disruption", "opec", "opec+", "oil tanker attack", "tanker seizure", "hormuz blockade", "strait hormuz", "red sea shipping", "suez canal shipping", "lng exports qatar", "saudi oil production", "kharg island", "iran oil exports", "us middle east policy", "us centcom", "centcom iran", "centcom strikes", "us military bases middle east", "american troops iraq", "us troops syria", "russia middle east policy", "russia syria military", "china middle east diplomacy", "china iran deal", "belt and road middle east", "abraham accords", "israel normalization", "saudi israel normalization", "arab league", "iran saudi relations", "iran china mediation", "turkey nato middle east", "iran protest", "iran unrest", "iran revolution", "arab spring", "middle east protests", "economic protests middle east", "government crackdown middle east", "regime change middle east", "political prisoners middle east", "shia islam", "sunni islam", "religious authority iran", "hajj pilgrimage", "mecca pilgrimage", "islamic scholarship middle east", "religious tensions middle east", "drone warfare middle east", "iran drones", "shahed drone", "cyber attack middle east", "cyber warfare israel iran", "ai military middle east", "missile defense israel", "iron dome", "arrow missile defense", "neom saudi", "saudi giga projects", "uae space program", "dubai real estate boom", "qatar world cup legacy", "middle east infrastructure", "refugee crisis middle east", "syrian refugees", "gaza humanitarian crisis", "famine yemen", "water crisis middle east", "climate change middle east", "desertification middle east", "breaking news middle east", "middle east analysis", "middle east geopolitics", "middle east conflict update", "middle east security update", "regional escalation", "gray zone conflict", "proxy warfare", "strategic deterrence", "regional balance of power", "maritime security gulf", "energy security middle east", "october 7 attack", "october 7 israel attack", "hamas october 7", "gaza ground offensive", "rafah offensive", "rafah crossing", "rafah evacuation", "gaza reconstruction", "gaza displacement", "gaza hostage crisis", "israeli hostages", "hostage negotiations gaza", "prisoner exchange israel hamas", "ceasefire negotiations gaza", "humanitarian corridor gaza", "gaza aid convoy", "gaza famine warning", "gaza refugee camps", "west bank raids", "settler violence west bank", "west bank escalation", "lebanon front escalation", "israel lebanon war risk", "hezbollah rocket barrage", "hezbollah precision missiles", "northern israel evacuation", "blue line conflict", "iran proxy network", "axis of resistance", "iran proxy war", "iran regional militias", "iran leadership crisis", "iran power struggle", "iran succession crisis", "post khamenei iran", "khamenei successor debate", "iran clerical leadership vacuum", "iran regime stability", "iran military leadership", "iran revolutionary guard leadership", "iran supreme leadership council", "iran transitional government speculation", "iran constitutional crisis", "iran elite power struggle", "iran hardliners vs reformists", "iran security crackdown", "iran internet blackout", "iran economic collapse", "iran rial crisis", "iran capital flight", "iran sanctions evasion", "iran shadow fleet", "iran tanker fleet", "iran drone exports", "iran russia drone deal", "iran china strategic partnership", "iran missile stockpile", "iran underground bases", "iran retaliation israel", "israel strike iran", "israel iran escalation", "israel preemptive strike iran", "israel nuclear red line", "regional escalation scenario", "persian gulf naval standoff", "gulf tanker war", "red sea naval task force", "maritime coalition red sea", "houthi missile attacks shipping", "houthi drone attacks ships", "bab el mandeb strait crisis", "global shipping disruption red sea", "insurance crisis shipping middle east", "oil shock risk middle east", "energy market shock middle east", "refugee flows middle east war", "regional war scenario middle east", "multi front war israel", "israel gaza lebanon war", "israel iran direct conflict", "iran retaliation scenario", "middle east escalation timeline", "middle east war forecast", "middle east geopolitical risk", "strategic chokepoints middle east", "global oil chokepoints", "hormuz crisis scenario", "red sea blockade scenario", "eastern mediterranean gas fields", "levant gas dispute", "cyprus gas exploration", "turkey greece eastern mediterranean tensions", "middle east arms race", "missile proliferation middle east", "drone proliferation middle east", "regional nuclear proliferation", "saudi nuclear program", "uae nuclear program", "middle east security architecture", "us carrier strike group middle east", "aircraft carrier persian gulf", "strategic bombing middle east", "bunker buster strike iran", "underground nuclear facility iran", "intelligence leaks middle east conflict", "satellite imagery iran bases", "osint iran military", "war games middle east scenario", "think tank analysis middle east conflict", "geopolitical forecasting middle east", "global markets reaction middle east war", "oil price spike middle east conflict", "defense spending middle east", "military mobilization middle east", "emergency diplomacy middle east", "backchannel negotiations middle east", "crisis summit middle east leaders", "international mediation middle east conflict"]
ME_KEYWORDS = set(word.lower() for kw in RAW_ME_KEYWORDS for word in kw.split())

# Full US keywords (all of them)
RAW_US_KEYWORDS = ["united states politics", "american politics", "us government", "federal government", "white house", "us congress", "us senate", "house of representatives", "supreme court", "us constitution", "bill of rights", "federal election", "presidential election", "midterm elections", "primary elections", "electoral college", "inauguration day", "state of the union", "campaign rally", "political campaign", "political debate", "voter turnout", "voter registration", "absentee ballot", "mail in voting", "early voting", "election day", "swing states", "battleground states", "red states", "blue states", "purple states", "democracy in america", "constitutional law", "executive order", "federal legislation", "government shutdown", "filibuster", "senate majority leader", "house speaker", "cabinet secretary", "national security council", "supreme court ruling", "federal budget", "national debt", "government spending", "tax reform", "immigration policy", "border security", "border wall", "southern border crisis", "us mexico border", "immigration reform", "asylum policy", "daca", "dreamers policy", "federal reserve", "inflation united states", "us economy", "unemployment rate us", "federal interest rates", "federal reserve policy", "stock market news usa", "wall street", "nasdaq", "dow jones", "s&p 500", "tech industry usa", "silicon valley", "big tech regulation", "antitrust lawsuits tech", "ai regulation usa", "climate policy usa", "energy policy usa", "oil production usa", "gas prices america", "renewable energy usa", "infrastructure bill", "infrastructure spending usa", "healthcare policy usa", "medicare", "medicaid", "affordable care act", "obamacare debate", "pharmaceutical prices usa", "gun control debate", "second amendment rights", "gun legislation usa", "police reform usa", "criminal justice reform", "supreme court nominations", "judicial appointments", "federal judges usa", "donald trump", "trump campaign", "trump rally", "trump indictment", "trump trial", "trump supporters", "maga movement", "make america great again", "joe biden", "biden administration", "biden speech", "biden policy agenda", "kamala harris", "vice president united states", "republican party", "democratic party", "libertarian party usa", "green party usa", "gop leadership", "democrat leadership", "senate republicans", "senate democrats", "house republicans", "house democrats", "presidential candidates 2028", "potential presidential candidates usa", "republican primary candidates", "democratic primary candidates", "governor elections usa", "senate races usa", "house races usa", "state legislatures usa", "state governors usa", "ron desantis", "gavin newsom", "greg abbott", "kathy hochul", "josh shapiro", "gretchen whitmer", "brian kemp", "glenn youngkin", "pete buttigieg", "bernie sanders", "elizabeth warren", "marco rubio", "ted cruz", "rand paul", "mitt romney", "lindsey graham", "chuck schumer", "mitch mcconnell", "hakeem jeffries", "kevin mccarthy", "nancy pelosi", "alexandria ocasio cortez", "aoc", "ilhan omar", "rashida tlaib", "ayanna pressley", "marjorie taylor greene", "lauren boebert", "matt gaetz", "elon musk", "tesla ceo", "spacex launches", "starlink satellites", "x platform news", "twitter politics", "mark zuckerberg", "meta platforms", "facebook news", "instagram trends", "jeff bezos", "amazon news", "bill gates", "microsoft founder", "sam altman", "openai leadership", "artificial intelligence debate usa", "ai ethics debate", "tech billionaires politics", "celebrity politics usa", "hollywood politics", "entertainment industry activism", "taylor swift news", "kanye west controversy", "kim kardashian news", "beyonce news", "jay z news", "oprah winfrey news", "joe rogan podcast", "famous podcasts usa", "podcast politics usa", "american influencers", "social media influencers usa", "youtube creators usa", "twitch streamers usa", "tiktok trends usa", "viral videos usa", "american pop culture", "celebrity scandals usa", "celebrity activism usa", "hollywood strikes", "writers guild strike", "actors strike hollywood", "film industry usa", "box office usa", "streaming wars usa", "netflix news", "disney news", "apple tv plus news", "sports politics usa", "nfl news", "super bowl", "nba finals", "mlb world series", "college football playoff", "olympics usa team", "college sports nil rules", "college campus protests usa", "university politics usa", "student loan forgiveness", "student loan policy", "campus free speech debate", "academic freedom usa", "culture wars usa", "free speech debate usa", "cancel culture debate", "woke culture debate", "identity politics usa", "civil rights movement history", "racial justice protests", "black lives matter movement", "police brutality protests", "immigration protests usa", "labor unions usa", "union strikes usa", "workers rights usa", "minimum wage debate", "gig economy workers", "uber drivers protests", "amazon labor unionization", "tech layoffs usa", "housing crisis usa", "real estate market usa", "mortgage rates usa", "rent prices usa", "homelessness crisis usa", "climate protests usa", "environmental activism usa", "national parks usa", "wildfire crisis california", "hurricane season usa", "disaster response usa", "fema response", "emergency management usa", "public health policy usa", "pandemic response usa", "vaccine policy usa", "cdc guidelines usa", "public school policy", "education reform usa", "charter schools debate", "teacher strikes usa", "school board politics", "parental rights movement", "book bans schools usa", "library censorship debate", "religious freedom usa", "church and state debate", "abortion rights debate", "roe v wade overturn", "supreme court abortion ruling", "planned parenthood policy", "pro life movement", "pro choice movement", "lgbtq rights usa", "transgender rights debate", "same sex marriage law", "pride month events usa", "fourth of july celebrations", "independence day usa", "memorial day usa", "veterans day usa", "thanksgiving holiday usa", "labor day usa", "martin luther king day", "presidents day usa", "juneteenth holiday", "halloween usa traditions", "christmas usa traditions", "new years celebrations usa", "american traditions", "american culture", "american dream debate", "patriotism usa", "national anthem protests", "pledge of allegiance debate", "flag controversy usa", "military spending usa", "pentagon budget", "us armed forces", "us navy deployments", "us army operations", "us air force strategy", "space force missions", "defense contractors usa", "lockheed martin news", "boeing defense contracts", "raytheon technologies", "military aid ukraine", "foreign aid debate usa", "nato alliance politics", "us china relations", "us russia relations", "trade war china usa", "tariffs policy usa", "supply chain issues usa", "semiconductor industry usa", "chips act implementation", "manufacturing policy usa", "reshoring industry usa", "american innovation policy", "startup ecosystem usa", "venture capital usa", "small business policy", "chamber of commerce usa", "consumer protection usa", "federal trade commission cases", "department of justice antitrust", "supreme court antitrust cases", "media bias debate usa", "press freedom usa", "journalism ethics usa", "investigative journalism usa", "whistleblower cases usa", "freedom of information act requests", "government transparency usa", "campaign finance law", "citizens united ruling", "super pac spending", "political donations usa", "lobbying in washington", "k street lobbying", "political polling usa", "election forecasts usa", "demographic trends usa", "census data usa", "population shifts usa", "urban politics usa", "rural politics usa", "suburban voting trends", "generational voting trends", "gen z politics usa", "millennial voters usa", "baby boomer voters usa", "religion in politics usa", "evangelical voters usa", "catholic voters usa", "jewish voters usa", "muslim voters usa", "latino voters usa", "black voters usa", "asian american voters", "native american voters", "immigration demographics usa", "american identity debate", "national security policy usa", "homeland security alerts", "cybersecurity usa", "cyber attacks infrastructure", "election security usa", "misinformation campaigns usa", "disinformation social media", "political advertising usa", "campaign strategy usa", "grassroots movements usa", "protest movements usa", "grassroots fundraising", "town hall meetings usa", "political conventions usa", "republican national convention", "democratic national convention", "presidential transition process", "cabinet nominations usa", "senate confirmation hearings", "congressional investigations", "special counsel investigations", "impeachment proceedings usa", "supreme court ethics debate", "judicial reform debate", "constitutional amendments debate", "states rights debate", "federalism debate usa"]
US_KEYWORDS = set(word.lower() for kw in RAW_US_KEYWORDS for word in kw.split())

# Sports
RAW_SPORTS_KEYWORDS = ["march madness", "college basketball", "arizona wildcats", "purdue boilermakers", "miami hurricanes", "villanova wildcats", "utah state aggies", "ncaa tournament", "college basketball crown", "ncaa bracket", "march madness bracket"]
SPORTS_KEYWORDS = set(word.lower() for kw in RAW_SPORTS_KEYWORDS for word in kw.split())

# Blocklists removed (as requested)
ME_BLOCKLIST = set()
US_BLOCKLIST = set()
SPORTS_BLOCKLIST = set()

# ====================== FULL SOURCE LISTS ======================
MIDDLE_EAST_SOURCES = [
    ("Reuters", "https://news.google.com/rss/search?q=when:1d+site:reuters.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Associated Press", "https://news.google.com/rss/search?q=when:1d+site:apnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("BBC News", "https://news.google.com/rss/search?q=when:1d+site:bbc.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Agence France-Presse", "https://news.google.com/rss/search?q=when:1d+site:afp.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times", "https://news.google.com/rss/search?q=when:1d+site:ft.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The Economist", "https://news.google.com/rss/search?q=when:1d+site:economist.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The Wall Street Journal", "https://news.google.com/rss/search?q=when:1d+site:wsj.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The New York Times", "https://news.google.com/rss/search?q=when:1d+site:nytimes.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera English", "https://news.google.com/rss/search?q=when:1d+site:aljazeera.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("CNN International", "https://news.google.com/rss/search?q=when:1d+site:cnn.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian", "https://news.google.com/rss/search?q=when:1d+site:theguardian.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The Washington Post", "https://news.google.com/rss/search?q=when:1d+site:washingtonpost.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Sky News", "https://news.google.com/rss/search?q=when:1d+site:skynews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("France 24 English", "https://news.google.com/rss/search?q=when:1d+site:france24.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("DW News", "https://news.google.com/rss/search?q=when:1d+site:dw.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg News", "https://news.google.com/rss/search?q=when:1d+site:bloomberg.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Politico", "https://news.google.com/rss/search?q=when:1d+site:politico.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The Times of Israel", "https://news.google.com/rss/search?q=when:1d+site:timesofisrael.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Haaretz", "https://news.google.com/rss/search?q=when:1d+site:haaretz.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The Jerusalem Post", "https://news.google.com/rss/search?q=when:1d+site:jpost.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Ynetnews", "https://news.google.com/rss/search?q=when:1d+site:ynetnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("i24NEWS", "https://news.google.com/rss/search?q=when:1d+site:i24news.tv+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The National", "https://news.google.com/rss/search?q=when:1d+site:thenationalnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Arab News", "https://news.google.com/rss/search?q=when:1d+site:arabnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Al Monitor", "https://news.google.com/rss/search?q=when:1d+site:al-monitor.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Al Majalla", "https://news.google.com/rss/search?q=when:1d+site:majalla.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Al Bawaba", "https://news.google.com/rss/search?q=when:1d+site:albawaba.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Kuwait Times", "https://news.google.com/rss/search?q=when:1d+site:kuwaittimes.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs", "https://news.google.com/rss/search?q=when:1d+site:foreignaffairs.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Policy", "https://news.google.com/rss/search?q=when:1d+site:foreignpolicy.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Carnegie Middle East Center", "https://news.google.com/rss/search?q=when:1d+site:carnegie-mec.org+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Middle East Institute", "https://news.google.com/rss/search?q=when:1d+site:mei.edu+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Atlantic Council", "https://news.google.com/rss/search?q=when:1d+site:atlanticcouncil.org+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Brookings Institution", "https://news.google.com/rss/search?q=when:1d+site:brookings.edu+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Institute for Near East Policy", "https://news.google.com/rss/search?q=when:1d+site:washingtoninstitute.org+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Middle East Eye", "https://news.google.com/rss/search?q=when:1d+site:middleeasteye.net+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("New Arab", "https://news.google.com/rss/search?q=when:1d+site:newarab.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Asharq Al-Awsat English", "https://news.google.com/rss/search?q=when:1d+site:aawsat.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Anadolu Agency English", "https://news.google.com/rss/search?q=when:1d+site:aa.com.tr+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Tasnim News English", "https://news.google.com/rss/search?q=when:1d+site:tasnimnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Mehr News Agency English", "https://news.google.com/rss/search?q=when:1d+site:mehrnews.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Press TV", "https://news.google.com/rss/search?q=when:1d+site:presstv.ir+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Kan News", "https://news.google.com/rss/search?q=when:1d+site:kan.org.il+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Egypt Today", "https://news.google.com/rss/search?q=when:1d+site:egypttoday.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Daily Sabah", "https://news.google.com/rss/search?q=when:1d+site:dailysabah.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Bellingcat", "https://news.google.com/rss/search?q=when:1d+site:bellingcat.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("The Intercept", "https://news.google.com/rss/search?q=when:1d+site:theintercept.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("ProPublica", "https://news.google.com/rss/search?q=when:1d+site:propublica.org+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("Arabi Facts Hub", "https://news.google.com/rss/search?q=when:1d+site:arabifacts.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
    ("New Lines Magazine", "https://news.google.com/rss/search?q=when:1d+site:newlinesmag.com+middle+east+OR+iran+OR+israel&hl=en-US&gl=US&ceid=US:en"),
]

US_POLITICS_SOURCES = [
    ("Associated Press", "https://news.google.com/rss/search?q=when:1d+site:apnews.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=when:1d+site:reuters.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg News", "https://news.google.com/rss/search?q=when:1d+site:bloomberg.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Agence France-Presse", "https://news.google.com/rss/search?q=when:1d+site:afp.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Dow Jones Newswires", "https://news.google.com/rss/search?q=when:1d+site:wsj.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The New York Times", "https://news.google.com/rss/search?q=when:1d+site:nytimes.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The Wall Street Journal", "https://news.google.com/rss/search?q=when:1d+site:wsj.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The Washington Post", "https://news.google.com/rss/search?q=when:1d+site:washingtonpost.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Los Angeles Times", "https://news.google.com/rss/search?q=when:1d+site:latimes.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("USA Today", "https://news.google.com/rss/search?q=when:1d+site:usatoday.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("NPR", "https://news.google.com/rss/search?q=when:1d+site:npr.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("PBS NewsHour", "https://news.google.com/rss/search?q=when:1d+site:pbs.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("BBC News", "https://news.google.com/rss/search?q=when:1d+site:bbc.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("CBS News", "https://news.google.com/rss/search?q=when:1d+site:cbsnews.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("ABC News", "https://news.google.com/rss/search?q=when:1d+site:abcnews.go.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("NBC News", "https://news.google.com/rss/search?q=when:1d+site:nbcnews.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("C-SPAN", "https://news.google.com/rss/search?q=when:1d+site:c-span.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Politico", "https://news.google.com/rss/search?q=when:1d+site:politico.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The Hill", "https://news.google.com/rss/search?q=when:1d+site:thehill.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Axios", "https://news.google.com/rss/search?q=when:1d+site:axios.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Roll Call", "https://news.google.com/rss/search?q=when:1d+site:rollcall.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("National Journal", "https://news.google.com/rss/search?q=when:1d+site:nationaljournal.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Congressional Quarterly", "https://news.google.com/rss/search?q=when:1d+site:cq.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Government Executive", "https://news.google.com/rss/search?q=when:1d+site:govexec.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Federal News Network", "https://news.google.com/rss/search?q=when:1d+site:federalnewsnetwork.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("ProPublica", "https://news.google.com/rss/search?q=when:1d+site:propublica.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Center for Public Integrity", "https://news.google.com/rss/search?q=when:1d+site:publicintegrity.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The Marshall Project", "https://news.google.com/rss/search?q=when:1d+site:themarshallproject.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Texas Tribune", "https://news.google.com/rss/search?q=when:1d+site:texastribune.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("CalMatters", "https://news.google.com/rss/search?q=when:1d+site:calmatters.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Mississippi Today", "https://news.google.com/rss/search?q=when:1d+site:mississippitoday.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Wisconsin Watch", "https://news.google.com/rss/search?q=when:1d+site:wisconsinwatch.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Voice of San Diego", "https://news.google.com/rss/search?q=when:1d+site:voiceofsandiego.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The Economist", "https://news.google.com/rss/search?q=when:1d+site:economist.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times", "https://news.google.com/rss/search?q=when:1d+site:ft.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The Atlantic", "https://news.google.com/rss/search?q=when:1d+site:theatlantic.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("The New Yorker", "https://news.google.com/rss/search?q=when:1d+site:newyorker.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs", "https://news.google.com/rss/search?q=when:1d+site:foreignaffairs.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Policy", "https://news.google.com/rss/search?q=when:1d+site:foreignpolicy.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("FiveThirtyEight", "https://news.google.com/rss/search?q=when:1d+site:fivethirtyeight.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Cook Political Report", "https://news.google.com/rss/search?q=when:1d+site:cookpolitical.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Sabato's Crystal Ball", "https://news.google.com/rss/search?q=when:1d+site:centerforpolitics.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("RealClearPolitics", "https://news.google.com/rss/search?q=when:1d+site:realclearpolitics.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Congressional Research Service", "https://news.google.com/rss/search?q=when:1d+site:crsreports.congress.gov+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Government Accountability Office", "https://news.google.com/rss/search?q=when:1d+site:gao.gov+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Congressional Budget Office", "https://news.google.com/rss/search?q=when:1d+site:cbo.gov+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Federal Register", "https://news.google.com/rss/search?q=when:1d+site:federalregister.gov+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Supreme Court of the United States", "https://news.google.com/rss/search?q=when:1d+site:supremecourt.gov+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("OpenSecrets", "https://news.google.com/rss/search?q=when:1d+site:opensecrets.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Project on Government Oversight", "https://news.google.com/rss/search?q=when:1d+site:pogo.org+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
]

SPORTS_SOURCES = [
    ("Broad Sports", "https://news.google.com/rss/search?q=march+madness+OR+college+basketball+OR+ncaa+tournament+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NCAA", "https://news.google.com/rss/search?q=when:1d+site:ncaa.com+march+madness+OR+college+basketball&hl=en-US&gl=US&ceid=US:en"),
    ("CBS Sports", "https://news.google.com/rss/search?q=when:1d+site:cbssports.com+march+madness+OR+college+basketball&hl=en-US&gl=US&ceid=US:en"),
    ("FOX Sports", "https://news.google.com/rss/search?q=when:1d+site:foxsports.com+march+madness+OR+college+basketball&hl=en-US&gl=US&ceid=US:en"),
    ("USA Today", "https://news.google.com/rss/search?q=when:1d+site:usatoday.com+march+madness+OR+college+basketball&hl=en-US&gl=US&ceid=US:en"),
    ("Sports Illustrated", "https://news.google.com/rss/search?q=when:1d+site:si.com+march+madness+OR+college+basketball&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== TIME WINDOWS & FALLBACK ======================
def fetch_section(sources, keywords, blocklist, max_per_source=15):
    matches = []
    seen_title = set()
    source_count = defaultdict(int)
    
    for source_name, url in sources:
        if source_count[source_name] >= max_per_source:
            continue
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=20) as response:
                    feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
                if feed.bozo:
                    break
                for entry in feed.entries:
                    if source_count[source_name] >= max_per_source:
                        break
                    raw_title = entry.title.strip()
                    norm_title = raw_title.lower()
                    link = entry.get('link', '#')
                    
                    if norm_title in seen_title:
                        continue
                    if blocklist and any(block in norm_title for block in blocklist):
                        continue
                    if any(kw in norm_title for kw in keywords):
                        ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                        ts = time.mktime(ts_struct) if ts_struct else time.time()
                        matches.append((ts, raw_title, source_name, link))
                        seen_title.add(norm_title)
                        source_count[source_name] += 1
                break
            except Exception as e:
                time.sleep(2)
    matches.sort(reverse=True, key=lambda x: x[0])
    return matches

# Fetch
middle_matches = fetch_section(MIDDLE_EAST_SOURCES, ME_KEYWORDS, ME_BLOCKLIST)
us_matches = fetch_section(US_POLITICS_SOURCES, US_KEYWORDS, US_BLOCKLIST)
sports_matches = fetch_section(SPORTS_SOURCES, SPORTS_KEYWORDS, SPORTS_BLOCKLIST)

# Time windows
current_ts = time.time()
four_hours_ago = current_ts - 14400   # 4 hours
twenty_hours_later = current_ts + 72000  # 20 hours

# Breaking (last 4 hours)
middle_breaking = [item for item in middle_matches if item[0] >= four_hours_ago][:50]
us_breaking = [item for item in us_matches if item[0] >= four_hours_ago][:50]
sports_breaking = [item for item in sports_matches if item[0] >= four_hours_ago][:50]

# Fallback to fill up to 50
middle_recent = [item for item in middle_matches if item not in middle_breaking][:50 - len(middle_breaking)]
us_recent = [item for item in us_matches if item not in us_breaking][:50 - len(us_breaking)]
sports_recent = [item for item in sports_matches if item not in sports_breaking][:50 - len(sports_breaking)]

# ====================== BUILD HTML ======================
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Mitchell Post</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body { background: #121212; color: #FFFFFF; font-family: Arial, sans-serif; margin: 20px; line-height: 1.5; }
        h1 { color: #FFFFFF; margin: 0; text-decoration: underline; font-size: 2.2em; }
        .byline { color: #aaaaaa; font-size: 1.05em; }
        .update { color: #aaaaaa; font-size: 0.85em; }
        .section-title { color: #FF0000; font-size: 1.6em; margin: 30px 0 10px; font-weight: bold; }
        .top-divider { border: 0; height: 3px; background: #FF0000; margin: 35px 0; }
        .headline { margin-bottom: 18px; padding-bottom: 10px; border-bottom: 1px solid #222222; }
        .title { color: #FFFFFF; }
        .link { color: #F6CB2F; text-decoration: underline; font-size: 0.85em; margin-left: 10px; }
        .container { display: flex; flex-wrap: wrap; gap: 30px; max-width: 1400px; margin: 0 auto; }
        .column { flex: 1; min-width: 300px; }
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
            <h2 class="section-title">Breaking US News (last 4 hours)</h2>
"""

if us_breaking:
    for ts, title, source, link in us_breaking:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking US news in the last 4 hours.</p>\n'

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
            <h2 class="section-title">Middle East Breaking News (last 4 hours)</h2>
"""

if middle_breaking:
    for ts, title, source, link in middle_breaking:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking Middle East news in the last 4 hours.</p>\n'

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
    html += '<p>No additional Middle East headlines right now.</p>\n'

html += """
        </div>
    </div>

    <hr class="top-divider">

    <!-- SPORTS -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Sports Breaking News (last 4 hours)</h2>
"""

if sports_breaking:
    for ts, title, source, link in sports_breaking:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking sports news in the last 4 hours.</p>\n'

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
    print("✅ SUCCESS: index.html updated with up to 50 articles per column")
except Exception as e:
    print(f"❌ ERROR writing file: {e}")

print("Script finished - GitHub Actions can now commit this index.html")