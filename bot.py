import feedparser
import time
import os
import re
import urllib.request
from datetime import datetime, timedelta
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
}

def get_friendly_source(raw_name):
    for key in SOURCE_MAP:
        if key.lower() in raw_name.lower():
            return SOURCE_MAP[key]
    return raw_name.split(" - ")[-1].strip() if " - " in raw_name else raw_name

# ====================== KEYWORDS (your lists) ======================
# Middle East (unchanged)
RAW_ME_KEYWORDS = ["middle east", "middle east news", "arab world", "gulf states", "gulf cooperation council", "gcc countries", "levant region", "maghreb region", "mena region", "persian gulf", "arabian peninsula", "west asia", "red sea region", "iran", "iranian", "tehran", "qom", "mashhad", "isfahan", "tabriz", "khuzestan", "israel", "israeli", "jerusalem", "tel aviv", "west bank", "gaza strip", "golan heights", "saudi arabia", "saudi", "riyadh", "jeddah", "neom", "vision 2030", "united arab emirates", "uae", "emirates", "abu dhabi", "dubai", "sharjah", "qatar", "doha", "kuwait", "kuwait city", "oman", "muscat", "bahrain", "manama", "iraq", "iraqi", "baghdad", "basra", "mosul", "kurdistan iraq", "erbil", "syria", "syrian", "damascus", "aleppo", "idlib", "lebanon", "lebanese", "beirut", "jordan", "amman", "turkey", "turkish", "ankara", "istanbul", "egypt", "egyptian", "cairo", "alexandria", "yemen", "yemeni", "sanaa", "aden", "palestine", "palestinian", "ramallah", "khamenei", "mojtabakhamenei", "mojta ba khamenei", "ayatollah", "supreme leader iran", "president iran", "pezeshkian", "benjamin netanyahu", "netanyahu government", "israeli war cabinet", "mohammed bin salman", "mbs saudi", "saudi crown prince", "mohammed bin zayed", "mbz", "recep tayyip erdogan", "abdel fattah el sisi", "tamim bin hamad al thani", "king abdullah jordan", "bashar al assad", "middle east war", "regional war middle east", "military escalation middle east", "proxy war middle east", "militia middle east", "airstrike middle east", "drone strike middle east", "missile attack middle east", "ballistic missile middle east", "naval clash middle east", "red sea shipping attack", "military buildup middle east", "troop deployment middle east", "hezbollah", "hamas", "palestinian islamic jihad", "irgc", "islamic revolutionary guard corps", "houthis", "ansar allah", "popular mobilization forces", "pmf iraq", "al qaeda arabian peninsula", "aqap", "isis", "isis-k", "islamic state", "gaza war", "israel gaza war", "gaza ceasefire", "israel lebanon border conflict", "israel hezbollah conflict", "yemen civil war", "red sea crisis", "syria civil war", "idlib offensive", "iraq militia attacks", "iran israel shadow war", "iran nuclear program", "uranium iran", "uranium enrichment", "nuclear breakout time", "iran centrifuges", "natanz nuclear facility", "fordow nuclear facility", "iaea iran", "nuclear inspections iran", "jcpoa", "iran nuclear deal", "snapback sanctions", "ballistic missile program iran", "hypersonic missile iran", "brent crude", "wti crude", "oil supply disruption", "opec", "opec+", "oil tanker attack", "tanker seizure", "hormuz blockade", "strait hormuz", "red sea shipping", "suez canal shipping", "lng exports qatar", "saudi oil production", "kharg island", "iran oil exports", "us middle east policy", "us centcom", "centcom iran", "centcom strikes", "us military bases middle east", "american troops iraq", "us troops syria", "russia middle east policy", "russia syria military", "china middle east diplomacy", "china iran deal", "belt and road middle east", "abraham accords", "israel normalization", "saudi israel normalization", "arab league", "iran saudi relations", "iran china mediation", "turkey nato middle east", "iran protest", "iran unrest", "iran revolution", "arab spring", "middle east protests", "economic protests middle east", "government crackdown middle east", "regime change middle east", "political prisoners middle east", "shia islam", "sunni islam", "religious authority iran", "hajj pilgrimage", "mecca pilgrimage", "islamic scholarship middle east", "religious tensions middle east", "drone warfare middle east", "iran drones", "shahed drone", "cyber attack middle east", "cyber warfare israel iran", "ai military middle east", "missile defense israel", "iron dome", "arrow missile defense", "neom saudi", "saudi giga projects", "uae space program", "dubai real estate boom", "qatar world cup legacy", "middle east infrastructure", "refugee crisis middle east", "syrian refugees", "gaza humanitarian crisis", "famine yemen", "water crisis middle east", "climate change middle east", "desertification middle east", "breaking news middle east", "middle east analysis", "middle east geopolitics", "middle east conflict update", "middle east security update", "regional escalation", "gray zone conflict", "proxy warfare", "strategic deterrence", "regional balance of power", "maritime security gulf", "energy security middle east", "october 7 attack", "october 7 israel attack", "hamas october 7", "gaza ground offensive", "rafah offensive", "rafah crossing", "rafah evacuation", "gaza reconstruction", "gaza displacement", "gaza hostage crisis", "israeli hostages", "hostage negotiations gaza", "prisoner exchange israel hamas", "ceasefire negotiations gaza", "humanitarian corridor gaza", "gaza aid convoy", "gaza famine warning", "gaza refugee camps", "west bank raids", "settler violence west bank", "west bank escalation", "lebanon front escalation", "israel lebanon war risk", "hezbollah rocket barrage", "hezbollah precision missiles", "northern israel evacuation", "blue line conflict", "iran proxy network", "axis of resistance", "iran proxy war", "iran regional militias", "iran leadership crisis", "iran power struggle", "iran succession crisis", "post khamenei iran", "khamenei successor debate", "iran clerical leadership vacuum", "iran regime stability", "iran military leadership", "iran revolutionary guard leadership", "iran supreme leadership council", "iran transitional government speculation", "iran constitutional crisis", "iran elite power struggle", "iran hardliners vs reformists", "iran security crackdown", "iran internet blackout", "iran economic collapse", "iran rial crisis", "iran capital flight", "iran sanctions evasion", "iran shadow fleet", "iran tanker fleet", "iran drone exports", "iran russia drone deal", "iran china strategic partnership", "iran missile stockpile", "iran underground bases", "iran retaliation israel", "israel strike iran", "israel iran escalation", "israel preemptive strike iran", "israel nuclear red line", "regional escalation scenario", "persian gulf naval standoff", "gulf tanker war", "red sea naval task force", "maritime coalition red sea", "houthi missile attacks shipping", "houthi drone attacks ships", "bab el mandeb strait crisis", "global shipping disruption red sea", "insurance crisis shipping middle east", "oil shock risk middle east", "energy market shock middle east", "refugee flows middle east war", "regional war scenario middle east", "multi front war israel", "israel gaza lebanon war", "israel iran direct conflict", "iran retaliation scenario", "middle east escalation timeline", "middle east war forecast", "middle east geopolitical risk", "strategic chokepoints middle east", "global oil chokepoints", "hormuz crisis scenario", "red sea blockade scenario", "eastern mediterranean gas fields", "levant gas dispute", "cyprus gas exploration", "turkey greece eastern mediterranean tensions", "middle east arms race", "missile proliferation middle east", "drone proliferation middle east", "regional nuclear proliferation", "saudi nuclear program", "uae nuclear program", "middle east security architecture", "us carrier strike group middle east", "aircraft carrier persian gulf", "strategic bombing middle east", "bunker buster strike iran", "underground nuclear facility iran", "intelligence leaks middle east conflict", "satellite imagery iran bases", "osint iran military", "war games middle east scenario", "think tank analysis middle east conflict", "geopolitical forecasting middle east", "global markets reaction middle east war", "oil price spike middle east conflict", "defense spending middle east", "military mobilization middle east", "emergency diplomacy middle east", "backchannel negotiations middle east", "crisis summit middle east leaders", "international mediation middle east conflict"]
ME_KEYWORDS = set(word.lower() for kw in RAW_ME_KEYWORDS for word in kw.split())

# US Politics (updated with your new list)
RAW_US_KEYWORDS = ["us politics", "american politics", "federal government", "state government", "local government", "congress news", "senate news", "house of representatives", "supreme court rulings", "scotus decisions", "federal court cases", "district court rulings", "appellate court rulings", "executive orders", "white house briefing", "presidential address", "press secretary briefing", "election news", "election updates", "election coverage", "presidential election", "midterm elections", "senate races", "house races", "governor races", "mayoral races", "ballot initiatives", "referendums", "voter turnout", "voter suppression", "election integrity", "mail in voting", "absentee ballots", "early voting", "voter id laws", "electoral college", "swing states", "battleground states", "red states", "blue states", "purple states", "political polling", "approval ratings", "favorability ratings", "policy proposals", "legislative agenda", "bipartisan bill", "partisan divide", "filibuster", "budget reconciliation", "government shutdown", "federal budget", "national debt", "deficit spending", "tax reform", "irs policy", "corporate tax", "income tax", "capital gains tax", "inflation rate", "cpi inflation", "ppi inflation", "interest rates", "federal reserve policy", "fed rate hike", "fed rate cuts", "unemployment rate", "job growth", "labor market", "wage growth", "housing market", "mortgage rates", "rent prices", "real estate trends", "housing affordability", "homelessness policy", "healthcare policy", "medicare", "medicaid", "affordable care act", "obamacare", "drug pricing", "prescription costs", "public health policy", "pandemic response", "vaccine policy", "immigration policy", "border security", "asylum policy", "deportation policy", "daca", "visa policy", "refugee policy", "foreign policy", "us china relations", "us russia relations", "us iran policy", "middle east policy", "nato policy", "defense spending", "military budget", "pentagon news", "national security", "intelligence community", "cia", "fbi", "nsa", "homeland security", "cybersecurity policy", "cyber attacks", "infrastructure security", "critical infrastructure", "energy policy", "oil production", "gas prices", "renewable energy", "solar power", "wind energy", "nuclear energy policy", "climate change policy", "carbon emissions", "environmental protection", "epa regulations", "water policy", "agriculture policy", "farm bill", "food supply chain", "trade policy", "tariffs", "global trade", "supply chain disruptions", "manufacturing policy", "industrial policy", "antitrust law", "big tech regulation", "ai regulation", "data privacy law", "section 230", "social media policy", "digital rights", "free speech law", "first amendment cases", "second amendment cases", "gun control policy", "gun rights", "crime rates", "policing policy", "criminal justice reform", "prison reform", "sentencing laws", "drug policy", "opioid crisis", "fentanyl crisis", "education policy", "student loans", "tuition costs", "k-12 education", "curriculum debates", "school funding", "charter schools", "culture war issues", "gender policy", "civil rights", "voting rights act", "discrimination law", "supreme court nominations", "judicial appointments", "political scandals", "ethics investigations", "lobbying", "lobbying disclosure", "campaign finance", "super pacs", "dark money", "election interference", "misinformation", "disinformation", "media bias", "journalism ethics", "breaking news us", "live news updates", "policy analysis", "political analysis", "expert commentary", "think tank reports", "government data releases", "economic indicators", "consumer confidence", "retail sales", "manufacturing index", "housing starts", "building permits", "transportation policy", "infrastructure bill", "highways funding", "public transit", "aviation policy", "airline industry", "faa regulation", "ev policy", "electric vehicles", "automotive regulation", "tech innovation policy", "space policy", "nasa missions", "spacex policy", "telecommunications policy", "5g rollout", "broadband access", "rural internet", "urban development", "zoning laws", "land use policy", "disaster response", "emergency management", "fema response", "wildfire policy", "hurricane response", "climate disasters", "insurance markets", "banking regulation", "financial markets", "stock market news", "dow jones", "s&p 500", "nasdaq", "earnings reports", "corporate governance", "mergers and acquisitions", "startup funding", "venture capital", "labor unions", "strikes", "labor disputes", "minimum wage", "gig economy", "workplace regulation", "osha policy", "diversity equity inclusion policy", "government oversight", "inspector general reports", "whistleblower cases", "transparency", "freedom of information act", "foia requests", "investigative journalism", "watchdog reporting", "accountability journalism", "fact checking", "verification", "primary sources", "official statements", "transcripts", "press releases", "data journalism", "open data", "public records", "expert analysis", "academic research policy", "peer reviewed studies", "policy outcomes", "longitudinal studies", "trend analysis", "scenario planning", "risk assessment", "geopolitical risk", "economic outlook", "future forecasts", "us economy", "economic growth", "recession risk", "soft landing economy", "hard landing economy", "fiscal policy", "monetary policy", "consumer spending", "supply and demand", "productivity growth", "manufacturing output", "services sector", "small business trends", "corporate layoffs", "hiring trends", "job openings", "labor participation rate", "unionization trends", "antitrust cases", "monopoly regulation", "tech monopolies", "platform regulation", "social media companies", "content moderation", "digital censorship", "online speech", "misinformation campaigns", "election security", "voting machines", "cybersecurity threats", "hacking incidents", "ransomware attacks", "data breaches", "identity theft", "privacy concerns", "surveillance policy", "facial recognition law", "biometric data", "border surveillance", "immigration raids", "sanctuary cities", "deportation flights", "refugee intake", "asylum backlog", "immigration courts", "border wall policy", "foreign aid", "military alliances", "defense contracts", "arms sales", "weapons systems", "drone warfare", "cyber warfare", "space force", "nuclear policy", "arms control treaties", "sanctions policy", "trade agreements", "export controls", "tariffs china", "tariffs europe", "trade war", "global markets", "currency exchange", "dollar strength", "inflation expectations", "bond market", "treasury yields", "housing affordability crisis", "urban housing crisis", "rural housing issues", "infrastructure investment", "public works projects", "transportation funding", "rail systems", "high speed rail", "airline safety", "aviation incidents", "supply chain logistics", "port congestion", "trucking industry", "fuel prices", "energy independence", "oil reserves", "strategic petroleum reserve", "clean energy transition", "green energy policy", "climate legislation", "emissions targets", "carbon pricing", "environmental justice", "water shortages", "drought conditions", "wildfire seasons", "hurricane tracking", "disaster recovery funding", "insurance premiums", "banking stability", "financial regulation", "fintech innovation", "cryptocurrency regulation", "digital assets", "blockchain policy", "central bank digital currency", "cbdc policy", "ai innovation", "ai startups", "ai governance", "automation jobs", "future of work", "remote work policy", "hybrid work trends", "workplace productivity", "labor shortages", "skills gap", "education reform", "charter school expansion", "public school funding", "higher education policy", "student debt relief", "loan forgiveness", "campus protests", "academic freedom", "free speech campuses", "civil liberties", "human rights us", "police reform", "qualified immunity", "incarceration rates", "prison conditions", "parole policy", "rehabilitation programs", "drug legalization", "marijuana policy", "border fentanyl trafficking", "healthcare costs", "insurance coverage", "hospital systems", "medical workforce", "telehealth expansion", "pharmaceutical industry", "drug approvals", "fda policy", "pandemic preparedness", "vaccine rollout", "disease outbreaks", "public health emergencies", "science funding", "research grants", "innovation policy", "space exploration", "satellite systems", "gps systems", "telecommunications law", "internet access", "digital divide", "rural broadband expansion", "urban infrastructure", "smart cities", "technology adoption", "consumer tech policy", "product safety", "recalls", "supply shortages", "retail trends", "consumer confidence index", "holiday shopping trends", "black friday sales", "cyber monday sales", "economic forecasts", "policy debates", "public hearings", "committee investigations", "special counsel investigations", "ethics violations", "campaign violations", "political donations", "fundraising totals", "election ads", "media coverage", "press conferences", "interviews politicians", "debate performances", "primary elections", "caucuses", "delegate counts", "convention news", "party platforms", "republican party news", "democratic party news", "independent candidates", "third party politics", "libertarian party", "green party", "political ideology", "conservatism", "liberalism", "populism", "nationalism", "globalization", "isolationism", "political polarization", "bipartisan cooperation", "legislative gridlock", "judicial review", "constitutional amendments", "civil cases", "criminal cases", "legal precedent", "supreme court majority", "dissenting opinions", "oral arguments", "legal briefs", "case filings", "appeals process", "justice department investigations", "attorney general actions", "federal prosecutions", "white collar crime", "corporate fraud", "insider trading", "financial crime", "public corruption", "ethics reforms", "transparency initiatives", "whistleblower protections", "government accountability", "public trust government", "civic participation", "voter registration", "turnout efforts", "campaign volunteering", "grassroots activism", "political organizing", "community engagement", "public forums", "town meetings", "citizen initiatives", "public referenda", "civic tech", "open government", "transparency data", "watchdog groups", "nonprofit reporting", "independent journalism", "media ecosystem", "news consumption trends", "information credibility", "source verification", "fact based reporting", "evidence based policy", "expert interviews", "data driven journalism", "public records access", "foia disclosures", "leak investigations", "insider information politics", "anonymous sources politics", "insider reports washington", "beltway politics", "washington insiders", "capitol hill updates", "white house insiders", "agency insiders", "whistleblower leaks", "classified document cases", "document mishandling investigations", "national archives disputes", "legal exposure politicians", "indictment news politicians", "criminal charges politicians", "court appearances politicians", "plea deals politics", "sentencing politicians", "legal defense teams politics", "constitutional challenges", "supreme court appeals", "precedent setting cases", "landmark rulings", "legal interpretation debates", "judicial philosophy", "originalism debate", "living constitution debate", "separation of church and state", "executive privilege claims", "congressional oversight authority", "subpoena enforcement", "contempt of congress", "impeachment proceedings", "articles of impeachment", "senate trial impeachment", "acquittal conviction impeachment", "political fallout impeachment", "public opinion impeachment", "historical comparisons impeachment", "american culture", "us culture trends", "pop culture us", "cultural trends america", "media landscape us", "news media trends", "cable news ratings", "streaming news consumption", "independent journalism growth", "alternative media platforms", "podcast popularity politics", "youtube political channels", "tiktok political trends", "viral news clips", "breaking news alerts", "real time reporting", "live press conferences", "white house live stream", "congressional live stream", "senate hearings live", "house hearings live", "court hearings live", "supreme court live audio", "emergency alerts us", "national emergency updates", "federal alerts", "state emergency alerts", "local breaking news", "crime news us", "local crime reports", "major crime cases", "high profile trials", "court verdicts", "jury decisions", "sentencing hearings", "police investigations", "fbi investigations", "doj investigations", "corruption cases", "bribery scandals", "fraud cases", "insider trading cases", "corporate scandals", "tech scandals", "banking scandals", "government scandals", "political corruption", "ethics violations", "watchdog investigations", "inspector general reports", "whistleblower disclosures", "transparency reports", "accountability reports", "government audits", "oversight committees", "congressional investigations", "special committees", "select committee hearings", "bipartisan investigations", "independent commissions", "public inquiry reports", "historical investigations", "national security briefings", "intelligence reports", "threat assessments", "homeland security alerts", "terror threat levels", "counterterrorism operations", "domestic extremism", "international terrorism", "cyber threats", "cyber espionage", "foreign intelligence operations", "espionage cases", "surveillance programs", "privacy concerns us", "civil liberties debates", "constitutional rights debates", "first amendment rights", "second amendment rights", "fourth amendment rights", "due process rights", "equal protection clause", "civil rights movements", "social justice movements", "protest coverage", "demonstrations us", "nationwide protests", "campus protests", "labor strikes", "union actions", "worker protests", "economic protests", "political rallies", "campaign rallies", "town halls live", "voter engagement events", "civic participation campaigns", "voter registration drives", "get out the vote efforts", "grassroots movements", "community organizing", "nonprofit advocacy", "advocacy campaigns", "lobbying campaigns", "public awareness campaigns", "issue advocacy", "political messaging campaigns", "media narratives shaping", "framing effects media", "information warfare", "propaganda analysis", "disinformation tracking", "fact check viral claims", "debunking misinformation", "source credibility analysis", "media literacy", "journalism standards", "editorial standards", "corrections policies", "retractions news", "accountability journalism standards", "investigative reporting methods", "data verification", "primary source verification", "public records access", "foia disclosures", "leak investigations", "insider information politics", "anonymous sources verification", "expert panel discussions", "policy expert interviews", "think tank analysis reports", "academic research publications", "peer review studies policy", "longitudinal policy studies", "statistical modeling politics", "predictive analytics elections", "forecasting elections", "polling aggregators", "polling averages", "trendline analysis politics", "sentiment analysis politics", "social media sentiment", "voter sentiment tracking", "demographic breakdown polling", "age group voting trends", "income level voting trends", "education level voting trends", "geographic voting patterns", "urban voting patterns", "suburban voting patterns", "rural voting patterns", "regional political trends", "state by state analysis", "county level results", "precinct level results", "electoral shifts", "realignment politics", "coalition building politics", "party strategy shifts", "ideological shifts us", "progressive movement", "conservative movement", "libertarian movement", "populist movement", "centrist politics", "moderate voters", "swing voters influence", "independent voter trends", "partisan loyalty", "party identification trends", "political branding", "candidate branding", "image management politics", "crisis communication politics", "damage control messaging", "rapid response teams politics", "opposition messaging", "negative campaigning", "attack ads", "campaign narratives", "storytelling politics", "speechwriting strategy", "rhetorical framing", "public persuasion techniques", "media appearances strategy", "interview strategy politics", "debate preparation", "mock debates", "talking points strategy", "policy communication", "legislative messaging", "executive messaging", "judicial messaging", "public relations campaigns government", "reputation management politics", "approval rating tracking", "disapproval rating trends", "favorability shifts", "trust in government", "institutional trust", "trust in media", "polarization metrics", "polarization studies", "echo chambers media", "filter bubbles", "algorithm influence news", "platform algorithms politics", "content distribution news", "virality factors politics", "news amplification", "media bias analysis", "ideological bias tracking", "balanced reporting standards", "neutrality in journalism", "objectivity standards", "sourcing standards journalism", "editorial independence", "newsroom practices", "newsroom ethics", "reporting guidelines", "corrections tracking", "transparency in reporting", "public editor reports", "ombudsman reviews", "audience trust metrics", "subscriber trends news", "paywall journalism", "nonprofit journalism models", "public broadcasting funding", "media ownership structures", "consolidation media", "independent outlets growth", "startup journalism", "local news decline", "news deserts", "regional news coverage", "hyperlocal journalism", "investigative series", "longform reporting", "documentary journalism", "multimedia journalism", "data visualization news", "graphics reporting", "interactive journalism", "live blogs news", "real time updates politics", "breaking alerts system", "push notification news", "daily briefings politics", "morning newsletters", "evening recaps", "weekly political analysis", "monthly outlook reports", "annual political forecasts", "election cycle tracking", "policy cycle tracking", "legislative calendar", "congressional schedule", "court calendar", "regulatory calendar", "budget cycle", "fiscal year planning", "appropriations timeline", "campaign calendar", "primary calendar updates", "caucus timing", "debate schedule", "convention planning", "inauguration timeline", "transition planning government", "cabinet formation process", "agency leadership appointments", "senate confirmations", "confirmation hearings", "appointment controversies", "resignations politics", "firings politics", "leadership changes government", "succession planning politics", "emergency succession plans", "continuity of government", "crisis governance", "disaster governance", "wartime governance", "emergency powers", "executive authority limits", "legislative authority limits", "judicial authority limits", "constitutional crises", "separation of powers conflict", "checks and balances disputes", "federal vs state power", "state sovereignty debates", "interstate conflicts policy", "federal mandates", "state resistance policies", "legal challenges states", "supreme court appeals states", "constitutional amendments proposals", "amendment ratification process", "constitutional interpretation debates", "legal scholarship constitutional law", "judicial review analysis", "precedent analysis law", "landmark case analysis", "comparative constitutional law", "international law us", "treaty obligations us", "global governance role us", "diplomatic relations tracking", "embassy activity", "consulate activity", "diplomatic statements", "foreign leader meetings us", "summit coverage", "international agreements", "sanctions enforcement tracking", "export control enforcement", "border policy enforcement", "immigration enforcement actions", "customs enforcement", "trade enforcement", "economic sanctions impact", "global economic impact us policy", "domestic economic impact policy", "social impact policy", "long term policy outcomes", "policy success metrics", "policy failure analysis", "reform proposals", "legislative reforms", "regulatory reforms", "institutional reforms", "governance innovation", "digital government", "e government services", "public service delivery", "government efficiency", "bureaucratic reform", "performance metrics government", "accountability mechanisms", "transparency initiatives", "anti corruption measures", "ethics reforms government", "public sector innovation", "civic technology tools", "open data platforms", "digital transparency", "citizen engagement platforms"]
US_KEYWORDS = set(word.lower() for kw in RAW_US_KEYWORDS for word in kw.split())

# Sports (updated with your new list)
RAW_SPORTS_KEYWORDS = ["march madness", "college basketball", "arizona wildcats", "purdue boilermakers", "miami hurricanes", "villanova wildcats", "utah state aggies", "ncaa tournament", "college basketball crown", "ncaa bracket", "march madness bracket", "sports news", "latest sports news", "breaking sports news", "football news", "nfl news", "nba news", "mlb news", "nhl news", "soccer news", "premier league news", "champions league news", "world cup news", "fifa world cup", "copa america", "euro cup", "la liga news", "serie a news", "bundesliga news", "mls news", "college football news", "college basketball news", "nba finals", "super bowl", "world series", "stanley cup", "olympics news", "olympics schedule", "olympics results", "summer olympics", "winter olympics", "tennis news", "grand slam tennis", "wimbledon news", "us open tennis", "australian open tennis", "french open tennis", "atp rankings", "wta rankings", "formula 1 news", "f1 standings", "f1 race results", "f1 qualifying", "f1 drivers", "lewis hamilton news", "max verstappen news", "ferrari f1", "mercedes f1", "red bull racing", "golf news", "pga tour news", "masters tournament", "us open golf", "british open golf", "ryder cup", "tiger woods news", "surfing news", "world surf league", "surfing competitions", "big wave surfing", "surf forecast", "nba trade rumors", "nfl trade rumors", "mlb trades", "transfer rumors soccer", "transfer window", "player injuries", "injury report nfl", "nba injury report", "fantasy football", "fantasy basketball", "fantasy sports news", "betting odds sports", "sports betting news", "esports news", "competitive gaming sports", "college recruiting news", "draft prospects nfl", "nba draft news", "mlb draft", "nhl draft", "sports analytics", "advanced stats sports", "player statistics", "team standings", "league standings", "power rankings", "sports highlights", "game recap", "post match analysis", "sports commentary", "sports podcasts", "athlete interviews", "locker room news", "coaching changes", "head coach firing", "sports scandals", "doping scandals", "anti doping agency", "olympic doping cases", "sports law", "contract negotiations", "player contracts", "salary cap nfl", "salary cap nba", "free agency news", "transfer fees soccer", "youth academy soccer", "academy prospects", "sports development programs", "women sports news", "wnba news", "women soccer news", "women tennis news", "women golf news", "title ix sports", "college athletics news", "ncaa rules", "nil deals college athletes", "sponsorship deals athletes", "endorsement deals athletes", "sports marketing", "sports media rights", "broadcasting deals sports", "streaming sports", "live sports streaming", "sports tv ratings", "fan attendance sports", "stadium news", "arena construction", "sports business news", "franchise valuations", "team ownership news", "sports mergers", "league expansion", "expansion teams", "relocation teams", "sports history", "greatest athletes", "hall of fame sports", "olympic history", "world records sports", "track and field news", "marathon running news", "cycling tour de france", "cycling news", "boxing news", "mma news", "ufc fights", "fight night results", "boxing title fights", "heavyweight boxing", "featherweight ufc", "sports injuries recovery", "athlete training", "sports science", "biomechanics sports", "nutrition athletes", "fitness training sports", "sports psychology", "mental health athletes", "fan reactions sports", "social media sports trends", "viral sports moments", "sports controversies", "referee decisions", "var decisions soccer", "instant replay sports", "officiating controversies", "sports governance", "fifa governance", "ioc decisions", "ncaa decisions", "sports politics", "geopolitics sports", "olympic boycotts", "national team news", "international friendlies", "qualifiers world cup", "regional tournaments", "asian cup soccer", "african cup nations", "concacaf gold cup", "sports rivalries", "derby matches soccer", "el clasico", "manchester derby", "nba rivalries", "nfl rivalries", "historic games sports", "buzzer beater shots", "overtime games", "penalty shootouts", "comeback victories", "underdog wins", "championship celebrations", "trophy presentations", "medal ceremonies", "sports technology", "var technology", "goal line technology", "wearable tech athletes", "performance tracking sports", "analytics software sports", "scouting reports", "talent evaluation", "combine results nfl", "pro day results", "training camp updates", "preseason games", "regular season schedule", "playoff bracket", "postseason results", "finals mvp", "league mvp", "rookie of the year", "defensive player of the year", "golden boot soccer", "ballon dor", "heisman trophy", "sports awards", "athlete retirements", "comeback stories athletes", "transfer confirmations", "contract extensions", "loan deals soccer", "sports agencies", "agent negotiations", "youth tournaments", "high school sports news", "amateur sports news", "grassroots sports", "community sports programs", "outdoor sports news", "surfing conditions", "beach conditions surfing", "swell forecast", "wind forecast surfing", "surf competitions schedule", "extreme sports news", "x games", "skateboarding news", "snowboarding news", "skiing competitions", "climbing competitions", "triathlon events", "ironman competitions", "motorsports news", "nascar news", "indycar news", "rally racing news", "endurance racing", "le mans 24 hours", "formula e news", "electric racing", "drone racing league", "sports innovation", "fan engagement sports", "ticket sales sports", "merchandise sales sports", "sports branding", "athlete branding", "media interviews athletes", "press conferences sports", "training drills", "practice sessions", "warm up routines", "game day preparation", "tactical analysis sports", "formations soccer", "playbooks nfl", "offensive schemes nba", "defensive strategies sports", "coaching tactics", "analytics driven decisions sports", "sports journalism", "sports reporting ethics", "sports documentaries", "behind the scenes sports", "locker room footage", "micd up athletes", "sports storytelling", "iconic moments sports"]
SPORTS_KEYWORDS = set(word.lower() for kw in RAW_SPORTS_KEYWORDS for word in kw.split())

# Tech and Life (your full list + the new words you just asked for)
RAW_TECH_KEYWORDS = ["technology news", "latest tech news", "emerging technology", "cutting edge technology", "future technology", "tech trends 2026", "artificial intelligence", "ai news", "ai breakthroughs", "generative ai", "machine learning", "deep learning", "neural networks", "ai regulation", "ai ethics", "robotics", "humanoid robots", "automation technology", "quantum computing", "quantum supremacy", "cloud computing", "edge computing", "cybersecurity", "data breaches", "hacking news", "ransomware attacks", "zero day exploit", "encryption technology", "blockchain technology", "cryptocurrency trends", "web3", "metaverse technology", "augmented reality", "virtual reality", "mixed reality", "spatial computing", "apple vision pro", "vr gaming", "ar glasses", "wearable technology", "smart devices", "internet of things", "iot devices", "smart home tech", "home automation", "voice assistants", "natural language processing", "big data analytics", "data science", "software development", "programming languages", "python programming", "javascript trends", "open source software", "linux news", "windows updates", "macos updates", "mobile technology", "smartphone releases", "android updates", "iphone news", "semiconductor industry", "chip shortage", "gpu technology", "cpu benchmarks", "nvidia news", "amd processors", "intel chips", "silicon valley startups", "venture capital tech", "startup funding", "tech ipo", "unicorn startups", "big tech companies", "google news", "apple news", "microsoft news", "amazon technology", "meta platforms", "social media technology", "algorithm changes", "content moderation", "digital privacy", "online security", "surveillance technology", "biometric systems", "facial recognition", "autonomous vehicles", "self driving cars", "electric vehicles", "ev battery technology", "tesla updates", "charging infrastructure", "hydrogen fuel cells", "automotive technology", "car software systems", "infotainment systems", "transportation technology", "high speed rail", "hyperloop", "aviation technology", "aircraft design", "aerospace engineering", "spacex launches", "nasa missions", "mars exploration", "moon missions", "satellite technology", "starlink internet", "space telescopes", "astrophysics discoveries", "astronomy news", "black holes", "exoplanets", "cosmology research", "physics breakthroughs", "particle physics", "cern research", "biology research", "genetics", "dna sequencing", "crispr technology", "gene editing", "biotechnology", "medical technology", "healthcare innovation", "vaccines research", "pharmaceuticals development", "neuroscience", "brain computer interfaces", "bci technology", "environmental science", "climate change research", "renewable energy", "solar power technology", "wind energy", "battery storage", "sustainability tech", "green technology", "carbon capture", "water purification", "ocean exploration", "marine biology", "wildlife conservation", "ecology research", "outdoor gear technology", "camping gear innovation", "hiking equipment", "survival gear", "gps navigation", "satellite navigation", "drones technology", "drone photography", "drone regulations", "gaming industry news", "video game releases", "game development", "game engines", "unreal engine", "unity engine", "esports news", "competitive gaming", "streaming platforms", "twitch streaming", "youtube gaming", "gaming hardware", "gaming pcs", "gaming laptops", "graphics cards", "ray tracing", "dlss technology", "vr gaming trends", "indie game development", "modding community", "digital distribution", "steam platform", "epic games store", "game monetization", "microtransactions", "gaming controversies", "entertainment technology", "streaming services", "netflix technology", "disney plus tech", "content delivery networks", "cdn technology", "5g networks", "6g research", "telecommunications technology", "fiber internet", "broadband expansion", "digital infrastructure", "smart cities technology", "urban tech innovation", "gov tech", "fintech innovation", "digital banking", "payment systems", "blockchain finance", "cybersecurity threats", "ethical hacking", "penetration testing", "devops practices", "agile development", "software engineering trends", "hardware engineering", "embedded systems", "nanotechnology", "materials science", "3d printing", "additive manufacturing", "industrial automation", "manufacturing technology", "supply chain technology", "logistics innovation", "retail technology", "e commerce trends", "digital marketing tech", "seo trends", "search algorithms", "google algorithm updates", "data privacy laws", "gdpr compliance", "digital rights", "internet governance", "future of work technology", "remote work tools", "collaboration software", "productivity tools", "human computer interaction", "user experience design", "ui ux trends", "digital transformation", "enterprise technology", "saas platforms", "cloud infrastructure", "server technology", "data centers", "green computing", "energy efficient computing", "ethical ai development", "responsible innovation", "tech policy", "government regulation tech", "antitrust tech", "innovation ecosystems", "research and development trends", "crypto", "NASA", "the ocean", "rockets", "rocket", "rocket technology", "spacecraft", "orbit", "satellite", "earth", "history", "archeology", "Grizzly bears", "Nevada", "Las Vegas", "Southwest", "Southwest United States", "cloud computing", "dinosaur", "dinosaurs", "Grok", "Open AI", "OpenAI", "NVidia", "Meta", "Artemis II", "telescope", "observatory", "Machu Picchu", "artifacts", "Thailand", "Vietnam", "Cambodia", "Southeast Asia"]
TECH_KEYWORDS = set(word.lower() for kw in RAW_TECH_KEYWORDS for word in kw.split())

# ====================== BLOCKLISTS ======================
ME_BLOCKLIST = {"trump", "harris", "biden", "congress", "senate", "house", "supreme court", "election", "midterm", "presidential", "republican", "democrat", "maga", "white house", "capitol", "washington dc", "oscars", "kennedy center", "tornadoes", "vernal equinox", "hyundai", "tsa", "airport security", "pope leo", "kentucky", "illinois primary", "michigan synagogue", "cuba", "china summit", "fcc", "sbf", "texas primaries", "nvidia", "foxconn", "walmart", "phonepe", "kushner", "sable offshore"}
US_BLOCKLIST = {"iran", "israel", "gaza", "hezbollah", "hamas", "hormuz", "khamenei", "netanyahu", "mbs", "mbz", "saudi", "uae", "qatar", "lebanon", "syria", "yemen", "palestine", "irgc", "houthis", "axis of resistance", "jcpoa", "snapback sanctions", "strait of hormuz"}
SPORTS_BLOCKLIST = ME_BLOCKLIST.union(US_BLOCKLIST)
TECH_BLOCKLIST = ME_BLOCKLIST.union(US_BLOCKLIST)

# ====================== SOURCES (updated with your new lists) ======================
MIDDLE_EAST_SOURCES = [
    ("Broad Middle East", "https://news.google.com/rss/search?q=middle+east+OR+iran+OR+israel+OR+gulf+OR+hezbollah+OR+hamas+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera", "https://news.google.com/rss/search?q=aljazeera+news+OR+al+jazeera+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Times of Israel", "https://news.google.com/rss/search?q=times+of+israel+news+OR+timesofisrael+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=reuters+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP News", "https://news.google.com/rss/search?q=ap+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NYT", "https://news.google.com/rss/search?q=nytimes+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("WSJ", "https://news.google.com/rss/search?q=wsj+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Post", "https://news.google.com/rss/search?q=washington+post+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times", "https://news.google.com/rss/search?q=financial+times+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Economist", "https://news.google.com/rss/search?q=the+economist+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC", "https://news.google.com/rss/search?q=bbc+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian", "https://news.google.com/rss/search?q=the+guardian+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg", "https://news.google.com/rss/search?q=bloomberg+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Politico", "https://news.google.com/rss/search?q=politico+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs", "https://news.google.com/rss/search?q=foreign+affairs+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

US_POLITICS_SOURCES = [
    ("Broad US Politics", "https://news.google.com/rss/search?q=donald+trump+OR+us+election+OR+congress+OR+kamala+harris+OR+joe+biden+OR+republican+OR+democrat+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP News", "https://news.google.com/rss/search?q=when:1d+site:apnews.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=when:1d+site:reuters.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("NYT", "https://news.google.com/rss/search?q=when:1d+site:nytimes.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("WSJ", "https://news.google.com/rss/search?q=when:1d+site:wsj.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Post", "https://news.google.com/rss/search?q=when:1d+site:washingtonpost.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Politico", "https://news.google.com/rss/search?q=when:1d+site:politico.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Axios", "https://news.google.com/rss/search?q=when:1d+site:axios.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg", "https://news.google.com/rss/search?q=bloomberg+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Atlantic", "https://news.google.com/rss/search?q=the+atlantic+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The New Yorker", "https://news.google.com/rss/search?q=the+new+yorker+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs", "https://news.google.com/rss/search?q=foreign+affairs+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Policy", "https://news.google.com/rss/search?q=foreign+policy+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("FiveThirtyEight", "https://news.google.com/rss/search?q=fivethirtyeight+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

SPORTS_SOURCES = [
    ("Broad Sports", "https://news.google.com/rss/search?q=march+madness+OR+college+basketball+OR+ncaa+tournament+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ESPN", "https://news.google.com/rss/search?q=espn+news+sports+OR+nfl+OR+nba+OR+mlb+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC Sport", "https://news.google.com/rss/search?q=bbc+sport+news+OR+football+OR+cricket+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sky Sports", "https://news.google.com/rss/search?q=sky+sports+news+OR+premier+league+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters Sports", "https://news.google.com/rss/search?q=reuters+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP Sports", "https://news.google.com/rss/search?q=ap+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Athletic", "https://news.google.com/rss/search?q=the+athletic+news+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sports Illustrated", "https://news.google.com/rss/search?q=when:1d+site:si.com+sports+OR+nfl+OR+nba+OR+mlb&hl=en-US&gl=US&ceid=US:en"),
]

TECH_SOURCES = [
    ("Broad Tech and Life", "https://news.google.com/rss/search?q=technology+news+OR+ai+OR+tech+OR+gaming+OR+wearable+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Wired", "https://news.google.com/rss/search?q=wired+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MIT Technology Review", "https://news.google.com/rss/search?q=mit+technology+review+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Verge", "https://news.google.com/rss/search?q=the+verge+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TechCrunch", "https://news.google.com/rss/search?q=techcrunch+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Engadget", "https://news.google.com/rss/search?q=engadget+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CNET", "https://news.google.com/rss/search?q=cnet+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ZDNet", "https://news.google.com/rss/search?q=zdnet+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("IEEE Spectrum", "https://news.google.com/rss/search?q=ieee+spectrum+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Nature", "https://news.google.com/rss/search?q=nature+news+science+OR+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== NEW CULTURE SECTION (your full list) ======================
RAW_CULTURE_KEYWORDS = ["celebrity news", "celebrity gossip", "hollywood news", "red carpet fashion", "awards show coverage", "oscars red carpet", "golden globes fashion", "emmys fashion", "met gala looks", "fashion week paris", "fashion week milan", "fashion week new york", "fashion week london", "haute couture", "ready to wear fashion", "runway shows", "supermodels", "model agency", "modeling portfolios", "model casting calls", "swimsuit models", "bikini models", "lingerie modeling", "high fashion editorial", "fashion photographers", "celebrity photographers", "paparazzi photos", "celebrity shoots", "photoshoots behind the scenes", "fashion magazines", "fashion editorials", "vogue covers", "harper’s bazaar covers", "elle magazine features", "glamour magazine features", "cosmopolitan celebrity", "gq magazine shoots", "esquire shoots", "w magazine features", "style trends", "fashion trends", "street style", "beauty trends", "makeup trends", "hair trends", "skincare trends", "celebrity style", "influencer fashion", "instagram models", "tiktok influencers", "social media celebrities", "online personalities", "streamer personalities", "content creators", "fan subscription services", "onlyfans stars", "onlyfans creators", "onlyfans content", "adult subscription content", "cam models", "webcam girls", "camming", "adult entertainers", "adult film stars", "porn stars", "adult celebrities", "porn actress news", "adult model news", "adult entertainment industry", "xbiz news", "avn awards", "porn award shows", "adult film releases", "erotica", "erotic photography", "glamour photography", "nude modeling", "bikini shoots", "swimsuit shoots", "fashion photography", "editorial shoots", "high-end fashion shoots", "luxury brand collaborations", "designer campaigns", "fashion advertising", "celebrity endorsements", "product collaborations", "influencer marketing fashion", "influencer partnerships", "beauty collaborations", "makeup influencer trends", "skincare influencer trends", "viral celebrity moments", "trending celebrities", "upcoming stars hollywood", "teen actresses", "young stars", "teen models", "rising models", "young fashion icons", "rising fashion influencers", "instagram stars", "social media rising stars", "pop culture news", "film industry news", "box office updates", "movie premieres", "movie reviews", "celebrity interviews", "behind the scenes film", "actor lifestyle", "actress lifestyle", "hollywood rumors", "film gossip", "celebrity breakups", "celebrity relationships", "celebrity dating", "celeb couples", "celebrity scandals", "red carpet moments", "hollywood fashion", "fashion critique", "runway highlights", "model lifestyle", "fitness models", "fitness influencer trends", "influencer fitness", "bikini fitness models", "swimsuit influencers", "beach photoshoots", "exotic locations shoots", "travel photography influencers", "travel fashion shoots", "luxury lifestyle influencers", "luxury fashion trends", "celebrity lifestyle trends", "fashion influencer tips", "online fame trends", "social media engagement", "digital celebrity trends", "content creation trends", "paid subscription platforms", "digital content monetization", "adult content monetization", "marketing for adult creators", "social media safety adult", "online persona management", "branding influencers", "influencer strategies", "viral content strategies", "modeling tips", "portfolio development modeling", "agency representation models", "model contracts", "casting announcements", "movie casting calls", "acting tips", "audition tips", "celeb fashion choices", "luxury fashion events", "fashion gala coverage", "beauty pageants coverage", "swimsuit competitions", "modeling competitions", "bikini contests", "modeling award shows", "top fashion influencers", "top models rankings", "top photographers ranking", "fashion photography trends", "photography lighting tips", "photography gear reviews", "camera reviews", "lens reviews", "digital photography trends", "photography tutorials", "portrait photography", "editorial photography", "fashion set photography", "glamour set photography", "nudity photography guidelines", "ethics in adult modeling", "privacy adult creators", "celebrity privacy news", "adult content creator news", "viral modeling campaigns", "influencer marketing campaigns", "film industry casting news", "upcoming hollywood movies", "streaming platform releases", "netflix celebrity features", "hbo celebrity shows", "prime video celebrities", "disney plus celebrity features", "teen tv shows", "teen movies", "young adult film news", "awards shows fashion highlights", "celebrity makeup looks", "celebrity hair trends", "fashion brand collaborations", "influencer brand collaborations", "digital fashion campaigns", "instagram fashion tips", "tiktok fashion challenges", "viral fashion content", "viral entertainment content", "fan engagement strategies", "content monetization tips", "online influencer networks", "influencer analytics tools", "social media metrics", "celebrity social media posts", "trending celebrity photos", "paparazzi updates", "viral celebrity moments", "celebrity scandals updates", "fashion commentary", "fashion review blogs", "fashion critiques online", "online modeling agencies", "webcam modeling tips", "adult industry blogs", "adult creator strategies", "adult industry reporting", "adult awards shows news", "adult performer interviews", "porn star lifestyle", "adult film production", "adult film casting", "adult content trends", "adult social media marketing", "onlyfans marketing tips", "content subscription tips", "adult influencer growth", "brand sponsorships influencers", "influencer earnings", "celebrity net worth trends", "young actress news", "teen actress coverage", "upcoming teen stars", "emerging models news", "fashion influencer rankings", "luxury influencer highlights", "viral modeling videos", "celebrity photography updates", "fashion photography trends", "photo editing trends", "digital photography influencers", "photography tutorial blogs", "modeling advice", "high fashion campaigns", "fashion editorial shoots", "bikini editorial shoots", "swimsuit fashion trends", "beachwear fashion trends", "lingerie fashion trends", "high-end swimwear brands", "luxury fashion brands", "fashion brand news", "designer news", "fashion CEO updates", "fashion industry reports", "modeling industry reports", "entertainment industry trends", "film industry analysis", "movie box office news", "celebrity endorsements fashion", "influencer collaborations fashion", "social media fashion campaigns", "fashion viral content", "entertainment viral news", "movie viral clips", "red carpet viral clips", "viral celebrity interviews", "social media viral stars", "online video content influencers", "adult content trends", "onlyfans trending creators", "adult creators ranking", "adult subscription content news", "digital creator lifestyle", "online model lifestyle", "webcam model tips", "adult monetization strategies", "fashion photographer tips", "editorial photography techniques", "celebrity shoot news", "photoshoot behind the scenes", "celebrity photoshoot updates", "luxury editorial campaigns", "high fashion set design", "celebrity stylist updates", "fashion stylist news", "styling tips", "fashion set production", "film set fashion", "fashion for film", "wardrobe stylist tips", "celebrity wardrobe updates", "high profile collaborations", "red carpet designer looks", "celebrity fashion critique", "fashion magazine editorials", "influencer interviews", "online creator interviews", "celebrity influencer updates", "viral fashion news", "viral entertainment news", "viral adult news", "fan engagement trends", "content creator trends", "trending onlyfans stars", "emerging adult creators", "social media adult trends", "fan monetization strategies", "subscription content strategies", "adult content production tips", "influencer safety online", "digital influencer growth", "teen influencer trends", "young model coverage", "emerging film stars", "up and coming actresses", "teen actress news", "high fashion model news", "bikini model news", "swimsuit model highlights", "high-end fashion influencer news", "fashion influencer tips online", "online fashion trends", "viral fashion photos", "celebrity viral videos", "social media celebrity trends", "entertainment viral content", "adult viral content", "adult content news updates", "modeling industry news", "fashion industry news", "photography industry news", "entertainment industry news", "film industry news", "influencer marketing trends", "digital content trends", "online subscription trends", "fan subscription trends", "adult entertainment trends", "high fashion trends", "luxury fashion trends", "viral celebrity fashion", "trending celebrity looks", "red carpet highlights", "fashion week highlights", "editorial shoot highlights", "photoshoot viral moments", "fashion photographer highlights", "celebrity styling trends", "fashion styling trends", "high-end fashion shoots", "online creator interviews", "influencer content interviews", "adult creator interviews", "OnlyFans news updates", "fan content trends", "subscription platform tips", "digital content creator news", "emerging influencer stars", "teen influencer coverage", "young talent coverage", "up and coming models", "up and coming actresses", "fashion brand collaborations trending", "influencer brand collaborations trending", "social media campaign insights", "celebrity campaign news", "viral campaign content", "entertainment campaign news", "celebrity viral moments", "online viral content", "fashion viral content", "modeling viral content", "adult industry viral content", "photoshoot viral updates", "behind the scenes viral updates", "celebrity lifestyle updates", "influencer lifestyle updates", "adult content creator lifestyle updates", "subscription trends", "OnlyFans trends", "adult content monetization trends", "fan subscription monetization", "digital content monetization", "emerging stars trends", "rising models trends", "rising actors trends", "teen actress trends", "teen influencer trends", "high fashion model trends", "bikini model trends", "swimsuit model trends", "lingerie model trends", "glamour model trends", "editorial model trends", "fashion model trends", "fashion photography trends", "editorial photography trends", "adult photography trends", "viral adult photography", "celebrity viral photography", "photoshoot viral content", "viral content creation", "digital content viral trends", "fan engagement viral trends", "content monetization viral trends", "adult content viral trends"]
CULTURE_KEYWORDS = set(word.lower() for kw in RAW_CULTURE_KEYWORDS for word in kw.split())

CULTURE_BLOCKLIST = ME_BLOCKLIST.union(US_BLOCKLIST).union(SPORTS_BLOCKLIST)

CULTURE_SOURCES = [
    ("Broad Culture", "https://news.google.com/rss/search?q=celebrity+news+OR+hollywood+OR+fashion+week+OR+met+gala+OR+red+carpet+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TMZ", "https://news.google.com/rss/search?q=tmz+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("E! News", "https://news.google.com/rss/search?q=e!+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("People Magazine", "https://news.google.com/rss/search?q=people+magazine+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Vanity Fair", "https://news.google.com/rss/search?q=vanity+fair+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Vogue", "https://news.google.com/rss/search?q=vogue+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Harper’s Bazaar", "https://news.google.com/rss/search?q=harpers+bazaar+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Elle", "https://news.google.com/rss/search?q=elle+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Cosmopolitan", "https://news.google.com/rss/search?q=cosmopolitan+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Glamour", "https://news.google.com/rss/search?q=glamour+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("GQ", "https://news.google.com/rss/search?q=gq+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Esquire", "https://news.google.com/rss/search?q=esquire+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("W Magazine", "https://news.google.com/rss/search?q=w+magazine+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Cut", "https://news.google.com/rss/search?q=the+cut+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Refinery29", "https://news.google.com/rss/search?q=refinery29+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Just Jared", "https://news.google.com/rss/search?q=just+jared+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hollywood Reporter", "https://news.google.com/rss/search?q=hollywood+reporter+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Variety", "https://news.google.com/rss/search?q=variety+news+hollywood+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Deadline", "https://news.google.com/rss/search?q=deadline+hollywood+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Entertainment Weekly", "https://news.google.com/rss/search?q=entertainment+weekly+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Billboard", "https://news.google.com/rss/search?q=billboard+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Rolling Stone", "https://news.google.com/rss/search?q=rolling+stone+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Pitchfork", "https://news.google.com/rss/search?q=pitchfork+news+music+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Complex", "https://news.google.com/rss/search?q=complex+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("IGN Entertainment", "https://news.google.com/rss/search?q=ign+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Screen Rant", "https://news.google.com/rss/search?q=screen+rant+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Collider", "https://news.google.com/rss/search?q=collider+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("IndieWire", "https://news.google.com/rss/search?q=indiewire+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Film Threat", "https://news.google.com/rss/search?q=film+threat+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Rotten Tomatoes", "https://news.google.com/rss/search?q=rotten+tomatoes+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Metacritic", "https://news.google.com/rss/search?q=metacritic+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Flickering Myth", "https://news.google.com/rss/search?q=flickering+myth+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Playlist", "https://news.google.com/rss/search?q=the+playlist+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Empire Magazine", "https://news.google.com/rss/search?q=empire+magazine+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Premiere Magazine", "https://news.google.com/rss/search?q=premiere+magazine+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Luxuo", "https://news.google.com/rss/search?q=luxuo+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Fashionista", "https://news.google.com/rss/search?q=fashionista+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Business of Fashion", "https://news.google.com/rss/search?q=the+business+of+fashion+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Models.com", "https://news.google.com/rss/search?q=models.com+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Supermodels.nl", "https://news.google.com/rss/search?q=supermodels.nl+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Style.com", "https://news.google.com/rss/search?q=style.com+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Glamour UK", "https://news.google.com/rss/search?q=glamour+uk+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Nylon Magazine", "https://news.google.com/rss/search?q=nylon+magazine+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Teen Vogue", "https://news.google.com/rss/search?q=teen+vogue+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("I-D Magazine", "https://news.google.com/rss/search?q=i-d+magazine+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Dazed Magazine", "https://news.google.com/rss/search?q=dazed+magazine+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Pop Sugar", "https://news.google.com/rss/search?q=popsugar+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Refinery29 UK", "https://news.google.com/rss/search?q=refinery29+uk+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Buzzfeed Entertainment", "https://news.google.com/rss/search?q=buzzfeed+entertainment+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Daily Mail Entertainment", "https://news.google.com/rss/search?q=daily+mail+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Metro UK Entertainment", "https://news.google.com/rss/search?q=metro+uk+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("OK Magazine", "https://news.google.com/rss/search?q=ok+magazine+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("US Weekly", "https://news.google.com/rss/search?q=us+weekly+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Star Magazine", "https://news.google.com/rss/search?q=star+magazine+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Celebrity Insider", "https://news.google.com/rss/search?q=celebrity+insider+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hollywood Life", "https://news.google.com/rss/search?q=hollywood+life+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Just Jared Jr", "https://news.google.com/rss/search?q=just+jared+jr+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("PopSugar Celebrity", "https://news.google.com/rss/search?q=popsugar+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Sun Celebrity", "https://news.google.com/rss/search?q=the+sun+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Heat Magazine", "https://news.google.com/rss/search?q=heat+magazine+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Daily Star Celebrity", "https://news.google.com/rss/search?q=daily+star+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Cosmopolitan UK", "https://news.google.com/rss/search?q=cosmopolitan+uk+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Independent Arts", "https://news.google.com/rss/search?q=the+independent+arts+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian Arts", "https://news.google.com/rss/search?q=the+guardian+arts+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC Culture", "https://news.google.com/rss/search?q=bbc+culture+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("New York Times Arts", "https://news.google.com/rss/search?q=new+york+times+arts+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Los Angeles Times Entertainment", "https://news.google.com/rss/search?q=los+angeles+times+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Variety Latino", "https://news.google.com/rss/search?q=variety+latino+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hollywood Reporter Latin", "https://news.google.com/rss/search?q=hollywood+reporter+latin+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Deadline Hollywood", "https://news.google.com/rss/search?q=deadline+hollywood+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Filmfare", "https://news.google.com/rss/search?q=filmfare+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Pinkvilla", "https://news.google.com/rss/search?q=pinkvilla+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Indian Express Entertainment", "https://news.google.com/rss/search?q=indian+express+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("DNA India Entertainment", "https://news.google.com/rss/search?q=dna+india+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Vogue India", "https://news.google.com/rss/search?q=vogue+india+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Elle India", "https://news.google.com/rss/search?q=elle+india+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("GQ India", "https://news.google.com/rss/search?q=gq+india+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Playboy", "https://news.google.com/rss/search?q=playboy+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hustler", "https://news.google.com/rss/search?q=hustler+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Penthouse", "https://news.google.com/rss/search?q=penthouse+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("XBIZ", "https://news.google.com/rss/search?q=xbiz+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AVN Magazine", "https://news.google.com/rss/search?q=avn+magazine+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Adult Video News", "https://news.google.com/rss/search?q=adult+video+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MyFreeCams Blog", "https://news.google.com/rss/search?q=myfreecams+blog+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("OnlyFans Blog", "https://news.google.com/rss/search?q=onlyfans+blog+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Fancenters", "https://news.google.com/rss/search?q=fancenters+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Pornhub News", "https://news.google.com/rss/search?q=pornhub+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Xhamster News", "https://news.google.com/rss/search?q=xhamster+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Redtube News", "https://news.google.com/rss/search?q=redtube+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AdultIndustryTimes", "https://news.google.com/rss/search?q=adultindustrytimes+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("EscortNews", "https://news.google.com/rss/search?q=escortnews+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("EscortDaily", "https://news.google.com/rss/search?q=escortdaily+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Glamour Models Magazine", "https://news.google.com/rss/search?q=glamour+models+magazine+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bikini Models Magazine", "https://news.google.com/rss/search?q=bikini+models+magazine+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Swimsuit International", "https://news.google.com/rss/search?q=swimsuit+international+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Fashion Model Directory", "https://news.google.com/rss/search?q=fashion+model+directory+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Model Management", "https://news.google.com/rss/search?q=model+management+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Model Mayhem", "https://news.google.com/rss/search?q=model+mayhem+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Photodom", "https://news.google.com/rss/search?q=photodom+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("500px Photography", "https://news.google.com/rss/search?q=500px+photography+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("PetaPixel", "https://news.google.com/rss/search?q=petapixel+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Fstoppers", "https://news.google.com/rss/search?q=fstoppers+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Digital Photography Review", "https://news.google.com/rss/search?q=digital+photography+review+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Photography Life", "https://news.google.com/rss/search?q=photography+life+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("DPReview", "https://news.google.com/rss/search?q=dpreview+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Shutterbug Magazine", "https://news.google.com/rss/search?q=shutterbug+magazine+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("LensCulture", "https://news.google.com/rss/search?q=lensculture+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Artforum", "https://news.google.com/rss/search?q=artforum+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ArtNews", "https://news.google.com/rss/search?q=artnews+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Arte Magazine", "https://news.google.com/rss/search?q=arte+magazine+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Art Newspaper", "https://news.google.com/rss/search?q=the+art+newspaper+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Juxtapositions", "https://news.google.com/rss/search?q=juxtapositions+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Artsy", "https://news.google.com/rss/search?q=artsy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hyperallergic", "https://news.google.com/rss/search?q=hyperallergic+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== BLOCKLISTS ======================
ME_BLOCKLIST = {"trump", "harris", "biden", "congress", "senate", "house", "supreme court", "election", "midterm", "presidential", "republican", "democrat", "maga", "white house", "capitol", "washington dc", "oscars", "kennedy center", "tornadoes", "vernal equinox", "hyundai", "tsa", "airport security", "pope leo", "kentucky", "illinois primary", "michigan synagogue", "cuba", "china summit", "fcc", "sbf", "texas primaries", "nvidia", "foxconn", "walmart", "phonepe", "kushner", "sable offshore"}
US_BLOCKLIST = {"iran", "israel", "gaza", "hezbollah", "hamas", "hormuz", "khamenei", "netanyahu", "mbs", "mbz", "saudi", "uae", "qatar", "lebanon", "syria", "yemen", "palestine", "irgc", "houthis", "axis of resistance", "jcpoa", "snapback sanctions", "strait of hormuz"}
SPORTS_BLOCKLIST = ME_BLOCKLIST.union(US_BLOCKLIST)
TECH_BLOCKLIST = ME_BLOCKLIST.union(US_BLOCKLIST)
CULTURE_BLOCKLIST = ME_BLOCKLIST.union(US_BLOCKLIST).union(SPORTS_BLOCKLIST)

# ====================== SOURCES (your original lists — untouched) ======================
MIDDLE_EAST_SOURCES = [
    ("Broad Middle East", "https://news.google.com/rss/search?q=middle+east+OR+iran+OR+israel+OR+gulf+OR+hezbollah+OR+hamas+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera", "https://news.google.com/rss/search?q=aljazeera+news+OR+al+jazeera+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Times of Israel", "https://news.google.com/rss/search?q=times+of+israel+news+OR+timesofisrael+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=reuters+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP News", "https://news.google.com/rss/search?q=ap+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NYT", "https://news.google.com/rss/search?q=nytimes+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("WSJ", "https://news.google.com/rss/search?q=wsj+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Post", "https://news.google.com/rss/search?q=washington+post+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times", "https://news.google.com/rss/search?q=financial+times+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Economist", "https://news.google.com/rss/search?q=the+economist+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC", "https://news.google.com/rss/search?q=bbc+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian", "https://news.google.com/rss/search?q=the+guardian+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg", "https://news.google.com/rss/search?q=bloomberg+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Politico", "https://news.google.com/rss/search?q=politico+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs", "https://news.google.com/rss/search?q=foreign+affairs+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

US_POLITICS_SOURCES = [
    ("Broad US Politics", "https://news.google.com/rss/search?q=donald+trump+OR+us+election+OR+congress+OR+kamala+harris+OR+joe+biden+OR+republican+OR+democrat+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP News", "https://news.google.com/rss/search?q=when:1d+site:apnews.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters", "https://news.google.com/rss/search?q=when:1d+site:reuters.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("NYT", "https://news.google.com/rss/search?q=when:1d+site:nytimes.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("WSJ", "https://news.google.com/rss/search?q=when:1d+site:wsj.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Post", "https://news.google.com/rss/search?q=when:1d+site:washingtonpost.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Politico", "https://news.google.com/rss/search?q=when:1d+site:politico.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Axios", "https://news.google.com/rss/search?q=when:1d+site:axios.com+trump+OR+biden+OR+harris+OR+congress+OR+election&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg", "https://news.google.com/rss/search?q=bloomberg+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Atlantic", "https://news.google.com/rss/search?q=the+atlantic+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The New Yorker", "https://news.google.com/rss/search?q=the+new+yorker+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs", "https://news.google.com/rss/search?q=foreign+affairs+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Policy", "https://news.google.com/rss/search?q=foreign+policy+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("FiveThirtyEight", "https://news.google.com/rss/search?q=fivethirtyeight+news+politics+OR+trump+OR+biden+OR+congress+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

SPORTS_SOURCES = [
    ("Broad Sports", "https://news.google.com/rss/search?q=march+madness+OR+college+basketball+OR+ncaa+tournament+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ESPN", "https://news.google.com/rss/search?q=espn+news+sports+OR+nfl+OR+nba+OR+mlb+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC Sport", "https://news.google.com/rss/search?q=bbc+sport+news+OR+football+OR+cricket+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sky Sports", "https://news.google.com/rss/search?q=sky+sports+news+OR+premier+league+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters Sports", "https://news.google.com/rss/search?q=reuters+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP Sports", "https://news.google.com/rss/search?q=ap+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Athletic", "https://news.google.com/rss/search?q=the+athletic+news+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sports Illustrated", "https://news.google.com/rss/search?q=when:1d+site:si.com+sports+OR+nfl+OR+nba+OR+mlb&hl=en-US&gl=US&ceid=US:en"),
]

TECH_SOURCES = [
    ("Broad Tech and Life", "https://news.google.com/rss/search?q=technology+news+OR+ai+OR+tech+OR+gaming+OR+wearable+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Wired", "https://news.google.com/rss/search?q=wired+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MIT Technology Review", "https://news.google.com/rss/search?q=mit+technology+review+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Verge", "https://news.google.com/rss/search?q=the+verge+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TechCrunch", "https://news.google.com/rss/search?q=techcrunch+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Engadget", "https://news.google.com/rss/search?q=engadget+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CNET", "https://news.google.com/rss/search?q=cnet+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ZDNet", "https://news.google.com/rss/search?q=zdnet+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("IEEE Spectrum", "https://news.google.com/rss/search?q=ieee+spectrum+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Nature", "https://news.google.com/rss/search?q=nature+news+science+OR+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

# ====================== FETCH FUNCTION (100% untouched) ======================
def normalize_title(title):
    if " - " in title:
        title = title.rsplit(" - ", 1)[0]
    return title.strip().lower()

def fetch_section(sources, keywords, blocklist):
    matches = []
    seen_title = set()
    source_count = defaultdict(int)
    
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
                        ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                        ts = time.mktime(ts_struct) if ts_struct else time.time()
                        matches.append((ts, raw_title, source_name, link))
                        seen_title.add(norm_title)
                        source_count[source_name] += 1
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
tech_matches = fetch_section(TECH_SOURCES, TECH_KEYWORDS, ME_BLOCKLIST.union(US_BLOCKLIST))
culture_matches = fetch_section(CULTURE_SOURCES, CULTURE_KEYWORDS, CULTURE_BLOCKLIST)

# Time split (still 6h / 24h)
current_ts = time.time()
six_hours_ago = current_ts - 21600

# ====================== SPILLOVER TO GUARANTEE 30 ITEMS ======================
def fill_to_30(breaking, recent):
    filled = breaking[:30]
    if len(filled) < 30:
        needed = 30 - len(filled)
        filled.extend(recent[:needed])
    return filled[:30]

middle_breaking = fill_to_30([item for item in middle_matches if item[0] >= six_hours_ago], middle_matches)
us_breaking = fill_to_30([item for item in us_matches if item[0] >= six_hours_ago], us_matches)
sports_breaking = fill_to_30([item for item in sports_matches if item[0] >= six_hours_ago], sports_matches)
tech_breaking = fill_to_30([item for item in tech_matches if item[0] >= six_hours_ago], tech_matches)
culture_breaking = fill_to_30([item for item in culture_matches if item[0] >= six_hours_ago], culture_matches)

middle_recent = [item for item in middle_matches if item not in middle_breaking][:30]
us_recent = [item for item in us_matches if item not in us_breaking][:30]
sports_recent = [item for item in sports_matches if item not in sports_breaking][:30]
tech_recent = [item for item in tech_matches if item not in tech_breaking][:30]
culture_recent = [item for item in culture_matches if item not in culture_breaking][:30]

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
        .banner {
    background: #001B47;
    width: 100%;
    height: 165px;               /* taller banner so news columns sit cleanly below */
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
}

.youtube-inset {
    position: absolute;
    top: 12px;                   /* centered vertically in the taller banner */
    right: 16px;
    width: 138px;
    height: 138px;
    z-index: 3;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}

.youtube-inset iframe {
    width: 100%;
    height: 100%;
    border: none;
}

.header {
    margin-bottom: 15px;
    text-align: left;
    position: relative;
    z-index: 2;
    padding: 25px 20px 30px 20px;
    margin-top: -128px;          /* pulls title ON TOP of the banner */
}
        }
        h1 { color: #FFFFFF; margin: 0; text-decoration: underline; font-size: 2.2em; }
        .byline { color: #aaaaaa; font-size: 1.05em; margin: 5px 0 0 0; }
        .update { color: #aaaaaa; font-size: 0.85em; margin: 5px 0 0 0; }
        .section-title { color: #FF0000; font-size: 1.6em; margin: 30px 0 10px; font-weight: bold; text-decoration: underline; text-decoration-color: #FF0000; }
        .top-divider { border: 0; height: 3px; background: #FF0000; margin: 35px 0; }
        .headline { margin-bottom: 18px; padding-bottom: 10px; border-bottom: 1px solid #222222; }
        .title { color: #FFFFFF; }
        .link { color: #454545; text-decoration: underline; font-size: 0.85em; margin-left: 10px; }
        .link:hover { color: #FFFFFF; }
        .container { display: flex; flex-wrap: wrap; gap: 30px; max-width: 1400px; margin: 0 auto; }
        .column { flex: 1; min-width: 300px; }
        @media (max-width: 768px) { .container { flex-direction: column; } }
    </style>
</head>
<body>
                   <!-- NEW BANNER HEADER with inset live YouTube video -->
    <div class="banner">
        <div class="youtube-inset">
            <iframe 
                src="https://www.youtube.com/embed/B4-L2nfGcuE?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1"
                allow="autoplay; encrypted-media"
                allowfullscreen>
            </iframe>
        </div>
    </div>

    <!-- Header text now sits cleanly ON TOP of the banner -->
    <div class="header">
        <h1>The Mitchell Post</h1>
        <span class="byline">By Sean Mitchell</span>
        <span class="update">updated at """ + (datetime.utcnow() - timedelta(hours=7)).strftime("%I:%M:%S %p PDT") + """</span>
    </div>

    <!-- US -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Breaking US News</h2>
"""

if us_breaking:
    for ts, title, source, link in us_breaking:
        friendly = get_friendly_source(source)
        highlighted = title[0].upper() + title[1:] if title else title
        html += f'<div class="headline"><span class="title">{highlighted}</span> <span style="color:#666666;"> - {friendly}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
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
        highlighted = title[0].upper() + title[1:] if title else title
        html += f'<div class="headline"><span class="title">{highlighted}</span> <span style="color:#666666;"> - {friendly}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
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
        highlighted = title[0].upper() + title[1:] if title else title
        html += f'<div class="headline"><span class="title">{highlighted}</span> <span style="color:#666666;"> - {friendly}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
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
        highlighted = title[0].upper() + title[1:] if title else title
        html += f'<div class="headline"><span class="title">{highlighted}</span> <span style="color:#666666;"> - {friendly}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No additional headlines right now.</p>\n'

html += """
        </div>
    </div>

    <hr class="top-divider">

    <!-- TECH AND LIFE -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Tech and Life Breaking News</h2>
"""

if tech_breaking:
    for ts, title, source, link in tech_breaking:
        friendly = get_friendly_source(source)
        highlighted = title[0].upper() + title[1:] if title else title
        html += f'<div class="headline"><span class="title">{highlighted}</span> <span style="color:#666666;"> - {friendly}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking tech and life news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">Today's Tech and Life Headlines</h2>
"""

if tech_recent:
    for ts, title, source, link in tech_recent:
        friendly = get_friendly_source(source)
        highlighted = title[0].upper() + title[1:] if title else title
        html += f'<div class="headline"><span class="title">{highlighted}</span> <span style="color:#666666;"> - {friendly}</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No additional tech and life headlines right now.</p>\n'

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

    <hr class="top-divider">

    <!-- CULTURE -->
    <div class="container">
        <div class="column">
            <h2 class="section-title">Culture Breaking News</h2>
"""

if culture_breaking:
    for ts, title, source, link in culture_breaking:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No breaking culture news in the last 6 hours.</p>\n'

html += """
        </div>
        <div class="column">
            <h2 class="section-title">Today's Culture Headlines</h2>
"""

if culture_recent:
    for ts, title, source, link in culture_recent:
        friendly = get_friendly_source(source)
        html += f'<div class="headline"><span class="title">{title}</span> <span style="color:#aaaaaa;">[{friendly}]</span> <a class="link" href="{link}" target="_blank">[Full Article]</a></div>\n'
else:
    html += '<p>No additional culture headlines right now.</p>\n'

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
