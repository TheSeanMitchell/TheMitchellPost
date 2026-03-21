import feedparser
import time
import calendar
import os
import re
import hashlib
import urllib.request
from datetime import datetime, timedelta
from collections import defaultdict

print("Starting bot...")
CURRENT_DIR = os.getcwd()
print(f"Saving files to current directory: {CURRENT_DIR}")
INDEX_HTML = os.path.join(CURRENT_DIR, "index.html")

HEADERS_FILE = os.path.join(CURRENT_DIR, '_headers')
FEED_JSON  = os.path.join(CURRENT_DIR, "feed.json")

# ====================== FRIENDLY SOURCE NAMES ======================
SOURCE_MAP = {
    "Reuters": "Reuters", "Associated Press": "AP", "AP News": "AP",
    "Agence France-Presse": "AFP", "AFP": "AFP",
    "The New York Times": "NYT", "New York Times": "NYT",
    "The Wall Street Journal": "WSJ", "Wall Street Journal": "WSJ",
    "The Washington Post": "WaPo", "Washington Post": "WaPo",
    "The Atlantic": "Atlantic", "The New Yorker": "New Yorker",
    "The Hill": "The Hill", "The Dispatch": "Dispatch", "The Bulwark": "Bulwark",
    "The Texas Tribune": "TX Tribune", "The Philadelphia Inquirer": "Philly Inquirer",
    "The Boston Globe": "Boston Globe", "The Seattle Times": "Seattle Times",
    "The Denver Post": "Denver Post", "The Arizona Republic": "AZ Republic",
    "The Star Tribune Minneapolis": "Star Tribune", "The Oregonian": "Oregonian",
    "The Sacramento Bee": "Sac Bee", "The San Francisco Chronicle": "SF Chronicle",
    "The Dallas Morning News": "Dallas News",
    "The Atlanta Journal-Constitution": "AJC", "The Miami Herald": "Miami Herald",
    "The Cook Political Report": "Cook Political", "The Art Newspaper": "Art Newspaper",
    "The Business of Fashion": "BoF", "The Cut": "The Cut",
    "The Markup": "The Markup", "The Guardian US": "Guardian US",
    "The Guardian Arts": "Guardian Arts", "The Guardian Sport": "Guardian Sport",
    "The Guardian Technology": "Guardian Tech", "The Guardian": "Guardian",
    "The Economist": "Economist", "The Athletic": "Athletic",
    "The Cipher Brief": "Cipher Brief", "The Independent": "Independent",
    "The Telegraph": "Telegraph", "The Times": "The Times",
    "The Ringer": "The Ringer", "The Media Line": "Media Line",
    "The Daily Star Lebanon": "Daily Star LB", "The Intercept": "Intercept",
    "The National UAE": "National UAE", "The Big Lead": "Big Lead",
    "The GIST": "The GIST", "The Sporting News": "Sporting News",
    "The Players Tribune": "Players Tribune", "The Information": "The Information",
    "The Wrap": "The Wrap", "The Playlist": "Playlist",
    "Politico": "Politico", "Politico Magazine": "Politico Mag",
    "Axios": "Axios", "NPR": "NPR", "PBS NewsHour": "PBS", "PBS": "PBS",
    "BBC News": "BBC", "BBC Sport": "BBC Sport", "BBC Culture": "BBC Culture",
    "BBC Technology": "BBC Tech", "BBC": "BBC", "C-SPAN": "C-SPAN",
    "Al Jazeera": "Al Jazeera", "Al Arabiya": "Al Arabiya", "Al Bawaba": "Al Bawaba",
    "AL-Monitor": "Al-Monitor", "Al-Monitor": "Al-Monitor",
    "Times of Israel": "Times of Israel", "Haaretz": "Haaretz",
    "Jerusalem Post": "Jerusalem Post", "Israel Hayom": "Israel Hayom",
    "i24NEWS": "i24 NEWS", "Financial Times": "FT", "USA Today": "USA Today",
    "Sports Illustrated": "SI", "CBS Sports": "CBS Sports", "CBS News": "CBS News",
    "ABC News": "ABC News", "NBC News": "NBC News", "NBC Sports": "NBC Sports",
    "FOX Sports": "FOX Sports", "FOX News": "FOX News", "NCAA.com": "NCAA",
    "Bloomberg Government": "Bloomberg Gov", "Bloomberg Sports": "Bloomberg Sports",
    "Bloomberg Technology": "Bloomberg Tech", "Bloomberg": "Bloomberg",
    "Foreign Affairs": "Foreign Affairs", "Foreign Policy": "Foreign Policy",
    "FiveThirtyEight": "538", "Christian Science Monitor": "CS Monitor",
    "CNBC": "CNBC", "Forbes": "Forbes",
    "Los Angeles Times Entertainment": "LAT Ent", "Los Angeles Times": "LAT",
    "Chicago Tribune": "Chi Tribune", "ProPublica": "ProPublica",
    "Pew Research Center": "Pew Research", "Brookings Institution": "Brookings",
    "RAND Corporation": "RAND", "Council on Foreign Relations": "CFR",
    "Atlantic Council": "Atlantic Council", "Roll Call": "Roll Call",
    "National Journal": "Natl Journal", "Ballotpedia": "Ballotpedia",
    "RealClearPolitics": "RCP", "FactCheck.org": "FactCheck",
    "PolitiFact": "PolitiFact", "Snopes": "Snopes", "Notus": "Notus",
    "Punchbowl News": "Punchbowl", "Semafor": "Semafor",
    "McClatchy DC Bureau": "McClatchy", "Stat News": "STAT News",
    "Defense News": "Defense News", "Just Security": "Just Security",
    "Lawfare Blog": "Lawfare", "SCOTUSblog": "SCOTUSblog",
    "OpenSecrets.org": "OpenSecrets", "Governing Magazine": "Governing",
    "Government Executive": "Gov Executive", "Federal News Network": "Fed News Net",
    "Defense One": "Defense One", "War on the Rocks": "War on Rocks",
    "National Defense Magazine": "Natl Defense", "NewsNation": "NewsNation",
    "Straight Arrow News": "Straight Arrow", "Iran International": "Iran Intl",
    "Middle East Eye": "ME Eye", "Middle East Monitor": "ME Monitor",
    "Middle East Institute": "MEI", "TRT World": "TRT World",
    "Press TV": "Press TV", "Tehran Times": "Tehran Times",
    "Ahram Online": "Ahram Online", "Hurriyet Daily News": "Hurriyet",
    "Arab News": "Arab News", "Asharq Al-Awsat": "Asharq",
    "Jadaliyya": "Jadaliyya", "L'Orient Today": "L'Orient",
    "Mondoweiss": "Mondoweiss", "Electronic Intifada": "E. Intifada",
    "Gulf News": "Gulf News", "Ynet News": "Ynet", "Crisis Group": "Crisis Group",
    "ESPN": "ESPN", "Sky Sports": "Sky Sports", "Yahoo Sports": "Yahoo Sports",
    "Bleacher Report": "B/R", "Front Office Sports": "Front Office",
    "Sportico": "Sportico", "Sports Business Journal": "SBJ",
    "Defector": "Defector", "Yardbarker": "Yardbarker", "SB Nation": "SB Nation",
    "Sportskeeda": "Sportskeeda", "Goal.com": "Goal", "Marca": "Marca",
    "L'Equipe": "L'Equipe", "Cricbuzz": "Cricbuzz", "ESPNcricinfo": "Cricinfo",
    "theScore": "theScore", "MMA Fighting": "MMA Fighting",
    "BoxingScene": "BoxingScene", "Golf Digest": "Golf Digest",
    "Motorsport.com": "Motorsport", "Autosport": "Autosport",
    "Wired": "Wired", "MIT Technology Review": "MIT Tech Review",
    "The Verge": "Verge", "TechCrunch": "TechCrunch", "Engadget": "Engadget",
    "CNET": "CNET", "ZDNet": "ZDNet", "IEEE Spectrum": "IEEE Spectrum",
    "Nature": "Nature", "Ars Technica": "Ars Technica", "Mashable": "Mashable",
    "Gizmodo": "Gizmodo", "TechRadar": "TechRadar", "VentureBeat": "VentureBeat",
    "Popular Science": "Pop Sci", "Scientific American": "Sci American",
    "TMZ": "TMZ", "E! News": "E! News", "People Magazine": "People",
    "Vanity Fair": "Vanity Fair", "Vogue": "Vogue",
    "Harper's Bazaar": "Harper's Bazaar", "Elle": "Elle",
    "Cosmopolitan": "Cosmopolitan", "Glamour": "Glamour", "GQ": "GQ",
    "Esquire": "Esquire", "W Magazine": "W Magazine", "Refinery29": "Refinery29",
    "Just Jared": "Just Jared", "Hollywood Reporter": "THR",
    "Hollywood Life": "Hollywood Life", "Variety": "Variety",
    "Deadline": "Deadline", "Entertainment Weekly": "EW",
    "Billboard": "Billboard", "Rolling Stone": "Rolling Stone",
    "Pitchfork": "Pitchfork", "Complex": "Complex", "IndieWire": "IndieWire",
    "PopSugar": "PopSugar", "US Weekly": "US Weekly", "Teen Vogue": "Teen Vogue",
    "Nylon Magazine": "Nylon", "Hyperallergic": "Hyperallergic",
    "PetaPixel": "PetaPixel", "Women's Wear Daily": "WWD",
    "Fashionista": "Fashionista", "Dazed": "Dazed", "Artforum": "Artforum",
    "Frieze": "Frieze", "New York Times Arts": "NYT Arts", "Vulture": "Vulture",
    "A.V. Club": "AV Club", "NME": "NME", "Consequence of Sound": "CoS",
    "Stereogum": "Stereogum", "Screen Rant": "Screen Rant", "Collider": "Collider",
    "Literary Hub": "Lit Hub", "Publishers Weekly": "PW", "Book Riot": "Book Riot",
    # Asia / Europe / World
    "Nikkei Asia": "Nikkei Asia", "Nikkei Asia Review": "Nikkei Asia",
    "Japan Times": "Japan Times", "The Japan News": "Japan News",
    "Asahi Shimbun": "Asahi Shimbun", "Mainichi Shimbun": "Mainichi",
    "Yomiuri Shimbun": "Yomiuri", "Sankei Shimbun": "Sankei",
    "NHK World": "NHK World", "Kyodo News": "Kyodo News",
    "Bangkok Post": "Bangkok Post", "The Nation Thailand": "Nation TH",
    "Thai PBS": "Thai PBS", "Straits Times": "Straits Times",
    "South China Morning Post": "SCMP", "Korea Herald": "Korea Herald",
    "The Korea Times": "Korea Times", "Hindustan Times": "Hindustan Times",
    "The Hindu": "The Hindu", "Euronews": "Euronews",
    "France 24": "France 24", "Deutsche Welle": "DW",
    "Politico Europe": "Politico EU", "The Local": "The Local",
    "Irish Times": "Irish Times", "Irish Independent": "Irish Indep",
    "La Repubblica": "La Repubblica", "Corriere della Sera": "Corriere",
    "Il Sole 24 Ore": "Il Sole", "Frankfurter Allgemeine": "FAZ",
    "Suddeutsche Zeitung": "SZ", "Die Welt": "Die Welt",
    "Le Figaro": "Le Figaro", "Liberation": "Liberation",
    "La Vanguardia": "La Vanguardia", "El Mundo": "El Mundo",
    "Neue Zurcher Zeitung": "NZZ", "Neue Zuercher Zeitung": "NZZ",
    "VnExpress": "VnExpress", "Philippine Daily Inquirer": "Phil Inquirer",
    "The Jakarta Post": "Jakarta Post", "The Star Malaysia": "Star Malaysia",
    "The Australian": "The Australian", "Sydney Morning Herald": "SMH",
    "Bloomberg Asia": "Bloomberg Asia", "The Diplomat": "The Diplomat",
    "Asia Times": "Asia Times", "East Asia Forum": "East Asia Forum",
    "Eurasia Review": "Eurasia Review", "Japan Forward": "Japan Forward",
    "The Cambodia Daily": "Cambodia Daily", "Myanmar Times": "Myanmar Times",
}

def get_friendly_source(raw_name):
    for key in SOURCE_MAP:
        if key.lower() in raw_name.lower():
            return SOURCE_MAP[key]
    return raw_name.split(" - ")[-1].strip() if " - " in raw_name else raw_name

# ====================== WHOLE-WORD KEYWORD MATCHING ======================
# Using word boundaries so "CIA" won't match inside "facial" or "social"

def make_keyword_pattern(keywords):
    sorted_kws = sorted(keywords, key=len, reverse=True)
    escaped = [re.escape(kw) for kw in sorted_kws]
    return re.compile(
        r'(?<![a-zA-Z0-9])(' + '|'.join(escaped) + r')(?![a-zA-Z0-9])',
        re.IGNORECASE
    )

def title_matches_keywords(title_lower, pattern):
    return bool(pattern.search(title_lower))

# ====================== KEYWORDS ======================

RAW_ME_KEYWORDS = [
    "middle east","arab world","gulf states","gulf cooperation council","gcc countries",
    "levant region","maghreb region","mena region","persian gulf","arabian peninsula",
    "west asia","red sea region","iran","iranian","tehran","qom","mashhad","isfahan",
    "tabriz","khuzestan","israel","israeli","jerusalem","tel aviv","west bank",
    "gaza strip","golan heights","saudi arabia","saudi","riyadh","jeddah","neom",
    "vision 2030","united arab emirates","uae","emirates","abu dhabi","dubai","sharjah",
    "qatar","doha","kuwait","kuwait city","oman","muscat","bahrain","manama",
    "iraq","iraqi","baghdad","basra","mosul","kurdistan iraq","erbil","syria",
    "syrian","damascus","aleppo","idlib","lebanon","lebanese","beirut","jordan",
    "amman","turkey","turkish","ankara","istanbul","egypt","egyptian","cairo",
    "alexandria","yemen","yemeni","sanaa","aden","palestine","palestinian","ramallah",
    "khamenei","ayatollah","supreme leader iran","pezeshkian","benjamin netanyahu",
    "netanyahu government","israeli war cabinet","mohammed bin salman","mbs saudi",
    "saudi crown prince","mohammed bin zayed","mbz","recep tayyip erdogan",
    "abdel fattah el sisi","tamim bin hamad al thani","king abdullah jordan",
    "bashar al assad","middle east war","military escalation middle east",
    "proxy war middle east","militia middle east","airstrike middle east",
    "drone strike middle east","missile attack middle east","ballistic missile middle east",
    "red sea shipping attack","military buildup middle east","hezbollah","hamas",
    "palestinian islamic jihad","irgc","islamic revolutionary guard corps","houthis",
    "ansar allah","popular mobilization forces","aqap","isis","isis-k","islamic state",
    "gaza war","israel gaza war","gaza ceasefire","israel hezbollah conflict",
    "yemen civil war","red sea crisis","syria civil war","iran nuclear program",
    "uranium enrichment","iran centrifuges","natanz nuclear facility",
    "fordow nuclear facility","iaea iran","jcpoa","iran nuclear deal","snapback sanctions",
    "brent crude","wti crude","oil supply disruption","opec","opec+",
    "oil tanker attack","hormuz blockade","strait of hormuz","red sea shipping",
    "suez canal shipping","iran oil exports","us middle east policy","us centcom",
    "centcom strikes","american troops iraq","us troops syria","russia middle east policy",
    "china iran deal","abraham accords","israel normalization","saudi israel normalization",
    "arab league","iran saudi relations","hezbollah rocket barrage","axis of resistance",
    "iran proxy war","iran leadership crisis","iran power struggle","iran succession crisis",
    "iran regime stability","iran missile stockpile","iran retaliation israel",
    "israel strike iran","israel iran escalation","persian gulf naval standoff",
    "houthi missile attacks shipping","bab el mandeb strait crisis",
    "global shipping disruption red sea","saudi nuclear program","uae nuclear program",
    "bunker buster strike iran","iran nuclear facilities","natanz","fordow",
    "iran escalation","october 7 attack","hamas october 7","gaza ground offensive",
    "rafah offensive","rafah crossing","gaza hostage crisis","israeli hostages",
    "hostage negotiations gaza","ceasefire negotiations gaza","gaza aid convoy",
    "gaza famine warning","west bank raids","settler violence west bank",
    "iran proxy network","iran hardliners vs reformists","iran internet blackout",
    "iran economic collapse","iran shadow fleet","iran drone exports","iran russia drone deal",
    "israel iran direct conflict","middle east geopolitical risk",
    "eastern mediterranean gas fields","levant gas dispute","middle east arms race",
    "drone proliferation middle east","aircraft carrier persian gulf","osint iran military",
    "oil price spike middle east conflict","emergency diplomacy middle east",
    "international mediation middle east conflict","iron dome","arrow missile defense",
    "shahed drone","cyber warfare israel iran","iran war","iran strikes",
    "iran nuclear strikes","operation midnight hammer","iran regime change",
    "irgc strikes","hormuz strait","us israel iran","maximum pressure iran",
    "qatar's energy","missile sites","missile threat","war rages","drone","drones",
    "dubai property","oil","energy price","oil fields","military operations",
    "crude","crude oil","crude exports","tanker","scarcity","rifle",
    "jews","jewish","israelis","rare earth","vaccine","ground troops",
    "muslim","lebenon","energy shock","gas-dependent","satellite images","flooding",
    "nuclear","nuclear energy","kurds","northern iraq","nowruz","top leaders",
    "energy fallout","humanitarian","humanitarian aid","nuclear submarine",

    "Iran tensions","OPEC meeting","barrel of oil","refinery fire","shale oil","naval blockade",
    "Tomahawk missile","Red Sea","Houthi rebels","fracking boom","strategic petroleum reserve","SPR release",
    "centrifuge","THAAD system","Patriot missile","Soleimani strike","Qasem Soleimani","Baghdad airport",
    "proxy militia","Iranian Revolutionary Guard","Gaza conflict","two-state solution","rocket barrage","IDF",
    "Israeli Defense Forces","Palestinian Authority","Hamas tunnels","war crimes probe","ICC warrant","genocide accusation",
    "UN resolution","Security Council veto","Nord Stream","pipeline sabotage","European gas crisis","LNG exports",
    "energy weaponization","Suez Canal blockage","Houthi drone attack","OPEC oil embargo","Iran hostage crisis","East Palestine train derailment",
    "anti Israel protest","Gaza solidarity","Palestine flag","Hormuz closure","Bab el Mandeb","Iran malign actor",
    "uranium stockpile","two state framework","grain deal","Black Sea grain corridor","wheat export","fertilizer shortage",
    "global hunger","famine risk","Horn of Africa","drought famine","aid convoy","humanitarian corridor",
    "access denial","siege tactic","starvation weapon","war crime charge","ICC investigation","genocide convention",
]
ME_KEYWORDS = set(kw.lower() for kw in RAW_ME_KEYWORDS)

RAW_US_KEYWORDS = [
    "us politics","american politics","federal government","state government",
    "local government","congress news","senate news","house of representatives",
    "supreme court rulings","scotus decisions","federal court cases",
    "district court rulings","appellate court rulings","executive orders",
    "white house briefing","presidential address","press secretary briefing",
    "election news","election updates","election coverage","presidential election",
    "midterm elections","senate races","house races","governor races","mayoral races",
    "ballot initiatives","referendums","voter turnout","voter suppression",
    "election integrity","mail in voting","absentee ballots","early voting",
    "voter id laws","electoral college","swing states","battleground states",
    "red states","blue states","purple states","political polling","approval ratings",
    "favorability ratings","policy proposals","legislative agenda","bipartisan bill",
    "partisan divide","filibuster","budget reconciliation","government shutdown",
    "federal budget","national debt","deficit spending","tax reform","irs policy",
    "corporate tax","income tax","capital gains tax","inflation rate","cpi inflation",
    "ppi inflation","interest rates","federal reserve policy","fed rate hike",
    "fed rate cuts","unemployment rate","job growth","labor market","wage growth",
    "housing market","mortgage rates","rent prices","real estate trends",
    "housing affordability","homelessness policy","healthcare policy","medicare",
    "medicaid","affordable care act","obamacare","drug pricing","prescription costs",
    "public health policy","pandemic response","vaccine policy","immigration policy",
    "border security","asylum policy","deportation policy","daca","visa policy",
    "refugee policy","foreign policy","us china relations","us russia relations",
    "us iran policy","nato policy","defense spending","military budget","pentagon news",
    "national security","intelligence community","fbi","nsa","homeland security",
    "cybersecurity policy","cyber attacks","infrastructure security","critical infrastructure",
    "energy policy","oil production","gas prices","renewable energy","solar power",
    "wind energy","nuclear energy policy","climate change policy","carbon emissions",
    "environmental protection","epa regulations","water policy","agriculture policy",
    "farm bill","food supply chain","trade policy","tariffs","global trade",
    "supply chain disruptions","manufacturing policy","industrial policy","antitrust law",
    "big tech regulation","ai regulation","data privacy law","section 230",
    "social media policy","digital rights","free speech law","first amendment cases",
    "second amendment cases","gun control policy","gun rights","crime rates",
    "policing policy","criminal justice reform","prison reform","sentencing laws",
    "drug policy","opioid crisis","fentanyl crisis","education policy","student loans",
    "tuition costs","k-12 education","curriculum debates","school funding","charter schools",
    "culture war issues","gender policy","civil rights","voting rights act",
    "discrimination law","supreme court nominations","judicial appointments",
    "political scandals","ethics investigations","lobbying","lobbying disclosure",
    "campaign finance","super pacs","dark money","election interference","misinformation",
    "disinformation","media bias","journalism ethics","breaking news us","policy analysis",
    "political analysis","expert commentary","think tank reports","government data releases",
    "economic indicators","consumer confidence","retail sales","manufacturing index",
    "housing starts","building permits","transportation policy","infrastructure bill",
    "highways funding","public transit","aviation policy","airline industry","faa regulation",
    "ev policy","electric vehicles","automotive regulation","tech innovation policy",
    "space policy","nasa missions","spacex policy","telecommunications policy","5g rollout",
    "broadband access","rural internet","urban development","zoning laws","land use policy",
    "disaster response","emergency management","fema response","wildfire policy",
    "hurricane response","climate disasters","insurance markets","banking regulation",
    "financial markets","stock market news","dow jones","nasdaq","earnings reports",
    "corporate governance","mergers and acquisitions","startup funding","venture capital",
    "labor unions","strikes","labor disputes","minimum wage","gig economy",
    "workplace regulation","osha policy","diversity equity inclusion policy",
    "government oversight","inspector general reports","whistleblower cases","transparency",
    "freedom of information act","foia requests","investigative journalism",
    "watchdog reporting","accountability journalism","fact checking","verification",
    "press releases","data journalism","open data","public records","expert analysis",
    "peer reviewed studies","policy outcomes","trend analysis","risk assessment",
    "geopolitical risk","economic outlook","future forecasts","us economy","economic growth",
    "recession risk","fiscal policy","monetary policy","consumer spending",
    "productivity growth","manufacturing output","services sector","small business trends",
    "corporate layoffs","hiring trends","job openings","labor participation rate",
    "unionization trends","antitrust cases","monopoly regulation","tech monopolies",
    "platform regulation","social media companies","content moderation","digital censorship",
    "online speech","misinformation campaigns","election security","voting machines",
    "cybersecurity threats","hacking incidents","ransomware attacks","data breaches",
    "identity theft","privacy concerns","surveillance policy","facial recognition law",
    "biometric data","border surveillance","immigration raids","sanctuary cities",
    "deportation flights","refugee intake","asylum backlog","immigration courts",
    "border wall policy","foreign aid","military alliances","defense contracts",
    "arms sales","weapons systems","drone warfare","cyber warfare","space force",
    "nuclear policy","arms control treaties","sanctions policy","trade agreements",
    "export controls","tariffs china","tariffs europe","trade war","global markets",
    "currency exchange","dollar strength","inflation expectations","bond market",
    "treasury yields","housing affordability crisis","urban housing crisis",
    "infrastructure investment","public works projects","transportation funding",
    "rail systems","high speed rail","airline safety","aviation incidents",
    "supply chain logistics","port congestion","trucking industry","fuel prices",
    "energy independence","oil reserves","strategic petroleum reserve",
    "clean energy transition","green energy policy","climate legislation",
    "emissions targets","carbon pricing","environmental justice","water shortages",
    "drought conditions","wildfire seasons","hurricane tracking","disaster recovery funding",
    "insurance premiums","banking stability","financial regulation","fintech innovation",
    "cryptocurrency regulation","digital assets","blockchain policy",
    "central bank digital currency","cbdc policy","ai innovation","ai startups",
    "ai governance","automation jobs","future of work","remote work policy",
    "hybrid work trends","workplace productivity","labor shortages","skills gap",
    "education reform","public school funding","higher education policy",
    "student debt relief","loan forgiveness","campus protests","academic freedom",
    "free speech campuses","civil liberties","human rights us","police reform",
    "qualified immunity","incarceration rates","prison conditions","parole policy",
    "rehabilitation programs","drug legalization","marijuana policy",
    "border fentanyl trafficking","healthcare costs","insurance coverage",
    "hospital systems","medical workforce","telehealth expansion","pharmaceutical industry",
    "drug approvals","fda policy","pandemic preparedness","vaccine rollout",
    "disease outbreaks","public health emergencies","science funding","research grants",
    "innovation policy","space exploration","satellite systems","gps systems",
    "telecommunications law","internet access","digital divide","rural broadband expansion",
    "urban infrastructure","smart cities","technology adoption","consumer tech policy",
    "product safety","recalls","supply shortages","retail trends","consumer confidence index",
    "economic forecasts","policy debates","public hearings","committee investigations",
    "special counsel investigations","ethics violations","campaign violations",
    "political donations","fundraising totals","election ads","media coverage",
    "press conferences","interviews politicians","debate performances","primary elections",
    "caucuses","delegate counts","convention news","party platforms",
    "republican party news","democratic party news","independent candidates",
    "third party politics","libertarian party","green party","political ideology",
    "conservatism","liberalism","populism","nationalism","globalization","isolationism",
    "political polarization","bipartisan cooperation","legislative gridlock",
    "judicial review","constitutional amendments","civil cases","criminal cases",
    "legal precedent","supreme court majority","dissenting opinions","oral arguments",
    "legal briefs","case filings","appeals process","justice department investigations",
    "attorney general actions","federal prosecutions","white collar crime",
    "corporate fraud","insider trading","financial crime","public corruption",
    "ethics reforms","transparency initiatives","whistleblower protections",
    "government accountability","civic participation","voter registration",
    "turnout efforts","campaign volunteering","grassroots activism","political organizing",
    "community engagement","public forums","town meetings","citizen initiatives",
    "public referenda","open government","watchdog groups","nonprofit reporting",
    "independent journalism","media ecosystem","news consumption trends",
    "information credibility","source verification","fact based reporting",
    "evidence based policy","expert interviews","data driven journalism",
    "public records access","foia disclosures","leak investigations",
    "insider information politics","anonymous sources politics","beltway politics",
    "washington insiders","capitol hill updates","white house insiders",
    "whistleblower leaks","classified document cases","document mishandling investigations",
    "legal exposure politicians","indictment news politicians","criminal charges politicians",
    "court appearances politicians","plea deals politics","sentencing politicians",
    "constitutional challenges","supreme court appeals","precedent setting cases",
    "landmark rulings","legal interpretation debates","judicial philosophy",
    "executive privilege claims","congressional oversight authority","subpoena enforcement",
    "contempt of congress","impeachment proceedings","articles of impeachment",
    "senate trial impeachment","political fallout impeachment",
    "america first","trump doctrine","trump 2.0","peace through strength",
    "maximum pressure","trump foreign policy","trump national security","trump defense strategy",
    "deter china","china deterrence","indo pacific","taiwan defense","taiwan invasion",
    "us china trade war","china tech controls","export controls china","first island chain",
    "ukraine ceasefire","ukraine peace deal","nato burden sharing","nato allies spending",
    "russia ukraine war","putin trump talks","ukraine concessions","nato reform",
    "western hemisphere","monroe doctrine","narco terrorism","cartel national security",
    "panama canal","greenland threat","border national security","homeland defense",
    "national defense strategy","defense industrial base","defense budget increase",
    "nuclear modernization","cyber defense","ai national security","quantum defense",
    "supply chain security","critical minerals","energy dominance","economic statecraft",
    "geopolitical competition","great power competition","multipolar world",
    "rules-based order","strategic stability","deterrence by denial",
    "trump tariffs foreign policy","us grand strategy","trump tariffs",
    "elon musk","jd vance","maga movement","deep state","fake news","cancel culture",
    "woke agenda","dei backlash","transgender rights debate","abortion ban","gun rights",
    "second amendment","border crisis","illegal immigration","election fraud claims",
    "supreme court ruling","roe v wade overturn","big tech censorship","section 230 reform",
    "twitter files","fox news bias","inflation spike","recession warning",
    "stock market crash","bitcoin crypto","ev mandate","climate change hoax","green new deal",
    "ozempic weight loss","big pharma corruption","vaccine injury claims","covid lab leak",
    "ukraine aid package","israel gaza war","china trade war","tariffs on china",
    "ai deepfake","chatgpt regulation","tesla stock","elon musk trump","vance vp",
    "maga rally","trump assassination attempt","secret service failure","fbi investigation",
    "doj corruption","impeachment talk","government shutdown threat","national debt ceiling",
    "tax cuts for rich","student loan forgiveness","campus protest","free speech on campus",
    "civil rights movement","black lives matter","defund the police","criminal justice",
    "death penalty","border fentanyl","cartel violence","asylum seeker","deportation flight",
    "sanctuary city","immigration court backlog","daca dreamers","visa overstays",
    "chain migration","h1b visa abuse","ai job loss","automation unemployment",
    "hawaii","marines","amphibious","assault ship","nato allies",
    "strait of hormuz","missile sites","missile threat","war rages","drone","drones",
    "wall street","inflation","energy price","stocks","american","americans",
    "americans expect","americans worry","oil fields","military operations","crude",
    "crude oil","crude exports","us households","cuba","tanker","scarcity","rifle",
    "harvard","jeffrey epstein","epstein","ghislaine maxwell","epstein files",
    "clinton","bill clinton","hillary clinton","kamala harris","gavin newsom",
    "steven hilton","us election","election campaign","campaign season","sam altman",
    "openai","rare earth","amazon","vaccine","kc-135","ground troops","new jersey",
    "mexico","costa rica","costa rican","judge","deportation","deport","deported",
    "immigration law","pump","wallet","financial crisis","financial","energy shock",
    "gas-dependent","world cup","satellite images","us deploys","us deployment",
    "pete hegseth","new york times","homeland security","executive order","flooding",
    "summer heat","southwest","climate change","governor","swalwell","california",
    "dea","prosecutors","probe","drug traffickers","overweight","obese","obesity",
    "fbi agents","cia agents","nuclear","nuclear energy","top leaders","campaigns",
    "campaign for governor","mail ballots","mail-in ballots","election day","pentagon",
    "energy fallout","humanitarian","humanitarian aid","protestor","protestors",
    "corpus christi","michigan","immigration operation","florida","boston",
    "fuel tax","police","police officer","police officers","nuclear submarine",
    "reporters","mar-a-lago","palm beach",
    "minimum wage hike","union strike","labor shortage","school choice","curriculum battle",
    "critical race theory","gender ideology","trans athlete","women sports","title ix",
    "biological sex","pronoun debate","big tech monopoly","google antitrust","amazon breakup",
    "facebook censorship","twitter rebrand x","elon musk free speech","section 230 repeal",
    "ai regulation bill","chatgpt bias","deepfake election","misinformation law",
    "mainstream media decline","alternative media rise","podcast boom","youtube politics",
    "tiktok ban bill","china spy","balloon incident","taiwan invasion risk","ukraine funding",
    "israel aid","gaza ceasefire","hamas hostage","iran nuclear","saudi normalization",
    "abraham accords","climate emergency","green energy subsidy","ev tax credit",
    "gas price spike","inflation reduction act","build back better","chip act",
    "semiconductor shortage","tesla robotaxi","space x launch","nasa artemis","moon mission",
    "satellite internet","starlink ukraine","cyber attack","ransomware","data breach",
    "privacy law","surveillance state","fbi whistleblower","qanon","conspiracy theory",
    "election denial","jan 6 committee","capitol riot","impeachment","hunter biden",
    "laptop from hell","burisma","big pharma","pfizer","moderna","vaccine mandate",
    "mask mandate","lockdown","covid origin","lab leak theory","gain of function",
    "who pandemic treaty","global health","obesity epidemic","ozempic shortage",
    "weight loss drug","mental health crisis","opioid epidemic","fentanyl death","cartel",
    "mexico border","wall construction","deportation","ice raid","sanctuary","dream act",
    "amnesty","jan 6",
    "2026 midterms","midterm elections 2026","house elections 2026","senate elections 2026",
    "primary elections 2026","texas primaries 2026","north carolina primaries 2026",
    "arkansas primaries 2026","nato trump rebuke","trump tariffs supreme court","dei 2026",
    "state of the union 2026","make america healthy again","maha policy",
    "artificial intelligence regulation 2026","budget tightening 2026","federalism 2026",
    "medicaid reform 2026","2026 election cycle","trump third term talk",
    "harris comeback 2026","gavin newsom national profile","josh hawley senate leadership",
    "marco rubio secretary of state","mike johnson speaker challenges",
    "hakeem jeffries minority leader","chuck schumer filibuster reform",
    "democrat house takeover path 2026","republican senate hold strategy",
    "generic congressional ballot 2026","trump approval rating",
    "economy midterm driver 2026","inflation cooling narrative","grocery price fatigue",
    "housing crash fears","commercial real estate distress","office vacancy rates",
    "return to office mandates","ai job displacement panic",
    "universal basic income debate 2026","wealth tax proposals","silicon valley trump shift",
    "one big beautiful bill","trump administration shifts 2026",
    "make america healthy again initiatives","state priorities 2026",
    "federalism conflicts 2026","supreme court tariff rulings 2026",
    "federal budget deals 2026","supreme court uphold tariffs",
    "election day november 2026","primary timelines 2026","special senate elections",
    "key races watch 2026","anti trump firebrand","pragmatist candidates","moderate appeal",
    "net gain senate","trump aligned candidates","far left challengers","far right challengers",
    "presidential approval drivers","blue wave 2026","republican outsiders",
    "executive overreach","cost of living midterms","entitlement cuts","democrat enthusiasm",
    "special election democrat","democrat outperform","house seat special",
    "state budget tightening 2026","revenues decline 2026","spending needs rise 2026",
    "transportation funding 2026","emergency management 2026","public health policy 2026",
    "medicaid changes 2026","trump accounts savings","trumprx policy","credit card interest cap",

    "war","oil","immigration","campaign","US Navy","aircraft carrier",
    "Persian Gulf","Iran tensions","ballistic missile","hypersonic missile","joint exercises","troop deployment",
    "allied forces","Pacific Fleet","oil prices","barrel of oil","stock market","recession fears",
    "gasoline shortage","diesel fuel","shale oil","global supply chain","Donald Trump","polling data",
    "debate night","primary election","Democratic Party","Republican Party","White House","Capitol Hill",
    "Senate race","Epstein list","court documents","unsealed files","Ghislaine trial","flight logs",
    "elite connections","conspiracy theories","southern border","illegal crossing","migrant caravan","asylum seekers",
    "ICE agents","border patrol","mass deportation","immigration reform","cartel smuggling","weight gain",
    "diet epidemic","childhood obesity","BMI index","fitness crisis","public health alert","CDC report",
    "drug bust","cartel operation","SWAT raid","arrest warrant","law enforcement","corruption probe",
    "extreme weather","hurricane warning","wildfire season","heat advisory","global warming","sea level rise",
    "storm surge","Texas coast","tech billionaire","supply chain crisis","China minerals","COVID booster",
    "FIFA World Cup","soccer tournament","spy satellite","reconnaissance images","American families","public opinion",
    "relief effort","protest march","demonstration rally","riot control","carrier strike group","defense budget",
    "air force base","Middle East conflict","energy crisis","commodity trading","vice presidential","cabinet nominee",
    "ballot box","voter fraud claims","Epstein island","document dump","border wall","public health",
    "fentanyl seizure","police raid","wildfire alert","rare earth minerals","world cup final","satellite surveillance",
    "humanitarian crisis","protest violence","shipping lanes","oil tanker attack","economic sanctions","missile defense",
    "allied summit","naval exercise","amphibious landing","Marine expeditionary unit","MEU","special operations",
    "SEAL team","Delta Force","Federal Reserve","real estate bubble","foreclosure wave","debt ceiling",
    "budget deficit","Social Security","entitlement reform","Supreme Court","Roe v Wade","abortion rights",
    "gun control","assault rifle ban","background checks","mass shooting","school shooting","active shooter",
    "lockdown drill","prescription drugs","gain-of-function research","lockdown protest","freedom convoy","January 6",
    "voter ID","ballot harvesting","drop boxes","Dominion voting","election fraud","audit results",
    "recount battle","swing state recount","Georgia runoff","Arizona audit","Pennsylvania primary","Michigan primary",
    "super PAC","political ad","attack ad","debate stage","town hall","rally crowd",
    "endorsement list","VP pick","running mate","transition team","inauguration day","cabinet confirmation",
    "Senate hearing","filibuster rule","Supreme Court nominee","judicial activism","originalism","constitutional crisis",
    "executive privilege","subpoena fight","impeachment inquiry","special counsel","Mueller report","Durham investigation",
    "classified documents","Mar-a-Lago raid","Jack Smith","laptop scandal","influence peddling","foreign lobbying",
    "FARA violation","espionage act","whistleblower","intelligence leak","Snowden","Assange",
    "WikiLeaks","shadow government","military industrial complex","defense contractor","Lockheed Martin","Raytheon",
    "Boeing stock","war profiteering","endless war","Afghanistan withdrawal","Kabul evacuation","Taliban takeover",
    "ISIS-K","drone strike","civilian casualty","rules of engagement","ROE","counterterrorism",
    "special forces raid","bin Laden raid","ceasefire talks","hostage release","border fence","war crimes probe",
    "ICC warrant","energy embargo","US LNG terminal","Arctic oil","North Sea drilling","Keystone XL cancellation",
    "pipeline protest","environmental activism","Extinction Rebellion","Just Stop Oil","climate protest","IRA subsidies",
    "fossil fuel phaseout","coal plant closure","free speech","national security risk","FISA warrant","warrantless wiretap",
    "child exploitation","DNI report","annual threat assessment","urban warfare","tunnel network","asymmetric warfare",
    "guerrilla tactics","insurgency","counterinsurgency","nation building","regime change","foreign meddling",
    "disinformation campaign","hybrid warfare","psyops","propaganda","mainstream narrative","fact check",
    "culture war","DEI initiative","diversity equity inclusion","athletic scholarship","medical malpractice","big pharma profit",
    "opioid settlement","Purdue Pharma","Sackler family","Purdue bankruptcy","addiction crisis","overdose death",
    "Narcan distribution","fentanyl test strip","harm reduction","safe injection site","drug decriminalization","Oregon Measure 110",
    "Portland crime wave","shoplifting epidemic","smash and grab","retail theft","organized retail crime","police defund",
    "chokehold ban","body cam footage","use of force policy","deadly force","no knock warrant","Breonna Taylor",
    "George Floyd","BLM protest","racial justice","back the blue","law and order","tough on crime",
    "bail reform","catch and release","recidivism rate","mass incarceration","private prison","sentencing reform",
    "mandatory minimum","three strikes law","juvenile justice","school to prison pipeline","truancy","dropout rate",
    "education crisis","teacher shortage","voucher program","charter school","homeschooling boom","Epstein client list",
    "Lolita Express","Epstein black book","elite pedophile ring","MeToo movement","whistleblower protection","retaliation claim",
    "discrimination lawsuit","class action","supply chain disruption","port backlog","shipping container shortage","Ever Given",
    "maritime security","insurance premium","freight cost","inflation driver","consumer price index","CPI report",
    "PCE inflation","core inflation","great resignation","quiet quitting","return to office","hybrid work",
    "banking crisis","Signature Bank","First Republic","regional bank stress","deposit flight","too big to fail",
    "Dodd-Frank","stress test","capital requirement","Basel III","financial stability","systemic risk",
    "contagion fear","market crash","safe haven","soft landing","hard landing","oil shock",
    "OPEC oil embargo","Iran hostage crisis","Reagan recovery","supply side economics","tax cut","corporate tax rate",
    "estate tax","wealth tax","billionaire tax","progressive taxation","flat tax","consumption tax",
    "VAT proposal","border adjustment tax","tariff war","trade deficit","Phase One deal","Section 301",
    "intellectual property theft","forced technology transfer","unfair trade practice","WTO complaint","trade imbalance","manufacturing revival",
    "reshoring","nearshoring","friendshoring","supply chain resilience","chip shortage","semiconductor fab",
    "TSMC Arizona","Intel Ohio","CHIPS Act","subsidy package","Made in America","Buy American",
    "bipartisan infrastructure law","green jobs","union labor","prevailing wage","apprenticeship program","skilled trades",
    "plumber shortage","electrician demand","construction boom","housing shortage","zoning reform","NIMBY opposition",
    "YIMBY movement","density bonus","transit oriented development","California bullet train","cost overrun","project delay",
    "Amtrak expansion","passenger rail","freight rail strike","rail safety","derailment risk","East Palestine train derailment",
    "chemical spill","vinyl chloride","evacuation zone","toxic plume","EPA response","Superfund site",
    "environmental disaster","cleanup cost","liability claim","class action lawsuit","corporate negligence","whistleblower reward",
    "SEC whistleblower","qui tam","False Claims Act","government fraud","defense contract fraud","overbilling",
    "cost plus contract","no bid contract","sole source","emergency procurement","COVID contract","ventilator scandal",
    "PPE shortage","mask contract","hydroxychloroquine","ivermectin debate","repurposed drug","off label use",
    "vaccine injury","excess mortality","life expectancy drop","fertility decline","birth rate collapse","demographic crisis",
    "population decline","immigration solution","replacement migration","dual citizenship","anchor baby","birthright citizenship",
    "14th Amendment","citizenship question","census count","apportionment","electoral college reform","national popular vote",
    "compact agreement","faithless elector","January 6 committee","select committee","subpoena power","contempt charge",
    "Steve Bannon","Peter Navarro","Mark Meadows","Cassidy Hutchinson","testimony leak","bombshell revelation",
    "closed door session","public hearing","primetime hearing","political theater","unity call","bridge building",
    "bipartisanship","gridlock","filibuster reform","nuclear option","reconciliation bill","budget resolution",
    "omnibus spending","continuing resolution","government funding","shutdown brinkmanship","debt limit crisis","extraordinary measures",
    "Treasury default risk","Supreme Court intervention","emergency powers","martial law rumor","Insurrection Act","National Guard deployment",
    "federal troops","state sovereignty","sanctuary state","federal preemption","immigration enforcement","Title 42 expiration",
    "catch and release policy","parole program","humanitarian parole","CBP One app","immigration court","judge shortage",
    "ICE detention","family detention","child separation","zero tolerance","family reunification","DACA renewal",
    "Dreamers","TPS extension","temporary protected status","deportation moratorium","Biden border policy","Trump wall funding",
    "remain in Mexico","MPP program","Title 8 expulsion","border surge","migrant wave","record crossing",
    "gotaways","border encounter statistic","apprehension number","fentanyl flow","cartel profit","human smuggling",
    "coyote fee","border tunnel","drug tunnel","narco submarine","go fast boat","maritime interdiction",
    "Coast Guard seizure","drug interdiction","high seas boarding","joint operation","DEA task force","FBI joint terrorism task force",
    "counterterrorism fusion center","fusion center","intelligence sharing","tip line","money laundering","shell company",
    "law enforcement takedown","international sting","Europol operation","Interpol red notice","fugitive capture","extradition treaty",
    "Julian Assange extradition","Edward Snowden asylum","political refugee","dissident protection","free speech advocate","press freedom",
    "journalist arrest","reporter jailed","shield law","source protection","leak prosecution","Espionage Act charge",
    "Pentagon Papers","prior restraint","freedom of the press","first amendment","speech code","trigger warning",
    "content warning","divestment campaign","police abolition","prison abolition","defund narrative","community safety",
    "violence interrupter","cure violence","gunshot detection","ShotSpotter","predictive policing","facial recognition ban",
    "surveillance camera","ring doorbell","neighbor app","crime map","public safety dashboard","crime statistic",
    "homicide rate","violent crime spike","carjacking surge","smash and grab retail","looting incident","flash mob robbery",
    "organized theft ring","porch piracy","package theft","catalytic converter theft","scrap metal theft","infrastructure vandalism",
    "train derailment","bridge collapse","dam failure","levee breach","flood control","Army Corps of Engineers",
    "disaster declaration","major disaster","national preparedness","continuity of government","presidential succession","line of succession",
    "25th Amendment","cabinet invocation","acting president","temporary incapacity","health crisis","presidential fitness",
    "cognitive test","physician letter","transparency demand","medical report","White House physician","annual physical",
    "Air Force One","Marine One","presidential limo","secret service detail","advance team","protective detail",
    "counter assault team","presidential motorcade","route security","perimeter security","crowd control","protest zone",
    "designated protest area","national special security event","Super Bowl security","convention security","inauguration security","state of the union",
    "joint session","opposition response","rebuttal speech","Oval Office address","primetime speech","Truth Social",
    "former president account","shadow ban lift","algorithm change","hashtag campaign","meme warfare","keyboard warrior",
    "news cycle","breaking news","live coverage","cable news panel","pundit class","talking head",
    "spin room","press gaggle","press secretary","daily briefing","podium moment","off the record",
    "background briefing","deep background","source familiar","anonymous official","leak strategy","controlled leak",
    "damaging leak","document leak","classified leak","top secret document","need to know","clearance level",
    "security clearance","polygraph","background investigation","foreign contact report","insider threat","espionage indicator",
    "mole hunt","counterintelligence","FBI counterintel","CIA counterintel","double agent","asset recruitment",
    "handler","case officer","dead drop","covert communication","anonymous board","information warfare",
    "red line","trip wire","flashpoint","Middle East flashpoint","choke point","maritime domain awareness",
    "frigate program","joint all domain command","plutonium reprocessing","missile test","submarine launched ballistic missile","resource competition",
    "trade pillar","clean energy pillar","marine security guard","diplomatic security service","peace treaty","status quo",
    "de facto control","referendum vote","naval base","war crime charge","force protection","Chapter VII",
    "clear hold build","influence campaign","exchange program","foreign aid budget","conditionality","good governance",
    "anti corruption","luxury property","leak expose","consortium report","global scoop","front page",
    "above the fold","anonymous sourcing","on background","not for attribution","off the record comment","embargo lift",
    "publication time","news dump","Friday night drop","holiday weekend release","document release","FOIA request",
    "records request","agency response","redaction battle","lawsuit filed","court order","unsealing motion",
    "public interest","transparency lawsuit","watchdog group","judicial watch","heritage action","project veritas",
    "sting operation","hidden camera","undercover video","expose video","whistleblower tape","internal memo",
    "leaked email","server image","classified server","private server","email scandal","server wipe",
    "deleted email","recovery attempt","congressional hearing","contempt citation","referral","special prosecutor",
    "independent counsel","statute of limitations","obstruction charge","perjury trap","false statement","lying to federal agent",
    "plea deal","cooperation agreement","immunity grant","witness protection","relocation","informant protection",
    "flip witness","testify against","kingpin prosecution","RICO charge","racketeering","conspiracy count",
    "money laundering count","asset forfeiture","civil forfeiture","seizure warrant","probable cause","search warrant",
    "knock and announce","no knock entry","dynamic entry","flash bang","breach team","tactical unit",
    "SWAT callout","barricade situation","hostage rescue","negotiator team","crisis intervention","mental health call",
    "welfare check","domestic disturbance","officer involved shooting","body cam release","dash cam footage","use of force review",
    "internal affairs","civilian review board","police commission","accountability measure","reform package","consent decree",
    "DOJ pattern practice","civil rights division",
    # ── US City Names ──
    "New York","Los Angeles","Chicago","Houston","Phoenix","Philadelphia","San Antonio","San Diego",
    "Dallas","Jacksonville","Fort Worth","San Jose","Austin","Charlotte","Columbus","Indianapolis",
    "San Francisco","Seattle","Denver","Oklahoma City","Nashville","Washington DC","El Paso","Las Vegas",
    "Boston","Detroit","Louisville","Portland","Memphis","Baltimore","Milwaukee","Albuquerque","Tucson",
    "Fresno","Sacramento","Atlanta","Mesa","Kansas City","Raleigh","Colorado Springs","Omaha","Miami",
    "Virginia Beach","Long Beach","Oakland","Minneapolis","Bakersfield","Tulsa","Tampa","Arlington",
    "Aurora","Wichita","Cleveland","New Orleans","Henderson","Honolulu","Anaheim","Orlando","Lexington",
    "Stockton","Riverside","Irvine","Newark","Santa Ana","Cincinnati","Pittsburgh","Saint Paul",
    "Greensboro","Jersey City","Durham","Lincoln","North Las Vegas","Plano","Anchorage","Gilbert",
    "Madison","Reno","Chandler","St. Louis","Chula Vista","Buffalo","Fort Wayne","Lubbock",
    "St. Petersburg","Toledo","Laredo","Port St. Lucie","Glendale","Irving","Winston-Salem",
    "Chesapeake","Garland","Scottsdale","Boise","Hialeah","Frisco","Richmond","Cape Coral","Norfolk",
    "Spokane","Huntsville","Santa Clarita","Tacoma","Fremont","McKinney","San Bernardino","Baton Rouge",
    "Modesto","Fontana","Salt Lake City","Moreno Valley","Des Moines","Worcester","Yonkers","Fayetteville",
    "Sioux Falls","Grand Prairie","Rochester","Tallahassee","Little Rock","Amarillo","Overland Park",
    "Augusta","Mobile","Oxnard","Grand Rapids","Peoria","Vancouver","Knoxville","Birmingham",
    "Montgomery","Providence","Huntington Beach","Brownsville","Chattanooga","Fort Lauderdale","Tempe",
    "Akron","Clarksville","Ontario","Newport News","Elk Grove","Cary","Salem","Pembroke Pines","Eugene",
    "Santa Rosa","Rancho Cucamonga","Shreveport","Garden Grove","Oceanside","Fort Collins","Springfield",
    "Murfreesboro","Surprise","Lancaster","Denton","Roseville","Palmdale","Corona","Salinas","Killeen",
    "Paterson","Alexandria","Hollywood","Hayward","Charleston","Macon","Lakewood","Sunnyvale","Naperville",
    "Joliet","Bridgeport","Mesquite","Pasadena","Olathe","Escondido","Savannah","McAllen","Gainesville",
    "Pomona","Rockford","Thornton","Waco","Visalia","Syracuse","Columbia","Midland","Miramar","Palm Bay",
    "Jackson","Coral Springs","Victorville","Elizabeth","Fullerton","Meridian","Torrance","Stamford",
    "West Valley City","Orange","Cedar Rapids","Warren","Hampton","New Haven","Kent","Dayton","Fargo",
    "Lewisville","Carrollton","Round Rock","Sterling Heights","Santa Clara","Norman","Abilene","Pearland",
    "Athens","College Station","Clovis","West Palm Beach","Allentown","North Charleston","Simi Valley",
    "Topeka","Wilmington","Lakeland","Thousand Oaks","Concord","Vallejo","Ann Arbor","Broken Arrow",
    "Fairfield","Lafayette","Hartford","Arvada","Berkeley","Independence","Billings","Cambridge","Lowell",
    "Odessa","High Point","League City","Antioch","Richardson","Goodyear","Pompano Beach","Nampa",
    "Menifee","Las Cruces","Clearwater","West Jordan","New Braunfels","Manchester","Miami Gardens",
    "Waterbury","Provo","Evansville","Westminster","Elgin","Conroe","Greeley","Lansing","Buckeye",
    "Tuscaloosa","Allen","Carlsbad","Everett","Beaumont","Murrieta","Rio Rancho","Temecula","Tyler",
    "Davie","South Fulton","Sparks","Gresham","Santa Maria","Pueblo","Hillsboro","Sugar Land","Ventura",
    "Downey","Costa Mesa","Centennial","Edinburg","Spokane Valley","Jurupa Valley","Bend","West Covina",
    "Boulder","Palm Coast","Lee's Summit","Dearborn","Green Bay","St. George","Woodbridge","Brockton",
    "Renton","Sandy Springs","Rialto","El Monte","Vacaville","Fishers","South Bend",
    # ── US State Names ──
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida",
    "Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
    "Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska",
    "Nevada","New Hampshire","New Jersey","New Mexico","North Carolina","North Dakota","Ohio","Oklahoma",
    "Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Utah","Vermont",
    "Virginia","West Virginia","Wisconsin","Wyoming",
    # ── US State Capitals ──
    "Juneau","Hartford","Dover","Frankfort","Annapolis","Lansing","Saint Paul","Jefferson City","Helena",
    "Carson City","Concord","Trenton","Santa Fe","Albany","Bismarck","Harrisburg","Pierre","Montpelier",
    "Olympia","Charleston","Cheyenne",
]
US_KEYWORDS = set(kw.lower() for kw in RAW_US_KEYWORDS)

RAW_SPORTS_KEYWORDS = [
    "march madness","college basketball","arizona wildcats","purdue boilermakers",
    "miami hurricanes","villanova wildcats","utah state aggies","ncaa tournament",
    "ncaa bracket","march madness bracket","sports news","latest sports news",
    "breaking sports news","football news","nfl news","nba news","mlb news","nhl news",
    "soccer news","premier league news","champions league news","world cup news",
    "fifa world cup","copa america","euro cup","la liga news","serie a news",
    "bundesliga news","mls news","college football news","college basketball news",
    "nba finals","super bowl","world series","stanley cup","olympics news",
    "olympics schedule","olympics results","summer olympics","winter olympics",
    "tennis news","grand slam tennis","wimbledon news","us open tennis",
    "australian open tennis","french open tennis","atp rankings","wta rankings",
    "formula 1 news","f1 standings","f1 race results","f1 qualifying","f1 drivers",
    "lewis hamilton news","max verstappen news","ferrari f1","mercedes f1",
    "red bull racing","golf news","pga tour news","masters tournament","us open golf",
    "british open golf","ryder cup","tiger woods news","surfing news","world surf league",
    "surfing competitions","big wave surfing","surf forecast","nba trade rumors",
    "nfl trade rumors","mlb trades","transfer rumors soccer","transfer window",
    "player injuries","injury report nfl","nba injury report","fantasy football",
    "fantasy basketball","fantasy sports news","sports betting news","esports news",
    "college recruiting news","draft prospects nfl","nba draft news","mlb draft",
    "nhl draft","sports analytics","advanced stats sports","player statistics",
    "team standings","league standings","power rankings","sports highlights","game recap",
    "post match analysis","sports commentary","athlete interviews","locker room news",
    "coaching changes","head coach firing","sports scandals","doping scandals",
    "anti doping agency","olympic doping cases","sports law","contract negotiations",
    "player contracts","salary cap nfl","salary cap nba","free agency news",
    "transfer fees soccer","youth academy soccer","women sports news","wnba news",
    "women soccer news","women tennis news","women golf news","title ix sports",
    "college athletics news","ncaa rules","nil deals college athletes",
    "sponsorship deals athletes","sports marketing","sports media rights",
    "broadcasting deals sports","streaming sports","live sports streaming",
    "sports tv ratings","fan attendance sports","stadium news","arena construction",
    "sports business news","franchise valuations","team ownership news","league expansion",
    "expansion teams","relocation teams","sports history","greatest athletes",
    "hall of fame sports","olympic history","world records sports","track and field news",
    "marathon running news","cycling tour de france","cycling news","boxing news",
    "mma news","ufc fights","fight night results","boxing title fights","heavyweight boxing",
    "sports injuries recovery","athlete training","sports science","nutrition athletes",
    "fitness training sports","sports psychology","mental health athletes",
    "fan reactions sports","social media sports trends","viral sports moments",
    "sports controversies","referee decisions","var decisions soccer",
    "instant replay sports","officiating controversies","sports governance",
    "fifa governance","ioc decisions","ncaa decisions","sports politics","olympic boycotts",
    "national team news","international friendlies","qualifiers world cup",
    "regional tournaments","asian cup soccer","african cup nations","concacaf gold cup",
    "sports rivalries","el clasico","manchester derby","nba rivalries","nfl rivalries",
    "buzzer beater shots","overtime games","penalty shootouts","comeback victories",
    "underdog wins","championship celebrations","trophy presentations","medal ceremonies",
    "sports technology","var technology","goal line technology","wearable tech athletes",
    "performance tracking sports","analytics software sports","scouting reports",
    "talent evaluation","combine results nfl","pro day results","training camp updates",
    "preseason games","regular season schedule","playoff bracket","postseason results",
    "finals mvp","league mvp","rookie of the year","defensive player of the year",
    "golden boot soccer","heisman trophy","sports awards","athlete retirements",
    "comeback stories athletes","transfer confirmations","contract extensions",
    "loan deals soccer","sports agencies","agent negotiations","youth tournaments",
    "high school sports news","amateur sports news","grassroots sports","outdoor sports news",
    "surfing conditions","beach conditions surfing","swell forecast",
    "surf competitions schedule","extreme sports news","x games","skateboarding news",
    "snowboarding news","skiing competitions","climbing competitions","triathlon events",
    "ironman competitions","motorsports news","nascar news","indycar news",
    "rally racing news","endurance racing","le mans 24 hours","formula e news",
    "sports innovation","fan engagement sports","ticket sales sports",
    "merchandise sales sports","sports branding","media interviews athletes",
    "press conferences sports","training drills","game day preparation",
    "tactical analysis sports","formations soccer","playbooks nfl","offensive schemes nba",
    "defensive strategies sports","coaching tactics","sports journalism",
    "sports documentaries","behind the scenes sports","iconic moments sports",
    "front office sports","sportico","sports business journal","defector sports",
    "bleacher report","yardbarker","sb nation","sportskeeda","goal.com","marca english",
    "l equipe","cricbuzz","espncricinfo","mma fighting","boxing scene","golf digest",
    "motorsport.com","autosport","cyclingnews","world rugby","rugbypass",
    "cricket australia","the ringer sports","players tribune","awful announcing",
    "sports media watch","march madness 2026","ncaa mens basketball 2026",
    "march madness scores 2026","super bowl 2026","winter olympics 2026",
    "nfl draft 2026","nba playoffs 2026","mlb opening day 2026","nhl stanley cup 2026",
    "kentucky derby 2026","wimbledon 2026","us open 2026","masters 2026",
    "world cup","boxing","world boxing","wembley","golf","olympics","olympic",
    "overtime","brackets","huge lead","all-time","champ","champion","boxer","fighter",
    "competition","chess","surfing","surfing event","surfing events","surf",
    "f1","race","races","racing","f1 race","f1 races","f1 racing",
    # ── Major Multi-Sport Events ──
    "2026 winter olympics milano cortina","2026 winter paralympics milano cortina",
    "2026 fifa world cup usa canada mexico","2026 commonwealth games glasgow",
    "2026 asian games aichi nagoya","2026 world baseball classic",
    "2026 icc mens t20 world cup sri lanka india","2028 summer olympics los angeles",
    "2027 fifa womens world cup brazil","2027 mens rugby world cup australia",
    "2027 cricket world cup south africa","2027 ryder cup adare manor ireland",
    "2027 netball world cup","2027 pan american games lima",
    "2027 world athletics championships beijing",
    "2027 british irish lions womens tour new zealand",
    "milano cortina 2026","commonwealth games 2026","asian games 2026",
    # ── Tennis Grand Slams ──
    "2026 australian open","2026 french open","2026 wimbledon championships","2026 us open tennis",
    "2027 australian open","2027 french open","2027 wimbledon championships","2027 us open tennis",
    "2028 australian open","2028 french open","2028 wimbledon championships","2028 us open tennis",
    # ── Golf Majors ──
    "the masters 2026","the masters 2027","the masters 2028",
    "pga championship 2026","pga championship 2027","pga championship 2028",
    "us open golf 2026","us open golf 2027","us open golf 2028",
    "the open championship 2026","the open championship 2027","the open championship 2028",
    # ── American Football ──
    "super bowl lxi 2027","super bowl lxii 2028",
    # ── Basketball ──
    "nba finals 2026","nba finals 2027","nba finals 2028",
    # ── Soccer ──
    "uefa champions league final 2026","uefa champions league final 2027","uefa champions league final 2028",
    "uefa europa league final 2026","uefa europa league final 2027","uefa europa league final 2028",
    "fifa club world cup 2026",
    # ── Cycling ──
    "tour de france 2026","tour de france 2027","tour de france 2028",
    # ── Motor Racing ──
    "monaco grand prix 2026","monaco grand prix 2027","monaco grand prix 2028",
    "formula 1 australian grand prix 2026","formula 1 australian grand prix 2027","formula 1 australian grand prix 2028",
    "formula 1 miami grand prix 2026","formula 1 japanese grand prix 2026",
    "24 hours of le mans 2026","24 hours of le mans 2027","24 hours of le mans 2028",
    "le mans 2026","le mans 2027","le mans 2028",
    "daytona 500 2026","daytona 500 2027","daytona 500 2028",
    "2028 daytona 500","2028 le mans",
    # ── Marathons ──
    "boston marathon 2026","boston marathon 2027","boston marathon 2028",
    "new york city marathon 2026","new york city marathon 2027","new york city marathon 2028",
    "london marathon 2026","london marathon 2027","london marathon 2028",
    "2026 tokyo marathon","2027 tokyo marathon","2028 tokyo marathon",
    # ── Rugby ──
    "six nations rugby championship 2026","six nations rugby championship 2027","six nations rugby championship 2028",
    # ── Baseball / Cricket ──
    "world series 2026","world series 2027","world series 2028",
    "indian premier league final 2026","indian premier league final 2027","indian premier league final 2028",
    # ── Ice Hockey ──
    "stanley cup finals 2026","stanley cup finals 2027","stanley cup finals 2028",
    # ── Horse Racing ──
    "kentucky derby 2026","kentucky derby 2027","kentucky derby 2028",
    "2026 grand national","2027 grand national","2028 grand national",
    "2026 cheltenham festival","2027 cheltenham festival","2028 cheltenham festival",
    # ── Sailing ──
    "americas cup 2027",
    # ── March/April 2026 Near-Term ──
    "march madness second round march 2026","march madness sweet sixteen 2026",
    "march madness elite eight 2026","march madness final four april 2026",
    "ncaa national championship april 2026","the masters tournament april 2026",
    "formula 1 japanese grand prix march 2026","masters par 3 contest 2026",
    "ncaa final four indianapolis 2026","suzuka fan zone 2026",
]
SPORTS_KEYWORDS = set(kw.lower() for kw in RAW_SPORTS_KEYWORDS)

RAW_TECH_KEYWORDS = [
    "technology news","latest tech news","emerging technology","cutting edge technology",
    "future technology","tech trends 2026","artificial intelligence","ai news",
    "ai breakthroughs","generative ai","machine learning","deep learning","neural networks",
    "ai regulation","ai ethics","robotics","humanoid robots","automation technology",
    "quantum computing","quantum supremacy","cloud computing","edge computing",
    "cybersecurity","data breaches","hacking news","ransomware attacks","zero day exploit",
    "encryption technology","blockchain technology","cryptocurrency trends","web3",
    "metaverse technology","augmented reality","virtual reality","mixed reality",
    "spatial computing","apple vision pro","vr gaming","ar glasses","wearable technology",
    "smart devices","internet of things","iot devices","smart home tech","home automation",
    "voice assistants","natural language processing","big data analytics","data science",
    "software development","programming languages","python programming","javascript trends",
    "open source software","linux news","windows updates","macos updates","mobile technology",
    "smartphone releases","android updates","iphone news","semiconductor industry",
    "chip shortage","gpu technology","cpu benchmarks","nvidia news","amd processors",
    "intel chips","silicon valley startups","venture capital tech","startup funding",
    "tech ipo","unicorn startups","big tech companies","google news","apple news",
    "microsoft news","amazon technology","meta platforms","social media technology",
    "algorithm changes","content moderation","digital privacy","online security",
    "surveillance technology","biometric systems","facial recognition","autonomous vehicles",
    "self driving cars","electric vehicles","ev battery technology","tesla updates",
    "charging infrastructure","hydrogen fuel cells","automotive technology",
    "transportation technology","high speed rail","hyperloop","aviation technology",
    "aircraft design","aerospace engineering","spacex launches","nasa missions",
    "mars exploration","moon missions","satellite technology","starlink internet",
    "space telescopes","astrophysics discoveries","astronomy news","black holes",
    "exoplanets","cosmology research","physics breakthroughs","particle physics",
    "cern research","biology research","genetics","dna sequencing","crispr technology",
    "gene editing","biotechnology","medical technology","healthcare innovation",
    "vaccines research","pharmaceuticals development","neuroscience",
    "brain computer interfaces","bci technology","environmental science",
    "climate change research","renewable energy","solar power technology","wind energy",
    "battery storage","sustainability tech","green technology","carbon capture",
    "water purification","ocean exploration","marine biology","wildlife conservation",
    "ecology research","outdoor gear technology","camping gear innovation",
    "hiking equipment","survival gear","gps navigation","satellite navigation",
    "drones technology","drone photography","drone regulations","gaming industry news",
    "video game releases","game development","game engines","unreal engine","unity engine",
    "esports news","competitive gaming","streaming platforms","twitch streaming",
    "youtube gaming","gaming hardware","gaming pcs","gaming laptops","graphics cards",
    "ray tracing","dlss technology","vr gaming trends","indie game development",
    "digital distribution","steam platform","epic games store","game monetization",
    "microtransactions","gaming controversies","entertainment technology",
    "streaming services","netflix technology","disney plus tech","content delivery networks",
    "5g networks","6g research","telecommunications technology","fiber internet",
    "broadband expansion","digital infrastructure","smart cities technology",
    "urban tech innovation","fintech innovation","digital banking","payment systems",
    "blockchain finance","cybersecurity threats","ethical hacking","penetration testing",
    "devops practices","agile development","software engineering trends",
    "hardware engineering","embedded systems","nanotechnology","materials science",
    "3d printing","additive manufacturing","industrial automation","manufacturing technology",
    "supply chain technology","logistics innovation","retail technology","e commerce trends",
    "digital marketing tech","seo trends","search algorithms","google algorithm updates",
    "data privacy laws","gdpr compliance","digital rights","internet governance",
    "future of work technology","remote work tools","collaboration software",
    "productivity tools","human computer interaction","user experience design",
    "ui ux trends","digital transformation","enterprise technology","saas platforms",
    "cloud infrastructure","server technology","data centers","green computing",
    "energy efficient computing","ethical ai development","responsible innovation",
    "tech policy","government regulation tech","antitrust tech","innovation ecosystems",
    "research and development trends","crypto","rockets","rocket technology",
    "spacecraft","orbit","satellite","earth","history","archeology","dinosaur","dinosaurs",
    "grok","openai","nvidia","meta","telescope","observatory","machu picchu","artifacts",
    "southeast asia","reuters technology news","associated press technology news",
    "ai goes physical 2026","agentic reality check 2026","ai infrastructure reckoning 2026",
    "ai native tech organization 2026","ai native development platforms 2026",
    "ai supercomputing platforms 2026","confidential computing 2026",
    "multiagent systems 2026","domain specific language models 2026","physical ai 2026",
    "preemptive cybersecurity 2026","digital provenance 2026","ai security platforms 2026",
    "geopatriation 2026","cloud 3.0 hybrid multi cloud 2026","intelligent ops 2026",
    "tech sovereignty 2026","resilient supply chain sourcing 2026",
    "multi agent orchestration 2026","practical ai adoption 2026",
    "open standards data centers 2026","cloud sovereignty 2026",
    "post quantum cryptography 2026","neuromorphic computing 2026",
    "quantum communication 2026","edge ai everywhere 2026",
    "hyperscale ai data centers 2026","new nuclear reactors 2026",
    "sodium ion batteries 2026","autonomous mobility 2026","ai coding tools 2026",
    "prompt engineering 2026","vector database 2026","workflow automation 2026",
    "ai translator headphones 2026","iphone 18 rumors 2026","samsung galaxy s26 2026",
    "pixel 11 release date 2026","best android phone 2026","ces 2026 ai robots",
    "paper thin tvs 2026","bendable screens 2026","ai powered exoskeletons 2026",
    "nvidia dlss 5 2026","openai astral acquisition 2026","nvidia amazon chip deal 2026",
    "baidu ai lobsters 2026","openai desktop superapp 2026","ai for coding 2026",
    "ai for writing 2026","ai for image generation 2026","best ai for math 2026",
    "ai agents 2026","physical ai robotics 2026","multiagent ai systems 2026",
    "domain specific ai models 2026","confidential computing encryption 2026",
    "ai supercomputing 2026","preemptive cyber ai 2026","digital provenance ai 2026",
    "intelligent operations ai 2026","neuromorphic chips 2026",
    "post quantum crypto standards 2026","edge ai inference 2026",
    "hyperscale data center energy 2026","ces 2026 gadgets ai","nvidia gtc 2026",
    "openai gpt updates 2026","anthropic claude agents 2026","tesla robotaxi 2026",
    "spacex starship 2026","nasa artemis 2026","quantum supremacy milestones 2026",
    "crispr gene editing advances 2026","brain computer interfaces neuralink 2026",
    "ev battery sodium ion 2026","6g research trials 2026","smart cities ai 2026",
    "sustainable green computing 2026","carbon capture tech 2026",
    "drone regulations updates 2026","vr ar spatial computing 2026",
    "apple vision pro 2 2026","meta quest 4 2026","gaming ray tracing dlss 2026",
    "esports ai coaching 2026","fintech blockchain 2026","digital privacy gdpr 2026",
    "remote work ai tools 2026","saas ai platforms 2026",
    "reuters ai breakthroughs 2026","associated press artificial intelligence 2026",
    "ars technica","techradar","venturebeat","popular science","scientific american",
    "agentic ai","most capable ai model","ai career","ai creativity","daily habits ai",
    "breakout searches 2026","labubu collectible","kpop demon hunters",
    "viral media hits","ai tools trend","chatgpt searches 2026","ai overviews google",
    "gemini ai","tiktok 2026","streaming consolidation 2026",
    "drone","drones","messaging apps","smartphone","smartphones","kc-135","iphone",
    "spyware","satellite","satellites","netflix","amazon video","hulu video",
    "paramount+","streaming","streamers","streamer","stream","meteor","meteorite",
    "asteroid","nuclear","nuclear energy","tech","tech tips","ai regulation",
    "ai","ai laws","nasa","moon","moon rocket","moon rockets","launch","new study",
    "data","data center","data centers","data harvesting","technology",

    "refinery fire","pipeline explosion","shale oil","ChatGPT","fracking boom","cyber attack",
    "ransomware","critical infrastructure","grid blackout","power outage","solar panel","wind farm",
    "green transition","carbon emissions","net zero","Paris Agreement","COP summit","electric vehicle",
    "EV charging","battery shortage","lithium mining","cobalt supply","Tesla stock","tech stocks",
    "Nasdaq rally","Federal Reserve","interest rates","rate hike","rate cut","quantitative easing",
    "bond yield","treasury bonds","vaccine hesitancy","booster shot","mRNA technology","gain of function",
    "lab leak","Wuhan lab","bioweapon","Keystone XL cancellation","net zero target","IRA subsidies",
    "EV tax credit","solar tax credit","wind energy subsidy","fossil fuel phaseout","coal plant closure","nuclear revival",
    "small modular reactor","SMR","fusion energy","breakthrough fusion","clean energy transition","grid modernization",
    "blackout risk","cyber vulnerability","EMP threat","solar flare","geomagnetic storm","space weather",
    "Starlink","satellite internet","SpaceX","Elon Musk","Twitter files","censorship",
    "shadow ban","Section 230","big tech monopoly","antitrust lawsuit","Google breakup","Amazon antitrust",
    "app store fees","Epic vs Apple","TikTok ban","data privacy","surveillance state","NSA spying",
    "FISA warrant","Patriot Act renewal","domestic surveillance","warrantless wiretap","encryption backdoor","online safety bill",
    "Section 702 reauthorization","China spy balloon","hypersonic glide vehicle","carrier killer missile","DF-21","anti-access area denial",
    "community notes","misinformation label","deepfake","AI generated","voice cloning","election deepfake",
    "synthetic media","platform liability","algorithm bias","crypto crash","Bitcoin halving","altcoin rally",
    "meme coin","dogecoin","NFT boom","NFT bust","metaverse hype","virtual land",
    "Roblox stock","tech layoff","Silicon Valley","venture capital","IPO market","SPAC merger",
    "meme stock","GameStop squeeze","WallStreetBets","retail investor","Robinhood trading","zero commission",
    "trading app","crypto exchange","Coinbase stock","Binance fine","regulatory crackdown","SEC lawsuit",
    "Ripple case","XRP ruling","stablecoin regulation","CBDC pilot","digital dollar","FedNow",
    "instant payment","Silicon Valley Bank","SVB collapse","flash crash","circuit breaker","trading halt",
    "volatility spike","VIX index","gold price","silver rally","bitcoin safe haven","digital gold",
    "treasury yield curve","inverted yield curve","recession indicator","stagflation risk","FDA emergency use","VAERS report",
    "adverse event","myocarditis risk","blood clot","suspicious activity report","SAR filing","bank secrecy act",
    "beneficial ownership","corporate transparency act","FinCEN rule","crypto mixer","Tornado Cash sanction","privacy coin",
    "dark web market","shadow ban lift","encrypted app","Signal use","Wickr","Telegram channel",
    "fact check debunk","post truth era","fake news epidemic","disinformation age","information warfare","hybrid threat",
    # ── Video Game Titles ──
    "grand theft auto v","the witcher 3 wild hunt","minecraft","counter-strike 2",
    "red dead redemption 2","half-life 2","elden ring","the elder scrolls v skyrim",
    "portal 2","baldurs gate 3","disco elysium","bioshock","half-life","dwarf fortress",
    "kerbal space program","into the breach","wildermyth","straftat","the last of us",
    "breath of the wild","super mario world","tetris","resident evil 4","mass effect 2",
    "fallout new vegas","doom","quake","starcraft","world of warcraft","civilization",
    "the sims","super mario 64","ocarina of time","super mario galaxy","portal",
    "bioshock infinite","grand theft auto iv","uncharted 2","metal gear solid 3",
    "final fantasy vii","chrono trigger","earthbound","persona 5","nier automata",
    "sekiro shadows die twice","bloodborne","dark souls","god of war","horizon zero dawn",
    "ghost of tsushima","marvels spider-man","animal crossing new horizons","hades",
    "it takes two","fortnite","apex legends","league of legends","overwatch","cyberpunk 2077",
    "starfield","black myth wukong","helldivers 2","palworld","valorant","among us",
    "a way out","dragon age origins","the witcher 2","fallout 3","the elder scrolls iv oblivion",
    "the elder scrolls iii morrowind","doom eternal","wolfenstein the new order",
    "metro exodus","control remedy","death stranding","tears of the kingdom",
    "super mario odyssey","pac-man","space invaders","street fighter ii","mortal kombat",
    "tekken","phoenix wright ace attorney","simcity","age of empires","command and conquer",
    "diablo ii",
    # ── Upcoming / Anticipated Game Titles ──
    "gta vi","gta 6","marvels wolverine","resident evil requiem","007 first light",
    "forza horizon 6","fable 2025","pragmata","tomb raider legacy of atlantis",
    "control resonant","phantom blade zero","subnautica 2","warhammer 40k dawn of war 4",
    "crimson desert","death stranding 2","slay the spire 2",
    "monster hunter stories 3 twisted reflection","nioh 3","marathon bungie",
    "toxic commando","saros game","cairn game","hytale","code vein 2",
    "mio memories in orbit","kingmakers game","romeo is a dead man","mina the hollower",
    "legacy of kain defiance remastered","heartopia","blasten","cozy caravan",
    "fire emblem fortunes weave","ace combat 8","the duskbloods","super meat boy 3d",
    "replaced game","kusan city of wolves","let it die offline edition","the lift game",
    "limit zero breakers","little samson","professor layton new world of steam",
    "pokemon champions","tomodachi life living the dream","mario tennis fever",
    "yoshi and the mysterious book","gears of war e-day","onimusha way of the sword",
    "halo ce remaster","wow midnight","solasta 2","deep rock galactic rogue core",
    # ── Game Studios ──
    "rockstar games","naughty dog","santa monica studio","insomniac games",
    "sucker punch productions","guerrilla games","kojima productions","fromsoftware",
    "larian studios","cd projekt red","epic games","valve corporation",
    "blizzard entertainment","riot games","ubisoft montreal","bioware",
    "obsidian entertainment","bethesda game studios","343 industries","id software",
    "infinity ward","treyarch","dice ea","crystal dynamics","eidos-montreal",
    "square enix","capcom","bandai namco","sega","konami","nintendo epd",
    "retro studios","game freak","supergiant games","hazelight studios",
    "hello games","moon studios","team cherry","remedy entertainment",
    "platinumgames","atlus","falcom","arkane studios","machinegames",
    "respawn entertainment","bungie","thatgamecompany","deck nine games",
    "raven software","popcap games","firaxis games","creative assembly",
    "relic entertainment","paradox development studio","gearbox software",
    "io interactive","avalanche studios","frontier developments","splash damage",
    "crytek","double fine productions","sandfall interactive","warhorse studios",
    "11 bit studios","owlcat games","amplitude studios","subset games",
    "motion twin","ludeon studios","grinding gear games","nixxes software",
    "bluepoint games","housemarque","team ico","gendesign","iron galaxy",
    "high moon studios","volition","psyonix","massive entertainment",
    "ubisoft quebec","ubisoft toronto","ubisoft paris","ubisoft sofia",
    "monolith soft","intelligent systems","creatures inc","hal laboratory",
    "camelot software planning","juego studios","kevuru games","stepico",
    "pingle studio","starloop studios","whimsy games","virtuos","sperasoft",
    "n-ix game vr studio","pushka studios","ulysses graphics",
]
TECH_KEYWORDS = set(kw.lower() for kw in RAW_TECH_KEYWORDS)

RAW_CULTURE_KEYWORDS = [
    "celebrity news","celebrity gossip","hollywood news","red carpet fashion",
    "awards show coverage","oscars red carpet","golden globes fashion","emmys fashion",
    "met gala looks","fashion week paris","fashion week milan","fashion week new york",
    "fashion week london","haute couture","ready to wear fashion","runway shows",
    "supermodels","model agency","modeling portfolios","model casting calls",
    "swimsuit models","bikini models","lingerie modeling","high fashion editorial",
    "fashion photographers","celebrity photographers","paparazzi photos",
    "celebrity shoots","photoshoots behind the scenes","fashion magazines",
    "fashion editorials","vogue covers","style trends","fashion trends","street style",
    "beauty trends","makeup trends","hair trends","skincare trends","celebrity style",
    "influencer fashion","instagram models","tiktok influencers","social media celebrities",
    "online personalities","streamer personalities","content creators","pop culture news",
    "film industry news","box office updates","movie premieres","movie reviews",
    "celebrity interviews","behind the scenes film","actor lifestyle","actress lifestyle",
    "hollywood rumors","film gossip","celebrity breakups","celebrity relationships",
    "celebrity dating","celeb couples","celebrity scandals","red carpet moments",
    "hollywood fashion","fashion critique","runway highlights","model lifestyle",
    "fitness models","fitness influencer trends","influencer fitness","swimsuit influencers",
    "beach photoshoots","travel photography influencers","travel fashion shoots",
    "luxury lifestyle influencers","luxury fashion trends","celebrity lifestyle trends",
    "fashion influencer tips","viral celebrity moments","trending celebrities",
    "upcoming stars hollywood","rising models","rising fashion influencers","instagram stars",
    "social media rising stars","streaming services","netflix celebrity features",
    "hbo celebrity shows","awards shows fashion highlights","celebrity makeup looks",
    "celebrity hair trends","fashion brand collaborations","influencer brand collaborations",
    "digital fashion campaigns","instagram fashion tips","tiktok fashion challenges",
    "viral fashion content","viral entertainment content",
    "editorial photography","high end fashion shoots","luxury brand collaborations",
    "designer campaigns","fashion advertising","celebrity endorsements","product collaborations",
    "influencer marketing fashion","influencer partnerships","beauty collaborations",
    "makeup influencer trends","skincare influencer trends","sports illustrated swimsuit",
    "si swimsuit","miss universe","miss america","miss world","pageant news",
    "kpop demon hunters",
    "teyana taylor red carpet 2026","2016 fashion revival 2026",
    "librarian chic fashion 2026","faux fur trend 2026","bomber jacket comeback 2026",
    "skinny jeans 2026","knee high boots revival 2026",
    "kylie jenner lip kits revival","laufey style 2026","iris law outfits 2026",
    "pinkpantheress fashion 2026","alex consani modeling 2026","lily rose depp looks 2026",
    "gen z celeb outfits 2026","synthetic celebrities ai idols 2026",
    "immersive entertainment trends 2026","k pop comebacks 2026","blackpink tour fashion",
    "bts solo style","newjeans runway looks",
    "instagram modeling reels 2026","youtube fashion vlogs",
    "paris fashion week haute couture 2026","milan fashion week runway 2026",
    "new york fashion week street style","london fashion week editorials",
    "coachella festival outfits 2026","burning man costumes trends",
    "glastonbury festival fashion","disney world new attractions 2026",
    "universal studios new rides","theme park fashion","bali influencer beach shoots",
    "maldives luxury yacht parties","ibiza nightlife bikini scenes",
    "miami beach swimwear parties","celebrity chef michelin dining 2026",
    "viral tiktok food trends","korean beauty glass skin","labubus toy fashion",
    "red carpet minimalism 2026","theatrical red carpet looks",
    "golden globes fashion highlights 2026","grammys red carpet 2026","baftas style moments",
    "oscars 2026","cannes film festival red carpet","venice film festival glamour",
    "art basel miami 2026","whitney biennial fashion","met museum exhibitions style",
    "louvre paris culture trends","tate modern art fashion","guggenheim museum shows",
    "broadway theater playbill","opera news costumes","dance magazine performances",
    "poetry foundation events","interview magazine celebrity shoots","paper magazine parties",
    "another magazine editorials","system magazine high fashion","wwd international coverage",
    "fashionista trend reports","dazed digital street style","i d magazine youth culture",
    "artforum gallery openings","frieze art fair 2026","art in america reviews",
    "bookforum literary gossip","new york review of books culture",
    "paris review fiction fashion","literary hub author style",
    "publishers weekly bestsellers","smithsonian magazine arts",
    "national geographic travel culture","atlantic culture essays","new yorker fashion profiles",
    "financial times arts section","wall street journal culture news",
    "bloomberg arts coverage","vulture pop culture","slate culture reviews",
    "salon culture commentary","the wrap hollywood news","a v club entertainment",
    "consequence of sound music","stereogum album reviews","nme music gossip",
    "spin magazine features","artnet news auctions","vogue business fashion finance",
    "fashion week daily runway","british vogue international","vogue france haute couture",
    "elle international editions","gq international menswear","playbill broadway",
    "broadway world theater","theatermania shows","opera news performances",
    "dance magazine tours","american theatre stage","poetry foundation news","granta magazine",
    "the millions literary","electric literature reads","book riot recommendations",
    "kirkus reviews","library journal","vulture entertainment",
    "cannes film festival official 2026","sundance film festival fashion",
    "toronto international film festival red carpet","venice biennale art fashion",
    "art basel news","met gala","coachella outfits","grammy awards fashion",
    "academy awards coverage","emmy awards red carpet","tony awards style",
    "nobel prize literature","pulitzer prize news","international booker prize",
    "british fashion council news","paris fashion week official 2026",
    "milan fashion week official","new york fashion week official",
    "london fashion week official","museum of modern art news",
    "metropolitan museum of art news","louvre museum news","venice film festival official",
    "berlin international film festival","tribeca film festival official","sxsw film official",
    "frankfurt book fair official","art basel miami beach official","frieze art fair official",
    "armory show official","film quarterly","sight and sound magazine","screen international",
    "variety international","the hollywood reporter international","deadline international",
    "indiewire international","iheartradio music awards 2026",
    "academy of country music awards 2026","grammys 2026","tony awards 2026",
    "emmy awards 2026","pop culture calendar 2026","in out list 2026",
    "washington post in out list","vanity fair cultural calendar",
    "spring pop culture events 2026","summer movies 2026","bad bunny super bowl",
    "kendrick lamar","d4vd music","sage blair story","epstein files","nostalgia loop",
    "emotional reassurance brands","premiumization","information overload","books handbag",
    "substack trend","nerding out","performative intellect","hot take out","wisdom flex",
    "cultural deja vu","frankenstein remake","hamnet waves","wuthering heights remake",
    "odyssey remake","pride prejudice remake","taylor swift","tame impala","mythology core",
    "folklore modern","blue hair revival","charli xcx","awesome con 2026",
    "dc pop culture convention","comics bonanza","breakout searches 2026",
    "kpop demon hunters viral 2026","wisdom flexing culture 2026",
    "remixing classics hollywood 2026","great depression chic fashion 2026",
    "repair aesthetic longevity 2026","grandma hobbies 2026","wellness rooms local 2026",
    "mahjong mania searches 2026","year in search 2026",
    "project hail mary","chuck norris","millennial","collectible","collectibles",
    "banksy","artist banksy","coffee","cacao","coffee prices","coffee beans","rural",
    "world cup","world boxing","photography","pictures","this week in pictures",
    "style","vanity fair","oscars","afterparty","netflix","amazon video","hulu video",
    "paramount+","streaming","streamers","streamer","stream","archeology","social media",
    "social-media","archeological","world tourism","world business","world travel",
    "european travel","world travel","top travel","travel destinations","around the world",
    "meteor","meteorite","asteroid","sake","recycling","recycle","cafe","restaurant",
    "overweight","obese","obesity","microshifting","exercise","tech","tech tips",
    "cancer","shampoo","brain","healthy","health","wealth","wisdom","k pop","k-pop",
    "bts","new study","animals","nature","wildlife","reality star","globe","global",
    "global concert","global concerts",

    "student loans","media bias","trust in media","legacy media","alternative media","citizen journalism",
    "independent reporter","podcast boom","Joe Rogan","Tucker Carlson","newsmax","OAN",
    "Breitbart","daily wire","echo chamber","polarization","culture war","woke agenda",
    "cancel culture","gender ideology","transgender rights","bathroom bill","sports fairness","biological male",
    "puberty blocker","gender affirming care","detransition","book ban","parental rights","CRT in classroom",
    "gender curriculum","sex education","library controversy","child protection","trafficking victim","child sex trafficking",
    "Epstein client list","Lolita Express","Epstein black book","elite pedophile ring","Hollywood scandal","Weinstein conviction",
    "sexual harassment","workplace misconduct","NDA settlement","non disclosure agreement","settlement payout","corporate scandal",
    "Enron collapse","WorldCom fraud","Theranos fraud","Elizabeth Holmes","Sam Bankman-Fried","FTX collapse",
    "NFT boom","NFT bust","gaming industry","esports tournament","streaming platform","Twitch ban",
    "YouTube demonetization","content creator","influencer marketing","brand deal","sponsored post","affiliate link",
    "dropshipping","e-commerce boom","Amazon Prime Day","Black Friday sales","speech code","campus free speech",
    "safe space","trigger warning","microaggression","hate speech definition","content warning","deplatforming",
    "no platform policy","viewpoint discrimination","conservative speaker","event protest","shout down","free speech zone",
    "campus activism","divestment campaign","BDS movement","anti Israel protest","encampment protest","Gaza solidarity",
    "Palestine flag","keffiyeh","intifada chant","from the river to the sea","antisemitism accusation","hate crime report",
    "campus safety","Jewish student","safety walk","bias incident","DEI training","unconscious bias",
    "allyship","privilege checklist","intersectionality","systemic racism","white fragility","antiracism",
    "equity over equality","restorative justice","transformative justice","abolition movement","social media post","Truth Social",
    "X platform","viral moment","trending topic","meme warfare","internet culture","online activism",
    "slacktivism","virtue signaling","performative activism","keyboard warrior","cancel mob","outrage cycle",
    "QAnon","conspiracy forum","alternative theory","fringe narrative","Snopes rating","media matters",
    "partisan outlet","echo chamber reinforcement","confirmation bias","motivated reasoning","cognitive dissonance","belief perseverance",
    "Pulitzer prize","investigative series","bombshell story","breaking scoop","exclusive report",
    # ── Celebrity Names ──
    "Bad Bunny","Cristiano Ronaldo","Drake","Taylor Swift","Lionel Messi","Harry Styles","Lady Gaga",
    "Billie Eilish","Bruno Mars","Justin Bieber","Cardi B","Shakira","Neymar","Nicki Minaj",
    "Ariana Grande","Rihanna","Eminem","Kim Kardashian","Lewis Hamilton","Kanye West","Brad Pitt",
    "Beyonce","Ed Sheeran","Adele","LeBron James","MrBeast","Jake Paul","Leonardo DiCaprio",
    "Adam Sandler","Will Smith","Kendrick Lamar","Snoop Dogg","Travis Scott","The Weeknd",
    "Selena Gomez","Kendall Jenner","Jay Z","Kylie Jenner","Zendaya","Millie Bobby Brown","Dua Lipa",
    "Dolly Parton","Miley Cyrus","Jennifer Lopez","John Cena","Salman Khan","Keanu Reeves","Tom Holland",
    "Post Malone","David Beckham","Scarlett Johansson","Gordon Ramsay","Joe Rogan","Usher",
    "Olivia Rodrigo","Giannis Antetokounmpo","Kevin Durant","Chris Hemsworth","Lil Wayne","Logan Paul",
    "Mark Zuckerberg","Anthony Edwards","Ja Morant","Shaquille O'Neal","Paul McCartney","Nicole Kidman",
    "Emma Watson","Doja Cat","Max Verstappen","Ryan Reynolds","Zac Efron","Zach Bryan","Stephen Curry",
    "Nicolas Cage","Kevin Hart","Jeff Bezos","Jennifer Aniston","George Clooney","Michael B Jordan",
    "Taylor Sheridan","Bronny James","Robert Pattinson","Jennifer Coolidge","Robert De Niro",
    "Mikey Madison","Lewis Pullman","Isabela Merced","Pedro Pascal","Walton Goggins","Timothee Chalamet",
    "Sydney Sweeney","Sabrina Carpenter","Chappell Roan","Tyla","Jacob Elordi","Elle Fanning",
    "Alan Ritchson","Pamela Anderson","Charlie Sheen","Eric Dane","Aubrey Plaza","Florence Pugh",
    "Austin Butler","Margot Robbie","Gal Gadot","Tom Cruise","Emma Stone","Hugh Jackman","Zoe Saldana",
    "Vin Diesel","Jason Statham","Denzel Washington","Samuel L Jackson","Al Pacino","Morgan Freeman",
    "Reese Witherspoon","Sandra Bullock","Julia Roberts","Meryl Streep","Cate Blanchett","Natalie Portman",
    "Anne Hathaway","Jessica Chastain","Viola Davis","Kerry Washington","Halle Berry","Jennifer Lawrence",
    "Emily Blunt","Kate Winslet","Keira Knightley","Charlize Theron","Penelope Cruz","Salma Hayek",
    "Eva Longoria","Sofia Vergara","Shah Rukh Khan","Aamir Khan","Hrithik Roshan","Tiger Woods",
    "Rafael Nadal","Usain Bolt","Michael Phelps","Simone Biles","Naomi Osaka","Virat Kohli",
    "Priyanka Chopra","Deepika Padukone","Roger Federer","Oprah Winfrey","Dwayne Johnson","Johnny Depp",
    "Kylian Mbappe","Serena Williams","Hailee Steinfeld","Josh Allen","Jason Momoa","Doechii",
    "Benson Boone","Charli xcx","Travis Kelce","Caitlin Clark","Angel Reese","Paige Bueckers",
    "Victor Wembanyama","Luka Doncic","Nikola Jokic","Joel Embiid","Karim Benzema","Erling Haaland",
    "Jude Bellingham","Phil Foden","Bukayo Saka","Mohamed Salah","Kevin De Bruyne","Harry Kane",
    "Son Heung-min","Vinicius Junior","Kobe Bryant","Conor McGregor","Floyd Mayweather",
    "Song Ji Woo","Malachi Barton","Milly Alcock","Anna Sawai","Lamine Yamal","Jalen Hurts",
    "Demi Lovato","Kim Taehyung","Jungkook","Jimin","BTS","Blackpink","Jennie","Lisa","NewJeans",
    "Stray Kids","Aespa","ITZY","Twice","Red Velvet","kpop","k-pop comeback",
    # ── Streamers and YouTubers ──
    "Jimmy Donaldson","MrBeast","Felix Kjellberg","PewDiePie","Ryan Kaji","Mark Rober","KSI",
    "IShowSpeed","Kai Cenat","Adin Ross","Darren Watkins","Pokimane","Valkyrae","xQc","Ninja",
    "Tyler Blevins","Pokimane","shroud","Tfue","Dream","GeorgeNotFound","TommyInnit","Thomas Simons",
    "Tubbo","Wilbur Soot","Ranboo","Quackity","Ludwig","MoistCr1TiKaL","Charlie White","penguinz0",
    "CoryxKenshin","David Dobrik","James Charles","Charli D'Amelio","Addison Rae","Dixie D'Amelio",
    "Ajey Nagar","CarryMinati","Ujjwal Chaurasia","Techno Gamerz","Bhuvan Bam","Anastasia Radzinskaya",
    "Like Nastya","Vlad and Niki","Jacksepticeye","Sean McLoughlin","VanossGaming","Evan Fong",
    "SSSniperWolf","DanTDM","Daniel Middleton","PrestonPlayz","Preston Arsement","Jelly","LazarBeam",
    "Muselk","Ali-A","Typical Gamer","FaZe Rug","Brian Awadis","Unspeakable","SSundee","FaZe Clan",
    "100 Thieves","Dude Perfect","Ibai Llanos","AuronPlay","Rubius","Airrack","Nick DiGiovanni",
    "BruceDropEmOff","YourRAGE","Fanum","Duke Dennis","Kai Cenat","Nelk Boys","Yes Theory",
    "PaymoneyWubby","JiDion","FlightReacts","Berleezy","ImDavisss","DDG","streamer",
    # ── World Travel Cities (Culture context) ──
    "Bangkok","Hong Kong","Istanbul","Dubai","Mecca","Antalya","Kuala Lumpur","Singapore","Seoul",
    "Phuket","Cancun","Bali","Denpasar","Jakarta","Manila","Pattaya","Vienna","Prague","Budapest",
    "Munich","Frankfurt","Zurich","Geneva","Stockholm","Copenhagen","Oslo","Helsinki","Athens",
    "Lisbon","Porto","Venice","Florence","Naples","Nice","Marseille","Lyon","Bordeaux","Toulouse",
    "Brussels","Luxembourg","Dublin","Edinburgh","Manchester","Liverpool","Glasgow","Toronto",
    "Vancouver","Montreal","Mexico City","Riviera Maya","Buenos Aires","Rio de Janeiro","Sao Paulo",
    "Santiago","Lima","Bogota","Cartagena","Medellin","Abu Dhabi","Doha","Riyadh","Jeddah",
    "Tel Aviv","Cairo","Marrakesh","Cape Town","Johannesburg","Sydney","Melbourne","Brisbane",
    "Auckland","Wellington","Christchurch","Queenstown","Hiroshima","Nara","Kyoto","Osaka",
    # ── Major Global Events ──
    "FIFA World Cup 2026","World Cup 2026","Commonwealth Games 2026","Asian Games 2026",
    "Coachella 2026","Tomorrowland 2026","Oktoberfest 2026","America 250","Route 66 centennial",
    "Total Solar Eclipse 2026","Tour de France 2026","Kentucky Derby 2026","Cannes 2026",
    "Burning Man 2026","Glastonbury 2026","Lollapalooza 2026","Rio Carnival","Venice Carnival",
    "Songkran 2026","Hajj 2026","Ramadan","Eid al-Fitr","Nowruz","Loy Krathong","Yi Peng lantern",
    "Cherry Blossom Japan","Tulip Festival Netherlands","Semana Santa","Ganesh Chaturthi","Navratri",
    "Notting Hill Carnival","Calgary Stampede","Edinburgh Military Tattoo","Inti Raymi","Pushkar",
    "Jaisalmer Desert Festival","Hornbill Festival","Las Fallas","SXSW 2026","BottleRock",
    "Governors Ball","Welcome to Rockville","Holi festival","Chinese New Year","Mardi Gras",
    "St Patricks Day","Vesak","Ashura","Sundance Film Festival","Stagecoach Festival",
    "Albuquerque Balloon Fiesta","Sturgis Motorcycle Rally","Ultra Music Festival",
    # ── Upcoming / Anticipated Films ──
    "The Odyssey film","Avengers Doomsday","Dune Part Three","Mandalorian and Grogu","Supergirl film",
    "Toy Story 5","The Bride film","Project Hail Mary film","28 Years Later Bone Temple",
    "Wuthering Heights film","Scream 7","Super Mario Galaxy Movie","Michael Jackson biopic",
    "Devil Wears Prada 2","Mortal Kombat II","Masters of the Universe film","Ready or Not 2",
    "Hunger Games Sunrise on the Reaping","Greenland Migration","Scary Movie 2026",
    "People We Meet on Vacation film","Lee Cronin Mummy","Apex film",
    "Disclosure Day film","Flowervale Street film","Hoppers 2026","The Drama film",
    "Moana 2026 film","Animal Friends film","The Moment film",
    "Avengers Doomsday Marvel","Dune Part Three film","The Mummy 2026",
    "28 Years Later 2026","The Odyssey 2026 movie",
    # ── TV Shows & Series ──
    "the pitt season 2","a knight of the seven kingdoms","bridgerton season 4",
    "industry season 4","his and hers hbo","daredevil born again season 2",
    "euphoria season 3","the boys season 5","outlander final season","scarpetta series",
    "beef season 2","lanterns dc","spider-noir","wonder man marvel","star trek starfleet academy",
    "the night manager season 2","the comeback hbo","the testaments hulu","marshals series",
    "rooster series","elle legally blonde prequel","margos got money troubles",
    "kevin animated series","darth maul star wars series","the madison series",
    "dtf st louis show","american classic series","rj decker series",
    "malcolm in the middle revival","king of the hill revival",
    "buffy the vampire slayer reboot","ted lasso season 4","shrinking season 3",
    "black ops series","heated rivalry series","waiting for the out series",
    "can you keep a secret series","falling series","rivals series",
    "it welcome to derry","when life gives you tangerines","mobland series",
    "dexter resurrection","paradise season 2","the hunt season 1",
    "fukushima a nuclear nightmare series","age of attraction series","sunny nights series",
    "on the edge world cup ski racing series","rise of the 49ers","cult of the real housewife",
    "second chance love series","crime in progress series","run away series",
    "mel brooks 99 year old man series","12 12 12 series","the age of innocence series",
    "bait series","big mistakes series","blade runner sequel series",
    "carrie mike flanagan adaptation","crystal lake series","cape fear remake",
    "man on fire remake","the traitors season 4","queer eye final season","yellowjackets final season",
    # ── Books ──
    "a tale of two cities","the little prince","the alchemist","harry potter philosophers stone",
    "and then there were none","dream of the red chamber","the hobbit",
    "alices adventures in wonderland","the da vinci code","the catcher in the rye",
    "sophies world","one hundred years of solitude","anne of green gables","black beauty",
    "the name of the rose","the eagle has landed novel","watership down","charlotte's web",
    "the purpose driven life","the tale of peter rabbit","the very hungry caterpillar",
    "to kill a mockingbird","flowers in the attic","angels and demons","kane and abel",
    "the kite runner","valley of the dolls","how to win friends and influence people",
    "the great gatsby","gone with the wind","rebecca du maurier","the girl with the dragon tattoo",
    "the hunger games","james and the giant peach","ben-hur tale of the christ",
    "who moved my cheese","a brief history of time","the seven habits of highly effective people",
    "totto-chan little girl at the window","the celestine prophecy",
    "the fault in our stars","the girl on the train","the shack novel","the godfather",
    "catching fire","mockingjay","gone girl","things fall apart","wolf totem",
    "jaws novel","adventures of huckleberry finn","pride and prejudice",
    "where the wild things are","the power of positive thinking","the secret book",
    "dune novel","charlie and the chocolate factory","kokoro natsume","where the crawdads sing",
    "follow your heart novel","matilda book","the book thief","the horse whisperer",
    "goodnight moon","the neverending story","all the light we cannot see",
    "fifty shades of grey","the outsiders","shogun novel","the pillars of the earth",
    "perfume novel","the grapes of wrath","the shadow of the wind",
    "interpreter of maladies","becoming michelle obama","the hitchhikers guide to the galaxy",
    "tuesdays with morrie","a wrinkle in time","long walk to freedom mandela",
    "the old man and the sea","the giver","me before you","norwegian wood murakami",
    "the plague camus","no longer human","mans search for meaning","the subtle art of not giving a fuck",
    "the divine comedy","the prophet gibran","the boy in the striped pyjamas","the exorcist",
    "the gruffalo","the help novel","catch-22","the stranger camus","the lovely bones",
    "wild swans","santa evita","night wiesel","life of pi","fahrenheit 451",
    "angelas ashes","the story of my experiments with truth","bridget jones diary",
    "it ends with us","half his age book","the future saints","the seven daughters of dupree",
    "whistler book","where the wildflowers grow","land book","vigil book",
    "the missed connection","the caretaker book","exit party book","the astral library",
    "dear debbie","my husbands wife","anatomy of an alibi","rites of the starling",
    "our perfect storm book","theres only one sin in hollywood",
    "the midnight train book","a parade of horribles","dogs boys other things ive cried about",
    "beginning middle end book","john of john","the hybrid prince","judge stone book",
    "the storm book","in your dreams book","what we did to survive","the trip book",
    "war and peace","the diary of anne frank","the thorn birds",
    # ── Hollywood Awards & Industry Events ──
    "2026 primetime emmy awards","met gala 2026","cannes film festival 2026",
    "toronto international film festival 2026","venice film festival 2026",
    "bafta television awards 2026","iheartradio music awards 2026",
    "mtv video music awards 2026","tony awards 2026","golden globes 2027",
    "academy awards 2027","sag awards 2027","critics choice awards 2027",
    "grammy awards 2027","comic-con international san diego 2026",
    "sundance film festival 2027","palm springs international film festival 2027",
    "boulder international film festival 2026","directors guild of america awards 2027",
    "writers guild of america awards 2027","producers guild of america awards 2027",
    "satellite awards 2026","anime awards 2026","voice arts awards 2026",
    "cas awards 2026","brit awards 2026","aacta awards 2026",
    "super bowl halftime show 2027","bafta film awards 2027",
    "miami film festival 2026","ann arbor film festival experimental",
    "pittsburgh film office lights glamour action gala",
    # ── Global Festivals & Cultural Events (evergreen + dated) ──
    "rio carnival","oktoberfest","chinese new year","diwali","holi festival",
    "mardi gras new orleans","songkran festival","coachella music festival",
    "glastonbury festival","burning man","tomorrowland","la tomatina",
    "san fermin running of the bulls","venice carnival","dia de los muertos",
    "christmas celebrations","new years eve celebration","easter celebrations","thanksgiving",
    "sxsw festival","ultra music festival","lollapalooza","rock in rio",
    "sziget festival","exit festival belgrade","edinburgh military tattoo",
    "macys thanksgiving day parade","yi peng lantern festival",
    "cherry blossom hanami japan","tulip festival netherlands",
    "notting hill carnival","love parade","bonfire night uk","european christmas markets",
    "albuquerque international balloon fiesta","sturgis motorcycle rally",
    "carnival salvador","carnival barranquilla","trinidad carnival","junkanoo bahamas",
    "cuban carnival","las fallas valencia","basel carnival","up helly aa shetland",
    "white nights festival st petersburg","calgary stampede","pushkar camel fair",
    "jaisalmer desert festival","hornbill festival india","inti raymi festival peru",
    "timkat festival ethiopia","la patum berga","loy krathong festival",
    "chinese lantern festival","mid-autumn festival","qingming festival",
    "dragon boat festival","obon festival japan","chuseok korea",
    "semana santa seville","ganesh chaturthi","navratri festival","onam festival",
    "pongal festival","guy fawkes night","bastille day","boryeong mud festival",
    "corpus christi procession","st patricks day",
    "new orleans jazz heritage festival","stagecoach country music festival",
    "bottlerock napa valley","governors ball music festival","welcome to rockville",
    "bad bunny debi tirar mas fotos world tour 2026",
    "ariana grande eternal sunshine tour 2026","lewis capaldi tour 2026",
    "tomorrowland thailand 2026","america 250th anniversary celebrations 2026",
    "route 66 centennial 2026","total solar eclipse europe 2026","paris fashion week 2026",
    "coachella music festival 2026","glastonbury festival 2026","burning man 2026",
    "lollapalooza 2026","oktoberfest munich 2026","diwali 2026","rio carnival 2027",
    "venice carnival 2027","songkran festival 2027","holi festival 2027",
    "chinese new year 2027","mardi gras new orleans 2027","stagecoach festival 2026",
    "bottlerock napa valley 2026","governors ball music festival 2026",
    "welcome to rockville 2026","ultra music festival 2027","sxsw festival 2027",
    "independence day mexico","el grito mexico","lantern festival taiwan",
    "canada day celebration","australia day","waitangi day new zealand",
    "independence day usa","nowruz persian new year",
    # ── Near-Term March & April 2026 Culture Events ──
    "coachella valley music arts festival weekend one april 2026",
    "coachella valley music arts festival weekend two april 2026",
    "easter sunday global celebrations april 2026","good friday observances april 2026",
    "passover seders april 2026","new orleans jazz heritage festival april 2026",
    "stagecoach country music festival april 2026",
    "boots in the park gilbert march 2026","beyond wonderland socal march 2026",
    "savannah music festival march 2026","hells heroes festival houston march 2026",
    "okeechobee music arts festival march 2026","rendezvous music festival jackson hole 2026",
    "cape town international jazz festival march 2026","milan design week april 2026",
    "cherry blossom hanami tokyo april 2026","cherry blossom hanami kyoto april 2026",
    "cherry blossom hanami osaka april 2026","earth day global events april 2026",
    "vaisakhi celebrations april 2026","boots in the park bakersfield april 2026",
    "boots in the park fresno april 2026","holo holo avila beach april 2026",
    "jam in the streets athens march 2026","sxsw aftermath mixers march 2026",
    "elton john aids foundation events 2026","milan fashion design pop-ups april 2026",
    "easter parades worldwide april 2026","stagecoach after-parties april 2026",
    "coachella surprise sets parties april 2026",
    "beyond wonderland rave stages march 2026",
    "cape town jazz main stage march 2026","okeechobee art installations march 2026",
    "dyngus day celebrations april 2026","national walking day april 2026",
    "vaisakhi parades temple celebrations april 2026",
    "japanese hanami picnic events festivals april 2026",

    "Mia Khalifa","Charlie Kirk","Novak Djokovic","Michael Jordan","Bill Gates","Sean Combs",
    "MrBeast","Victoria Beckham","ASAP Rocky","Stefon Diggs","Sophie Rain","James Harden",
    "YoungBoy","Ozzy Osbourne","Paul George","David Corenswet","Justin Baldoni","Emma Myers",
    "Justin Jefferson","Barack Obama","Joe Biden","Vladimir Putin","Narendra Modi",
    "Angelina Jolie","Tom Hanks","Robert Downey Jr","Chris Evans","Mark Ruffalo","Jackie Chan",
    "Jeffree Star","Nikita Dragun","Travis Barker","Kourtney Kardashian","Khloe Kardashian",
    "Kris Jenner","Caitlyn Jenner","Odessa A'Zion","Alex Warren","Gracie Abrams","Tate McRae",
    "Conan Gray","J-Hope","V BTS","Mike Tyson","Rodrygo","Robert Lewandowski","Eden Hazard",
    "Paul Pogba","Antoine Griezmann","Joshua Kimmich","Toni Kroos","Manuel Neuer","Pedri","Gavi",
    "Florian Wirtz","Jamal Musiala","Cole Palmer","Declan Rice","Trent Alexander-Arnold",
    "Marcus Rashford","Bruno Fernandes","Lachlan Ross Power","Flauhjae Johnson",
    # ── Missing YouTubers Batch 2 ──
    "Amit Bhadana","Vladimir Vashketov","Nikita Vashketov","Alan Stokes","Alex Stokes",
    "VanossGaming","Evan Fong","SSSniperWolf","Lia Wolf","Jelle van Vucht","PaymoneyWubby",
    "JiDion","Imane Anys","Rachell Hofstetter","Felix Lengyel","Michael Grzesiek",
    "Turner Tenney","Toby Smith","William Gold","Philza","Phil Watson","Ludwig Ahgren",
    "Cory Williams","Dashie","Sean McLaughlin",
    # ── Missing World Travel Cities ──
    "Madrid","Amsterdam","Barcelona","Guangzhou","Shenzhen","Palermo",
    # ── WNBA & Women's Sports Stars ──
    "Sabrina Ionescu","A'ja Wilson","Brittney Griner","Sue Bird","Diana Taurasi",
    "Candace Parker","Maya Moore","Sheryl Swoopes","Lisa Leslie","Chamique Holdsclaw",
    "Tamika Catchings","Elena Delle Donne","Breanna Stewart","Napheesa Collier",
    "Aliyah Boston","Cameron Brink","JuJu Watkins","Flauhjae Johnson",
    # ── UK YouTubers / Sidemen ──
    "Miniminter","Simon Minter","Vikkstar123","Vikram Barn","Zerkaa","Josh Bradley",
    "TBJZL","Tobi Brown","Behzinga","Callux","Harry Lewis","Sidemen",
    # ── Spanish / Latin YouTubers ──
    "Mikecrack","ElMariana","Rubius","AuronPlay","Vegetta777","Willyrex",
    "Ibai Llanos","TheGrefg","Jordi Wild",
    # ── Rising Stars / Actors ──
    "Aimee Lou Wood","Matthew Goode","Hero Fiennes Tiffin","Jessie Buckley","Emily Rudd",
    "Owen Cooper","Theodor Pellerin","Hailey Gates","Havana Rose Liu","Marissa Bode",
    # ── Latin Music Artists & Tours ──
    "Karol G","Anitta","Maluma","J Balvin","Daddy Yankee","Ozuna","Becky G","Peso Pluma",
    "Ariana Grande Eternal Sunshine Tour","Lewis Capaldi Tour 2026","DeBi Tirar Mas Fotos Tour",
    "Bad Bunny World Tour 2026","Ariana Grande tour","Eternal Sunshine concert",
    # ── Additional Films ──
    "Disclosure Day film","Flowervale Street film","Hoppers 2026","The Drama 2026",
    "Moana 2026 film","Animal Friends film","Apex 2026 film",
    "28 Years Later 2026","The Odyssey 2026 movie","Ready or Not 2 film",
    # ── Additional Events ──
    "America 250th Anniversary","Route 66 Centennial 2026","Total Solar Eclipse Europe 2026",
    "Masters Tournament 2026","Wimbledon 2026 tennis","Diwali 2026","Lollapalooza 2026",
    "Ultra Music Festival 2026","Stagecoach 2026","BottleRock 2026","Sundance 2027",
    "Commonwealth Games Glasgow 2026","Asian Games Japan 2026",
]
CULTURE_KEYWORDS = set(kw.lower() for kw in RAW_CULTURE_KEYWORDS)

RAW_WORLD_KEYWORDS = [
    # Europe broad
    "europe","european union","eu","eurozone","european parliament","european commission",
    "european council","nato","schengen","brexit","uk politics","united kingdom",
    "england","scotland","wales","northern ireland","ireland","france","germany",
    "italy","spain","portugal","netherlands","belgium","austria","switzerland",
    "sweden","norway","denmark","finland","poland","czech republic","hungary",
    "romania","bulgaria","greece","croatia","serbia","ukraine","russia",
    "macron","scholz","meloni","sanchez","sunak","starmer","tusk","orban",
    "eu summit","eu elections","eu budget","eu sanctions","eu migration",
    "eu climate","eu energy","eu trade","eu economy","eu enlargement",
    "european central bank","ecb","euro currency","eurozone inflation",
    "eu russia sanctions","ukraine war","ukraine russia","kyiv","zelenskyy",
    "putin russia","moscow","kremlin","nato expansion","nato summit",
    "european heatwave","europe flooding","europe wildfires","europe drought",
    # Asia broad
    "asia","southeast asia","east asia","south asia","central asia","pacific asia",
    "asean","apec","asia pacific","indo pacific","quad alliance",
    "china","chinese","beijing","shanghai","hong kong","taiwan","taipei",
    "taiwan strait","south china sea","xi jinping","cpc","communist party china",
    "japan","japanese","tokyo","osaka","kyoto","hiroshima","nagasaki",
    "fumio kishida","shigeru ishiba","bank of japan","yen","nikkei",
    "south korea","korean","seoul","busan","yoon suk yeol","korea peninsula",
    "north korea","pyongyang","kim jong un","dprk","korea nuclear",
    "india","indian","new delhi","mumbai","modi","bjp","congress party india",
    "pakistan","islamabad","pakistan army","imran khan",
    "bangladesh","dhaka","myanmar","yangon","junta myanmar",
    "thailand","bangkok","phuket","chiang mai","thai government","thai politics",
    "vietnam","hanoi","ho chi minh","vietnam economy","vietnam manufacturing",
    "indonesia","jakarta","bali","jokowi","prabowo","indonesia election",
    "malaysia","kuala lumpur","anwar ibrahim","malaysia economy",
    "singapore","singapore economy","singapore tech","lee hsien loong",
    "philippines","manila","marcos","philippine sea","south china sea dispute",
    "cambodia","phnom penh","laos","vientiane","brunei",
    "sri lanka","colombo","nepal","kathmandu","bhutan",
    "australia","sydney","canberra","albanese","australia china",
    "new zealand","wellington","auckland","ardern","luxon",
    # Global / World
    "global economy","world economy","imf","world bank","g7","g20",
    "wto","trade war","global trade","supply chain","semiconductor",
    "global inflation","global recession","global markets","foreign exchange",
    "united nations","un security council","un general assembly","un resolution",
    "international court","icc","international law","global diplomacy",
    "climate change global","cop30","paris agreement","global warming",
    "global health","who","pandemic","disease outbreak",
    "international relations","geopolitics","foreign policy global",
    "global migration","refugee crisis","human rights global",
    "global technology","ai global","semiconductor global","tech rivalry",
    "global energy","lng","natural gas","oil global","opec global",
    "space exploration","nasa","spacex global","esa","jaxa",
    # Search terms from attached document
    "reuters europe news","associated press asia","agence france-presse europe",
    "bbc europe news","financial times europe","le monde international",
    "der spiegel","el pais europe","the guardian asia","nikkei asia review",
    "japan times news","asahi shimbun english","nhk world japan","kyodo news english",
    "bangkok post thailand","straits times singapore","south china morning post",
    "korea herald news","hindustan times asia","euronews europe","france 24 asia",
    "deutsche welle asia","politico europe","the local europe","irish times",
    "nikkei japan economy 2026","japan times tokyo 2026","bangkok post tourism 2026",
    "straits times singapore tech 2026","europe eu election 2026",
    "asia china india relations 2026","japan yen currency 2026",
    "thailand tourism boom 2026","europe heatwave summer 2026",
    "japan cherry blossom forecast 2026","thailand songkran festival 2026",
    "europe ukraine update 2026","asia semiconductor supply 2026",
    "japan osaka expo 2026","europe germany election 2026",
    "asia kpop global tour 2026","japan mount fuji climbing 2026",
    "europe paris olympics legacy 2026","asia taiwan strait tensions 2026",
    "europe italy venice flooding 2026","asia indonesia bali volcano 2026",
    "japan hokkaido ski 2026","europe uk starmer government 2026",
    "asia philippines south china sea 2026","japan nagoya tech hub 2026",
    "europe spain election 2026","asia malaysia economy 2026",
    "europe netherlands climate 2026","asia cambodia angkor wat 2026",
    "japan sapporo snow festival 2026","europe sweden nato 2026",
    "asia laos mekong river 2026","europe portugal wildfires 2026",
    "asia myanmar border 2026","europe poland ukraine border 2026",
    "asia singapore formula one 2026","europe denmark green energy 2026",
    "europe finland arctic 2026","japan wakayama temples 2026",
    "nikkei japan stock market 2026","europe brexit impact 2026",
    "asia south korea k drama 2026","asia vietnam manufacturing 2026",
    "europe france macron news 2026","japan fukuoka food 2026",
    "japan kyoto temple tourism 2026","thailand chiang mai digital nomad 2026",
    "amphibious","assault ship","nato allies","strait of hormuz","missile sites",
    "missile threat","war rages","drone","drones","oil","inflation","energy price",
    "stocks","oil fields","military operations","crude","crude oil","crude exports",
    "tanker","scarcity","rifle","rare earth","spain","spanish","vaccine",
    "ground troops","king charles","caribbean","norway","crown princess","crown",
    "epstein","jeffrey epstein","energy shock","gas-dependent","security concerns",
    "world cup","taiwan","taiwan's","bts","world tourism","world business",
    "world travel","france","french","macron","europe","european travel","flooding",
    "around the world","sake","overweight","obese","obesity","fukushima",
    "fukushima reactor","nuclear","nuclear energy","rhinos","uganda","ukraine",
    "russia","top leaders","energy fallout","humanitarian","humanitarian aid",
    "russian tanker","czech","vatican","mining industries","mining","faslane",
    "nuclear submarine",

    "G7 meeting","Indo-Pacific strategy","AUKUS pact","freedom of navigation","pandemic treaty","WHO authority",
    "Russia Ukraine","Putin invasion","Nord Stream","European gas crisis","island chain","first island chain",
    "second island chain","Taiwan invasion scenario","amphibious assault","beachhead","color revolution","Arab Spring",
    "Maidan revolution","hybrid warfare","information operations","gray zone","salami slicing","fait accompli",
    "escalation ladder","deterrence failure","miscalculation risk","Taiwan flashpoint","Korea flashpoint","Malacca Strait",
    "energy chokepoint","global trade route","maritime domain awareness","freedom of navigation operation","FONOP","carrier transit",
    "destroyer passage","littoral combat ship","stealth technology","railgun test","laser weapon","directed energy",
    "hypersonic program","conventional prompt strike","scramjet engine","boost glide","boost phase intercept","space based sensor",
    "kill chain","sensor to shooter","JADC2","multi domain operation","MDO","great power competition",
    "near peer adversary","pacing threat","China pacing threat","Russia acute threat","North Korea rogue state","proliferation risk",
    "nuclear breakout","ICBM range","submarine launched ballistic missile","SLBM","Ohio class","Columbia class",
    "Virginia class","attack submarine","fast attack","under ice capability","Arctic strategy","polar security",
    "icebreaker fleet","heavy icebreaker","polar security cutter","coast guard expansion","Arctic presence","rare earth dominance",
    "mineral security","critical mineral stockpile","supply chain vulnerability","IPEF framework","Indo Pacific economic framework","geopolitical competition",
    "soft power","hard power","smart power","diplomatic corps","foreign service","ambassador post",
    "embassy security","state department cable","diplomatic pouch","back channel","track two diplomacy","shuttle diplomacy",
    "Camp David accord","Oslo accord","Abraham Accords","normalization deal","two state framework","frozen conflict",
    "occupied territory","annexation claim","self determination","separatist movement","Donbas conflict","Luhansk",
    "Donetsk","Crimea annexation","Black Sea fleet","Sevastopol","food security","global hunger",
    "atrocity prevention","responsibility to protect","UN peacekeeping","blue helmet","peacekeeping mission","peace enforcement",
    "peace building","stabilization operation","counterinsurgency doctrine","population centric","hearts and minds","influence campaign",
    "narrative dominance","strategic communication","public diplomacy","cultural diplomacy","Fulbright","Peace Corps",
    "USAID project","development assistance","foreign aid budget","transparency international","corruption perception index","kleptocracy",
    "oligarch sanction","asset freeze","yacht seizure","London laundromat","golden visa","citizenship by investment",
    "passport sale","tax haven","offshore account","Panama Papers","Paradise Papers","Pandora Papers",
    "ICIJ","international consortium","cross border reporting",
    # ── World Travel Cities ──
    "Bangkok","Phuket","Pattaya","Chiang Mai","Bali","Denpasar","Jakarta","Manila","Ho Chi Minh City",
    "Hanoi","Kuala Lumpur","Singapore","Seoul","Taipei","Osaka","Kyoto","Hong Kong","Macao","Istanbul",
    "Vienna","Prague","Budapest","Berlin","Munich","Frankfurt","Zurich","Geneva","Stockholm","Copenhagen",
    "Oslo","Helsinki","Athens","Lisbon","Porto","Venice","Florence","Naples","Nice","Marseille","Lyon",
    "Bordeaux","Toulouse","Brussels","Luxembourg","Dublin","Edinburgh","Manchester","Liverpool","Glasgow",
    "Toronto","Vancouver","Montreal","Buenos Aires","Rio de Janeiro","Sao Paulo","Santiago","Lima",
    "Bogota","Cartagena","Medellin","Cape Town","Johannesburg","Sydney","Melbourne","Brisbane","Auckland",
    "Wellington","Christchurch","Queenstown","Hiroshima","Nara","Antalya",
    # ── Major International Events ──
    "FIFA World Cup 2026","Commonwealth Games 2026","Asian Games 2026","Tour de France 2026",
    "Wimbledon 2026","Cannes Film Festival 2026","Oktoberfest 2026","Songkran 2026","Hajj 2026",
    "Cherry Blossom Japan","Yi Peng lantern festival","Loy Krathong","Nowruz","Vesak","Ashura",
    "Rio Carnival","Venice Carnival","Glastonbury 2026","Edinburgh Military Tattoo",
    # ── International Events Added 2026 ──
    "2026 winter olympics milano cortina","2026 commonwealth games glasgow",
    "2026 asian games aichi nagoya","2027 mens rugby world cup australia",
    "2027 ryder cup adare manor ireland","2027 world athletics championships beijing",
    "total solar eclipse europe 2026","great wildebeest migration",
    "timkat festival ethiopia","inti raymi festival peru","up helly aa shetland",
    "songkran festival 2027","loy krathong festival 2026","yi peng lantern festival 2026",
    "cherry blossom hanami japan 2027","obon festival japan 2026","chuseok korea 2026",
    "mid-autumn festival 2026","dragon boat festival 2026","chinese new year 2027",
    "lantern festival taiwan 2027","nowruz persian new year 2027",
    "carnival barranquilla 2027","carnival salvador 2027","trinidad carnival 2027",
    "junkanoo bahamas 2027","las fallas valencia 2027","semana santa seville 2027",
    "tulip festival netherlands 2026","european christmas markets 2026",
    "hornbill festival india 2026","pushkar camel fair 2026",
    "jaisalmer desert festival 2026","white nights festival st petersburg 2026",
    "boryeong mud festival 2026","basel carnival 2027","love parade berlin 2026",
    "corpus christi procession 2026","la patum berga 2027",
    "independence day mexico 2026","el grito mexico 2026",
    "canada day 2026","australia day 2027","waitangi day",
    "bastille day 2026","guy fawkes night 2026",
    "hajj pilgrimage 2026","ramadan 2027","eid al-fitr 2027","eid al-adha",
    "yom kippur 2026","hanukkah 2026","vesak buddha day 2026","ashura 2026",
    "muharram processions","camino de santiago pilgrimage","kumbh mela",
    "formula 1 japanese grand prix suzuka 2026","cape town international jazz festival",
    "savannah music festival","hell's heroes festival houston",
]
WORLD_KEYWORDS = set(kw.lower() for kw in RAW_WORLD_KEYWORDS)

RAW_BUSINESS_KEYWORDS = [
    # ── Core business / markets ──
    "stock market","stock markets","wall street","dow jones","s&p 500","nasdaq","nyse",
    "stock price","share price","market cap","market capitalization","bull market","bear market",
    "market rally","market selloff","market crash","earnings report","quarterly earnings",
    "revenue growth","profit margin","operating income","net income","eps","earnings per share",
    "forward guidance","analyst forecast","wall street analyst","price target","buy rating",
    "sell rating","hold rating","upgrade downgrade","ipo","initial public offering","spac",
    "merger","acquisition","m&a","hostile takeover","buyout","leveraged buyout","lbo",
    "private equity","venture capital","startup funding","series a","series b","series c",
    "unicorn startup","decacorn","pre ipo","going public","delisting","stock buyback",
    "share repurchase","dividend","dividend yield","dividend cut","special dividend",
    "stock split","reverse stock split","index fund","etf","mutual fund","hedge fund",
    "activist investor","short seller","short selling","short squeeze","options trading",
    "call option","put option","derivatives","futures contract","commodities market",
    "gold price","silver price","copper price","oil price","natural gas price",
    "commodity prices","inflation data","cpi report","ppi report","fed minutes",
    "federal reserve rate","interest rate decision","rate hike","rate cut","monetary policy",
    "quantitative easing","quantitative tightening","treasury yield","bond market",
    "credit market","junk bond","investment grade","credit rating","moody s","s&p rating",
    "fitch rating","yield curve","inverted yield","debt market","sovereign debt",
    # ── Company / corporate ──
    "corporate earnings","ceo","chief executive","cfo","chief financial officer",
    "board of directors","shareholder meeting","annual report","sec filing","10-k","10-q","8-k",
    "proxy statement","corporate governance","executive compensation","layoffs","job cuts",
    "workforce reduction","restructuring","cost cutting","expense reduction","profit warning",
    "earnings miss","earnings beat","revenue miss","revenue beat","guidance raised","guidance cut",
    "corporate strategy","business strategy","market share","competitive advantage",
    "supply chain","logistics","manufacturing output","factory orders","industrial production",
    "retail sales","consumer spending","e-commerce","online retail","amazon","walmart","target",
    "home depot","costco","apple earnings","microsoft earnings","google earnings","alphabet",
    "meta earnings","tesla earnings","nvidia earnings","amazon earnings","netflix earnings",
    "banking earnings","jpmorgan","goldman sachs","morgan stanley","bank of america","citigroup",
    "wells fargo","blackrock","vanguard","fidelity","berkshire hathaway","warren buffett",
    "charlie munger","cathie wood","ark invest","bill ackman","carl icahn",
    # ── Economy macro ──
    "gdp growth","gdp report","economic growth","recession","economic recession",
    "soft landing","hard landing","stagflation","economic contraction","economic expansion",
    "consumer confidence","business confidence","pmi","purchasing managers index",
    "manufacturing pmi","services pmi","job openings","jolts report","nonfarm payrolls",
    "unemployment claims","jobless claims","labor market report","wage growth","average earnings",
    "productivity report","trade deficit","trade surplus","current account","trade balance",
    "import prices","export prices","tariff impact","trade war impact","dollar index",
    "currency markets","forex","euro dollar","dollar yen","dollar yuan","pound dollar",
    "emerging market","developing economy","imf forecast","world bank forecast",
    "oecd forecast","global growth","global recession","global economy outlook",
    # ── Finance / banking / fintech ──
    "banking sector","bank failure","bank collapse","fdic","bank regulation",
    "financial regulation","dodd frank","basel iii","capital requirements","stress test",
    "credit card","consumer debt","household debt","corporate debt","national debt",
    "deficit spending","fiscal policy","government spending","budget deficit",
    "mortgage rate","refinancing","housing market","home prices","real estate market",
    "commercial real estate","office vacancy","retail vacancy","reit",
    "fintech","digital banking","neobank","payment processing","credit card fees",
    "buy now pay later","bnpl","payday loan","auto loan","student loan refinancing",
    "personal finance","financial planning","retirement savings","401k","ira",
    "wealth management","financial advisor","robo advisor","asset management",
    "portfolio management","risk management","insurance market","reinsurance",
    "insurtech","healthtech finance","payroll","accounts payable","accounts receivable",
    "small business loan","sba loan","microloan","crowdfunding","kickstarter","indiegogo",
    "angel investor","seed funding","seed round","startup ecosystem","silicon valley funding",
    # ── Crypto / digital assets ──
    "bitcoin price","bitcoin etf","crypto market","cryptocurrency","ethereum","altcoin",
    "defi","nft market","stablecoin","cbdc","digital dollar","crypto regulation",
    "sec crypto","cftc crypto","coinbase","binance","crypto exchange","blockchain business",
    "crypto crash","crypto rally","bitcoin halving","crypto adoption","institutional crypto",
    "crypto fund","grayscale","blackrock bitcoin","bitcoin spot etf","crypto winter",
    "web3 business","tokenization","rwa tokenization","digital asset management",
    # ── Real estate / housing ──
    "housing affordability","home sales","existing home sales","new home sales",
    "housing starts","building permits","zillow","redfin","opendoor","real estate broker",
    "commercial property","office market","industrial real estate","multifamily",
    "apartment rents","rental market","landlord","tenant market","foreclosure rate",
    "mortgage delinquency","housing inventory","home builder","dr horton","lennar",
    # ── Entrepreneurship / small biz ──
    "small business","entrepreneurship","startup news","business launch","business failure",
    "franchise","franchising","business model","pivot","product market fit","growth hacking",
    "revenue model","subscription model","saas business","b2b","b2c","direct to consumer",
    "dtc","e-commerce growth","shopify","woocommerce","dropshipping business",
    "amazon fba","marketplace business","gig economy business","side hustle","freelance economy",
    # ── Specific business SEO from source list ──
    "bloomberg business","reuters finance","wsj markets","ft markets","economist business",
    "cnbc markets","forbes business","business insider","fortune 500","marketwatch",
    "yahoo finance","investopedia","morningstar","barrons","harvard business review",
    "hbr","entrepreneur magazine","inc magazine","fast company","kiplinger","nerdwallet",
    "bankrate","coindesk","theblock","decrypt crypto","housingwire","seeking alpha",
    "tradingview","zacks investment","money magazine","us news money","thestreet",
    "investing.com","consumer reports","investment news","financial planning magazine",
    "bisnow","inman real estate","globest","finviz","bplans","startups.com","score business",
    "bitcoin magazine","beincrypto","cointelegraph","ledger insights","blockworks",
    "bankless","cryptoslate","real vision","kiva loans","prosper marketplace",
    # ── Additional business keywords from SEO list ──
    "excessive force finding","systemic issue","training reform","broken windows theory",
    "zero tolerance","stop and frisk","qualified immunity doctrine","excessive force standard",
    "graham v connor","objective reasonableness","clearly established law","circuit split",
    "stare decisis","carried interest","hedge fund tax","private equity fund",
    "real estate tax break","1031 exchange","opportunity zone","tax shelter",
    "offshore haven","inversion deal","corporate relocation","tax competitiveness",
    "global minimum tax","pillar two","beps framework","oecd agreement","digital services tax",
    "gafa tax","tech giant tax","antitrust lawsuit business","google breakup","amazon antitrust",
    "app store fees","epic vs apple","sec lawsuit","ripple case","xrp ruling",
    "stablecoin regulation","silicon valley bank","svb collapse","flash crash",
    "trading halt","volatility spike","vix index","treasury yield curve","inverted yield curve",
    "recession indicator","stagflation risk","bank secrecy act","beneficial ownership",
    "corporate transparency act","fincen rule","crypto mixer","suspicious activity report",
    "sar filing","aml","kyc","money transmitter","fintech regulation",
    "robo advisor","fiduciary duty","best interest standard","dol rule","retirement advice",
    "401k fee","target date fund","lifecycle fund","asset allocation","risk tolerance",
    "portfolio diversification","tax loss harvesting","capital gain","wash sale rule",
    "municipal bond","roth ira","traditional ira","backdoor roth","solo 401k","sep ira",
    "financial independence","fire movement","retire early","savings rate","4 percent rule",
    "safe withdrawal rate","sequence of return risk","longevity risk","healthcare cost business",
    "long term care insurance","annuity","pension plan","defined benefit","defined contribution",
    "401k match","employer contribution","vesting schedule","rollover ira","hardship withdrawal",
    "financial literacy","budgeting","emergency fund","sinking fund","debt snowball",
    "debt avalanche","credit score","fico score","credit utilization","payment history",
    "bankruptcy","chapter 7","chapter 13","foreclosure","loan modification","forbearance",
    "student loan refinance","income driven repayment","income share agreement","isa education",
    "college roi","earnings premium","college wage premium","underemployment",
    "degree inflation","credential inflation","human capital","fintech innovation business",
    "digital wallet business","apple pay business","google pay business","contactless payment",
    "qr code payment","cryptocurrency payment","bitcoin acceptance","lightning network",
    "layer 2 crypto","scalability crypto","energy consumption crypto","proof of stake",
    "ethereum merge","carbon footprint crypto","nft marketplace","opensea","nft floor price",
    "crypto custody","cold storage","hardware wallet","seed phrase","crypto scam","rug pull",
    "exchange hack","mt gox","coincheck","bitfinex","binance hack","insurance fund",
    "proof of reserves","merkle tree","audit report","regulatory compliance crypto",
    "know your customer","anti money laundering","travel rule","fatf guidance",
    "virtual asset","vasp","money transmitter license","occ crypto","sabre charter",
    "custody bank","fidelity digital assets","coinbase custody","gemini trust",
    "cftc jurisdiction","sec security","howey test","investment contract","utility token",
    "security token","sto platform","tokenized asset","real world asset","rwa",
    "on chain lending","defi protocol","aave","compound","uniswap","decentralized exchange",
    "dex","amm","automated market maker","liquidity pool","impermanent loss","yield farming",
    "staking reward","governance token","dao","snapshot vote","quadratic voting",
    "token weighted","sybil attack","decentralized identity","web3 wallet","metamask",
    "mev","sandwich attack","frontrunning","arbitrage bot","liquidation bot","oracle manipulation",
    "price impact","slippage","mempool","flashbots","builder market","pbs",
    "restaking","eigenlayer","liquid restaking","airdrop farming","retroactive airdrop",
    "wallet clustering","multi wallet","farming strategy","cross chain yield","bridge exploit",
    "token sniffer","honeypot detector","contract verifier","etherscan","bscscan","gas fee",
    "rollup","optimistic rollup","zk rollup","polygon","arbitrum","optimism","base chain",
    "cosmos ecosystem","ibc protocol","atom token","validator set","slashing",
    "unbonding period","liquid staking","lido","staked eth","rocket pool","home staking",
    "node operator","execution client","consensus client","mev boost",
    "account abstraction","erc 4337","paymaster","bundler","entry point contract",
    "wallet as service","gas sponsorship","gasless transaction","relayer","biconomy",
    "smart account","session key","passkey","webauthn","passwordless","mpc wallet",
    "multi party computation","social login","email wallet","wallet connect","hardware wallet ledger",
    "trezor","coldcard","air gapped","shamir secret sharing","multi sig wallet","gnosis safe",
    "multisignature","social recovery","seed backup","metal seed",
    "not your keys","exchange risk","custodial risk","bankruptcy risk","ftx collapse",
    "proof of reserve audit","merkle proof","solvency proof","chain analysis",
    "bitcoin etf inflow","institutional custody","blackrock ibit","fidelity fbtc",
    "grayscale gbtc","etf volume","creation redemption","authorized participant",
    "liquidity provider","bid ask spread","24/7 trading","weekend trading",
    "global market hours","volatility hour","macro event","fed meeting","powell speech",
    "dot plot","economic projection","rate path","terminal rate","neutral rate",
    "r star","taylor rule","monetary policy rule","forward guidance","data dependent",
    "hawkish","dovish","pivot expectation","soft pivot","cut cycle","hiking cycle",
    "pause period","balance sheet reduction","qt pace","treasury runoff","mbs runoff",
    "mortgage backed security","agency mbs","fed holdings","reverse repo","rrp facility",
    "money market fund","treasury bill","short term debt","extraordinary measure",
    "x date","cash balance","tga balance","treasury general account","tax receipt",
    "spending outflow","reconciliation package","omnibus bill","fiscal space",
    "primary deficit","primary surplus","structural deficit","cyclical adjustment",
    "potential gdp","output gap","phillips curve","nairu","natural rate unemployment",
    "beveridge curve","job opening","quit rate","layoff rate","hiring rate",
    "labor force participation","prime age participation","employment population ratio",
    "wage pressure","average hourly earnings","eci index","compensation cost",
    "productivity growth","unit labor cost","profit margin business","corporate profit",
    "shiller pe","cape ratio","valuation metric","mean reversion","bubble risk",
    "fear greed index","aaii sentiment","investor sentiment","put call ratio",
    "vix term structure","contango","backwardation","volatility smile","skew index",
    "tail risk","black swan","fat tail","tail hedge","option strategy","protective put",
    "collar strategy","covered call","wheel strategy","income generation","dividend capture",
    "ex dividend date","dividend aristocrat","dividend king","payout ratio","dividend growth",
    "yield on cost","total return","compounding","reinvestment","drip plan",
    "dollar cost averaging","lump sum investing","timing risk","market timing",
    "buy the dip","contrarian strategy","value investing","growth investing",
    "momentum trading","factor investing","smart beta","low vol","quality factor",
    "size factor","value factor","fama french","five factor model","risk premium",
    "equity risk premium","carry trade","risk parity","60 40 portfolio","all weather portfolio",
    "permanent portfolio","golden butterfly","diversified allocation","alternative asset",
    "hedge fund strategy","long short equity","global macro","event driven","distressed debt",
    "merger arbitrage","convertible arbitrage","volatility arbitrage","tail risk fund",
    "reinsurance","catastrophe bond","insurance linked security","ils fund","private credit",
    "direct lending","mezzanine debt","venture debt","buyout fund","growth equity",
    "secondary market","fund of funds","evergreen fund","interval fund","tender offer fund",
    "liquidity premium","illiquidity discount","lock up period","redemption gate",
    "side pocket","performance fee","high water mark","hurdle rate","preferred return",
    "clawback provision","gp commitment","skin in the game","fee structure","2 and 20",
    "management fee","incentive fee","carry","carried interest tax","capital gain treatment",
    "service income","tax loophole","carried interest reform","wall street tax",
    "millionaire surtax","wealth tax","unrealized gain tax","mark to market","annual taxation",
    "accrual taxation","realization event","step up basis","estate tax avoidance",
    "generation skipping","dynasty trust","perpetual trust","family office","ultra high net worth",
    "family governance","succession planning","wealth transfer","philanthropic vehicle",
    "private foundation","donor advised fund","charitable remainder trust","crt",
    "charitable lead trust","clt","impact philanthropy","venture philanthropy",
    "effective altruism","earning to give","givewell","charity navigator","impact assessment",
    "cost effectiveness","qaly","daly","lives saved","marginal impact","room for more funding",
    "top charity","against malaria foundation","deworming program","cash transfer charity",
    "give directly","unconditional cash","poverty trap","graduation program","ultra poor",
    "asset transfer","training package","savings group","microfinance","grameen bank",
    "microcredit","group lending","joint liability","repayment rate","over indebtedness",
    "debt trap","financial inclusion","mobile money","m pesa","unbanked population",
    "fintech revolution","branchless banking","agent network","last mile delivery",
    "financial access","credit scoring","alternative data","thin file","machine learning credit",
    "risk based pricing","subprime lending","payday loan regulation","high interest loan",
    "debt cycle","real estate investment","reit dividend","commercial mortgage","cap rate",
    "net operating income","noi","gross rent multiplier","grm","property management",
    "property value","appraisal","comps","comparative market analysis","cma",
    "home equity","heloc","cash out refinance","jumbo mortgage","conventional loan",
    "fha loan","va loan","usda loan","conforming loan","non conforming loan",
    "mortgage backed","fannie mae","freddie mac","ginnie mae","mbs",
    "private mortgage insurance","pmi insurance","escrow","title insurance","closing costs",
    "real estate agent","commission","buyer agent","seller agent","dual agency",
    "for sale by owner","fsbo","zillow offer","ibuyer","opendoor offer",
    "real estate crowdfunding","syndication","passive income real estate","cash flow property",
    "cap rate compression","real estate cycle","commercial real estate vacancy",
    "office market outlook","retail apocalypse","industrial demand","warehouse rents",
    "multifamily vacancy","apartment construction","build to rent","single family rental",
    "sfr","manufactured housing","mobile home park","self storage","data center reit",
    "cell tower reit","net lease","triple net","nnn lease","gross lease","modified gross",
    "lease expiration","tenant improvement","capital expenditure","depreciation","amortization",
    "1031 exchange real estate","opportunity zone investment","cost segregation",
    "bonus depreciation","real estate tax","property tax","transfer tax","mello roos",
    "hoa fees","condo association","co op board","real estate law","zoning",
    "entitlement","land use","variance","conditional use permit","cup","density bonus",
    "affordable housing requirement","inclusionary zoning","adu","accessory dwelling unit",
    "short term rental","airbnb regulation","vrbo","vacation rental","proptech",
    "real estate technology","mls","multiple listing service","days on market","dom",
    "absorption rate","months of supply","seller market","buyer market","bidding war",
    "cash offer","contingency","inspection contingency","financing contingency",
    "appraisal contingency","escalation clause","pocket listing","off market",
    "wholesaling real estate","fix and flip","hard money loan","bridge loan","construction loan",
    "lot loan","land loan","agricultural loan","commercial construction","spec home",
    "custom home builder","production builder","tract home","modular home",
    "prefab home","tiny home","container home","sustainable building","leed certified",
    "energy efficient home","solar home","green building","passive house",
    "net zero home","smart home technology","home automation business",
    # ── Additional high-value business terms ──
    "business news","market news","financial news","economy news","economics",
    "economic policy","fiscal stimulus","stimulus package","infrastructure spending",
    "trade policy","tariff","tariffs","import duties","export","exports","imports",
    "supply chain disruption","global supply chain","logistics cost","freight rates",
    "container shipping","port congestion","warehousing","inventory management",
    "just in time","lean manufacturing","reshoring","nearshoring","offshoring",
    "manufacturing cost","labor cost","automation","robotics business","ai business",
    "digital transformation business","saas revenue","cloud revenue","subscription revenue",
    "arr","mrr","churn rate","customer acquisition cost","cac","lifetime value","ltv",
    "gross margin","ebitda","free cash flow","fcf","working capital","accounts receivable",
    "days sales outstanding","dso","inventory turnover","days inventory outstanding","dio",
    "days payable outstanding","dpo","cash conversion cycle","ccc","return on equity","roe",
    "return on assets","roa","return on invested capital","roic","price to earnings",
    "price to book","price to sales","enterprise value","ev ebitda","dcf",
    "discounted cash flow","net present value","npv","internal rate of return","irr",
    "payback period","break even","gross profit","operating profit","net profit",
    "top line growth","bottom line growth","operating leverage","financial leverage",
    "debt to equity","debt to ebitda","interest coverage","current ratio","quick ratio",
    "liquidity ratio","solvency ratio","working capital ratio","asset turnover",
    "inventory management","procurement","vendor management","contract negotiation",
    "intellectual property","patent","trademark","copyright business","licensing revenue",
    "royalties","franchise fee","franchise model","licensing deal","strategic partnership",
    "joint venture","spin off","carve out","divestiture","asset sale","business sale",
    "due diligence","valuation","deal structure","earn out","escrow business",
    "representations warranties","indemnification","non compete","non disclosure",
    "letter of intent","term sheet","closing","integration","post merger integration",
    "synergies","cost synergies","revenue synergies","goodwill impairment",
    "accounting","gaap","ifrs","audit","auditor","financial statement","balance sheet",
    "income statement","cash flow statement","statement of changes in equity",
    "notes to financial statements","related party transactions","off balance sheet",
    "revenue recognition","expense recognition","depreciation schedule","amortization schedule",
    "impairment","write down","write off","provision","reserve","contingent liability",
    "deferred revenue","deferred tax","tax accounting","transfer pricing","tax planning",
    "tax avoidance","tax evasion","irs audit","tax compliance","sales tax","vat",
    "excise tax","payroll tax","corporate tax rate","effective tax rate","tax credit",
    "r&d tax credit","investment tax credit","tax loss carryforward","nol","tax shield",
    "business formation","llc","corporation","s corp","partnership","sole proprietorship",
    "registered agent","articles of incorporation","bylaws","operating agreement",
    "shareholder agreement","cap table","vesting schedule equity","cliff vesting equity",
    "option pool","employee stock option","esop","equity compensation","restricted stock unit",
    "rsu","phantom stock","stock appreciation right","sar business","profit sharing",
    "bonus structure","commission structure","base salary","total compensation",
    "benefits package","health insurance business","retirement benefit","401k match business",
    "paid time off","remote work policy","hybrid work","return to office","employer brand",
    "talent acquisition","recruiting","headhunting","executive search","onboarding",
    "performance review","okr","kpi","management by objectives","compensation benchmarking",
    "pay equity","hr technology","hris","human resources business","workforce planning",
    "organizational structure","corporate culture","diversity equity inclusion business",
    "esg investing","environmental social governance","sustainability report","carbon neutral business",
    "net zero business","carbon credit","carbon offset","scope 1 2 3 emissions",
    "climate risk business","physical risk","transition risk","tcfd","sasb","gri",
    "impact investing","responsible investing","socially responsible investing","sri",
    "green bond","sustainability linked bond","blue bond","social bond",
    "stakeholder capitalism","shareholder primacy","purpose driven business","b corp",
    "benefit corporation","social enterprise","nonprofit management","charity finance",
    "endowment management","foundation investing","planned giving","major gifts",
    "fundraising","grant writing","grant funding","crowdfunding business","kickstarter campaign",
    "indiegogo campaign","gofundme business","equity crowdfunding","regulation crowdfunding",
    "reg cf","reg a plus","regulation d","private placement","accredited investor",
    "qualified purchaser","family office investing","multi family office","single family office",
    "wealth preservation","estate planning","trust administration","will","probate",
    "beneficiary","inheritance tax","gift tax","annual exclusion","gift splitting",
    "grantor retained annuity trust","grat","intentionally defective grantor trust","idgt",
    "spousal lifetime access trust","slat","qualified opportunity zone fund","qoz",
    "like kind exchange","boot","basis","cost basis","adjusted cost basis",
    "step up in basis","carryover basis","gift basis","inherited basis",
]
BUSINESS_KEYWORDS = set(kw.lower() for kw in RAW_BUSINESS_KEYWORDS)

# ====================== BLOCKLISTS ======================
ME_BLOCKLIST    = {"trump"}
US_BLOCKLIST    = {"iran"}
SPORTS_BLOCKLIST = set()
TECH_BLOCKLIST   = set()
CULTURE_BLOCKLIST= set()
WORLD_BLOCKLIST  = set()
BUSINESS_BLOCKLIST = {
    "iran", "ukraine", "gaza", "hamas", "hezbollah", "israel", "middle east",
    "russia", "taliban", "afghanistan", "military", "airstrike", "war", "missile",
    "nato", "pentagon", "troops", "soldier", "combat", "election", "vote", "ballot",
    "congress", "senate", "white house", "supreme court", "abortion", "gun control",
    "immigration", "border", "deportation", "drag", "transgender", "culture war",
}

# ── Job posting filter (site-wide) ──
JOB_FILTER_PHRASES = [
    "hiring", " job ", "jobs ", "career", "associate -",
    "full time", "part time", "per hour", "salary", "apply now",
    "job opening", "now hiring", "we're hiring", "open position",
    "sales associate", "retail associate", "warehouse associate",
    "customer service rep", "customer service associate",
    "store manager", "assistant manager", "team member",
]

# Pre-compile all patterns once
ME_PATTERN      = make_keyword_pattern(ME_KEYWORDS)
US_PATTERN      = make_keyword_pattern(US_KEYWORDS)
SPORTS_PATTERN  = make_keyword_pattern(SPORTS_KEYWORDS)
TECH_PATTERN    = make_keyword_pattern(TECH_KEYWORDS)
CULTURE_PATTERN = make_keyword_pattern(CULTURE_KEYWORDS)
WORLD_PATTERN   = make_keyword_pattern(WORLD_KEYWORDS)
BUSINESS_PATTERN = make_keyword_pattern(BUSINESS_KEYWORDS)

# ====================== SOURCES ======================
MIDDLE_EAST_SOURCES = [
    ("Broad Middle East","https://news.google.com/rss/search?q=middle+east+OR+iran+OR+israel+OR+gulf+OR+hezbollah+OR+hamas+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters","https://news.google.com/rss/search?q=reuters+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Associated Press","https://news.google.com/rss/search?q=associated+press+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Agence France-Presse","https://news.google.com/rss/search?q=afp+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC News","https://news.google.com/rss/search?q=bbc+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Economist","https://news.google.com/rss/search?q=the+economist+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times","https://news.google.com/rss/search?q=financial+times+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Wall Street Journal","https://news.google.com/rss/search?q=site:wsj.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("New York Times","https://news.google.com/rss/search?q=site:nytimes.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Post","https://news.google.com/rss/search?q=site:washingtonpost.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg","https://news.google.com/rss/search?q=bloomberg+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Media Line","https://news.google.com/rss/search?q=media+line+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AL-Monitor","https://news.google.com/rss/search?q=al+monitor+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Times of Israel","https://news.google.com/rss/search?q=times+of+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Haaretz","https://news.google.com/rss/search?q=haaretz+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("France 24","https://news.google.com/rss/search?q=france24+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Deutsche Welle","https://news.google.com/rss/search?q=dw+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian","https://news.google.com/rss/search?q=the+guardian+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Arab News","https://news.google.com/rss/search?q=arab+news+middle+east+OR+saudi+OR+gulf+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Arabiya","https://news.google.com/rss/search?q=al+arabiya+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Jerusalem Post","https://news.google.com/rss/search?q=jerusalem+post+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Christian Science Monitor","https://news.google.com/rss/search?q=site:csmonitor.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Policy","https://news.google.com/rss/search?q=site:foreignpolicy.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Axios","https://news.google.com/rss/search?q=site:axios.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NPR","https://news.google.com/rss/search?q=site:npr.org+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("PBS NewsHour","https://news.google.com/rss/search?q=pbs+newshour+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Telegraph","https://news.google.com/rss/search?q=the+telegraph+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Le Monde","https://news.google.com/rss/search?q=le+monde+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sky News","https://news.google.com/rss/search?q=sky+news+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Independent","https://news.google.com/rss/search?q=the+independent+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Politico","https://news.google.com/rss/search?q=site:politico.com+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NBC News","https://news.google.com/rss/search?q=site:nbcnews.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ABC News","https://news.google.com/rss/search?q=site:abcnews.go.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CBS News","https://news.google.com/rss/search?q=site:cbsnews.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("USA Today","https://news.google.com/rss/search?q=site:usatoday.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Gulf News","https://news.google.com/rss/search?q=gulf+news+uae+OR+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The National UAE","https://news.google.com/rss/search?q=the+national+uae+middle+east+OR+gulf+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Asharq Al-Awsat","https://news.google.com/rss/search?q=asharq+al+awsat+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Euronews","https://news.google.com/rss/search?q=euronews+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Voice of America","https://news.google.com/rss/search?q=voice+of+america+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Anadolu Agency","https://news.google.com/rss/search?q=anadolu+agency+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera","https://news.google.com/rss/search?q=al+jazeera+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs","https://news.google.com/rss/search?q=site:foreignaffairs.com+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Atlantic","https://news.google.com/rss/search?q=site:theatlantic.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Hill","https://news.google.com/rss/search?q=site:thehill.com+middle+east+OR+iran+OR+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Iran International","https://news.google.com/rss/search?q=iran+international+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Middle East Eye","https://news.google.com/rss/search?q=middle+east+eye+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Ahram Online","https://news.google.com/rss/search?q=ahram+online+egypt+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hurriyet Daily News","https://news.google.com/rss/search?q=hurriyet+daily+news+turkey+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Ynet News","https://news.google.com/rss/search?q=ynet+news+israel+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Daily Star Lebanon","https://news.google.com/rss/search?q=daily+star+lebanon+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Jadaliyya","https://news.google.com/rss/search?q=jadaliyya+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Bawaba","https://news.google.com/rss/search?q=al+bawaba+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Arabian Business","https://news.google.com/rss/search?q=arabian+business+gulf+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Jordan Times","https://news.google.com/rss/search?q=jordan+times+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Daily News Egypt","https://news.google.com/rss/search?q=daily+news+egypt+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Middle East Monitor","https://news.google.com/rss/search?q=middle+east+monitor+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("i24NEWS","https://news.google.com/rss/search?q=i24+news+israel+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sky News Arabia","https://news.google.com/rss/search?q=sky+news+arabia+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("FARS News Agency","https://news.google.com/rss/search?q=fars+news+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Middle East Report","https://news.google.com/rss/search?q=middle+east+report+merip+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TRT World","https://news.google.com/rss/search?q=trt+world+middle+east+OR+turkey+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Press TV","https://news.google.com/rss/search?q=press+tv+iran+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Tehran Times","https://news.google.com/rss/search?q=tehran+times+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Mondoweiss","https://news.google.com/rss/search?q=mondoweiss+israel+palestine+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Electronic Intifada","https://news.google.com/rss/search?q=electronic+intifada+palestine+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("L'Orient Today","https://news.google.com/rss/search?q=lorient+today+lebanon+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Israel Hayom","https://news.google.com/rss/search?q=israel+hayom+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Atlantic Council ME","https://news.google.com/rss/search?q=atlantic+council+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Council on Foreign Relations ME","https://news.google.com/rss/search?q=site:cfr.org+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Crisis Group ME","https://news.google.com/rss/search?q=crisis+group+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Middle East Institute","https://news.google.com/rss/search?q=middle+east+institute+analysis+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Brookings ME","https://news.google.com/rss/search?q=site:brookings.edu+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Carnegie ME","https://news.google.com/rss/search?q=carnegie+endowment+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("RAND ME","https://news.google.com/rss/search?q=site:rand.org+middle+east+OR+iran+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CSIS ME","https://news.google.com/rss/search?q=csis+middle+east+OR+iran+security+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Plus972 Magazine","https://news.google.com/rss/search?q=972+magazine+israel+palestine+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("New Arab","https://news.google.com/rss/search?q=new+arab+middle+east+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Levant24","https://news.google.com/rss/search?q=levant24+syria+lebanon+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al-Masry Al-Youm","https://news.google.com/rss/search?q=al+masry+al+youm+egypt+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

US_POLITICS_SOURCES = [
    ("Broad US Politics","https://news.google.com/rss/search?q=us+politics+OR+congress+OR+senate+OR+white+house+OR+supreme+court+OR+foreign+policy+OR+defense+OR+national+security+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP News","https://news.google.com/rss/search?q=when:1d+site:apnews.com&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters","https://news.google.com/rss/search?q=when:1d+site:reuters.com&hl=en-US&gl=US&ceid=US:en"),
    ("NYT","https://news.google.com/rss/search?q=when:1d+site:nytimes.com&hl=en-US&gl=US&ceid=US:en"),
    ("WSJ","https://news.google.com/rss/search?q=when:1d+site:wsj.com&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Post","https://news.google.com/rss/search?q=when:1d+site:washingtonpost.com&hl=en-US&gl=US&ceid=US:en"),
    ("Politico","https://news.google.com/rss/search?q=when:1d+site:politico.com&hl=en-US&gl=US&ceid=US:en"),
    ("Axios","https://news.google.com/rss/search?q=when:1d+site:axios.com&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg","https://news.google.com/rss/search?q=when:1d+site:bloomberg.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Atlantic","https://news.google.com/rss/search?q=when:1d+site:theatlantic.com&hl=en-US&gl=US&ceid=US:en"),
    ("The New Yorker","https://news.google.com/rss/search?q=when:1d+site:newyorker.com&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs","https://news.google.com/rss/search?q=when:1d+site:foreignaffairs.com&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Policy","https://news.google.com/rss/search?q=when:1d+site:foreignpolicy.com&hl=en-US&gl=US&ceid=US:en"),
    ("FiveThirtyEight","https://news.google.com/rss/search?q=when:1d+site:fivethirtyeight.com&hl=en-US&gl=US&ceid=US:en"),
    ("NPR","https://news.google.com/rss/search?q=when:1d+site:npr.org&hl=en-US&gl=US&ceid=US:en"),
    ("PBS NewsHour","https://news.google.com/rss/search?q=when:1d+site:pbs.org/newshour&hl=en-US&gl=US&ceid=US:en"),
    ("CBS News","https://news.google.com/rss/search?q=when:1d+site:cbsnews.com&hl=en-US&gl=US&ceid=US:en"),
    ("ABC News","https://news.google.com/rss/search?q=when:1d+site:abcnews.go.com&hl=en-US&gl=US&ceid=US:en"),
    ("NBC News","https://news.google.com/rss/search?q=when:1d+site:nbcnews.com&hl=en-US&gl=US&ceid=US:en"),
    ("USA Today","https://news.google.com/rss/search?q=when:1d+site:usatoday.com&hl=en-US&gl=US&ceid=US:en"),
    ("Christian Science Monitor","https://news.google.com/rss/search?q=when:1d+site:csmonitor.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Hill","https://news.google.com/rss/search?q=when:1d+site:thehill.com&hl=en-US&gl=US&ceid=US:en"),
    ("CNBC","https://news.google.com/rss/search?q=when:1d+site:cnbc.com&hl=en-US&gl=US&ceid=US:en"),
    ("Forbes","https://news.google.com/rss/search?q=when:1d+site:forbes.com&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times","https://news.google.com/rss/search?q=when:1d+site:ft.com&hl=en-US&gl=US&ceid=US:en"),
    ("BBC News","https://news.google.com/rss/search?q=when:1d+site:bbc.com/news&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian US","https://news.google.com/rss/search?q=when:1d+site:theguardian.com/us-news&hl=en-US&gl=US&ceid=US:en"),
    ("Los Angeles Times","https://news.google.com/rss/search?q=when:1d+site:latimes.com&hl=en-US&gl=US&ceid=US:en"),
    ("Chicago Tribune","https://news.google.com/rss/search?q=when:1d+site:chicagotribune.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Boston Globe","https://news.google.com/rss/search?q=when:1d+site:bostonglobe.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Philadelphia Inquirer","https://news.google.com/rss/search?q=when:1d+site:inquirer.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Seattle Times","https://news.google.com/rss/search?q=when:1d+site:seattletimes.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Denver Post","https://news.google.com/rss/search?q=when:1d+site:denverpost.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Arizona Republic","https://news.google.com/rss/search?q=when:1d+site:azcentral.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Star Tribune Minneapolis","https://news.google.com/rss/search?q=when:1d+site:startribune.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Oregonian","https://news.google.com/rss/search?q=when:1d+site:oregonlive.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Sacramento Bee","https://news.google.com/rss/search?q=when:1d+site:sacbee.com&hl=en-US&gl=US&ceid=US:en"),
    ("The San Francisco Chronicle","https://news.google.com/rss/search?q=when:1d+site:sfchronicle.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Dallas Morning News","https://news.google.com/rss/search?q=when:1d+site:dallasnews.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Atlanta Journal-Constitution","https://news.google.com/rss/search?q=when:1d+site:ajc.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Miami Herald","https://news.google.com/rss/search?q=when:1d+site:miamiherald.com&hl=en-US&gl=US&ceid=US:en"),
    ("ProPublica","https://news.google.com/rss/search?q=when:1d+site:propublica.org&hl=en-US&gl=US&ceid=US:en"),
    ("Pew Research Center","https://news.google.com/rss/search?q=when:1d+site:pewresearch.org&hl=en-US&gl=US&ceid=US:en"),
    ("Brookings Institution","https://news.google.com/rss/search?q=when:1d+site:brookings.edu&hl=en-US&gl=US&ceid=US:en"),
    ("RAND Corporation","https://news.google.com/rss/search?q=when:1d+site:rand.org&hl=en-US&gl=US&ceid=US:en"),
    ("Council on Foreign Relations","https://news.google.com/rss/search?q=when:1d+site:cfr.org&hl=en-US&gl=US&ceid=US:en"),
    ("The Texas Tribune","https://news.google.com/rss/search?q=when:1d+site:texastribune.org&hl=en-US&gl=US&ceid=US:en"),
    ("Politico Magazine","https://news.google.com/rss/search?q=when:1d+site:politico.com/magazine&hl=en-US&gl=US&ceid=US:en"),
    ("Roll Call","https://news.google.com/rss/search?q=when:1d+site:rollcall.com&hl=en-US&gl=US&ceid=US:en"),
    ("National Journal","https://news.google.com/rss/search?q=when:1d+site:nationaljournal.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Cook Political Report","https://news.google.com/rss/search?q=when:1d+site:cookpolitical.com&hl=en-US&gl=US&ceid=US:en"),
    ("Ballotpedia","https://news.google.com/rss/search?q=when:1d+site:ballotpedia.org&hl=en-US&gl=US&ceid=US:en"),
    ("RealClearPolitics","https://news.google.com/rss/search?q=when:1d+site:realclearpolitics.com&hl=en-US&gl=US&ceid=US:en"),
    ("FactCheck.org","https://news.google.com/rss/search?q=when:1d+site:factcheck.org&hl=en-US&gl=US&ceid=US:en"),
    ("PolitiFact","https://news.google.com/rss/search?q=when:1d+site:politifact.com&hl=en-US&gl=US&ceid=US:en"),
    ("Snopes","https://news.google.com/rss/search?q=when:1d+site:snopes.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Dispatch","https://news.google.com/rss/search?q=when:1d+site:thedispatch.com&hl=en-US&gl=US&ceid=US:en"),
    ("Notus","https://news.google.com/rss/search?q=when:1d+site:notus.org&hl=en-US&gl=US&ceid=US:en"),
    ("Punchbowl News","https://news.google.com/rss/search?q=when:1d+site:punchbowl.news&hl=en-US&gl=US&ceid=US:en"),
    ("Semafor","https://news.google.com/rss/search?q=when:1d+site:semafor.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Bulwark","https://news.google.com/rss/search?q=when:1d+site:thebulwark.com&hl=en-US&gl=US&ceid=US:en"),
    ("McClatchy DC Bureau","https://news.google.com/rss/search?q=when:1d+site:mcclatchydc.com&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg Government","https://news.google.com/rss/search?q=when:1d+site:bgov.com&hl=en-US&gl=US&ceid=US:en"),
    ("Stat News","https://news.google.com/rss/search?q=when:1d+site:statnews.com&hl=en-US&gl=US&ceid=US:en"),
    ("Defense News","https://news.google.com/rss/search?q=when:1d+site:defensenews.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Cipher Brief","https://news.google.com/rss/search?q=when:1d+site:thecipherbrief.com&hl=en-US&gl=US&ceid=US:en"),
    ("Just Security","https://news.google.com/rss/search?q=when:1d+site:justsecurity.org&hl=en-US&gl=US&ceid=US:en"),
    ("Lawfare Blog","https://news.google.com/rss/search?q=when:1d+site:lawfareblog.com&hl=en-US&gl=US&ceid=US:en"),
    ("SCOTUSblog","https://news.google.com/rss/search?q=when:1d+site:scotusblog.com&hl=en-US&gl=US&ceid=US:en"),
    ("OpenSecrets.org","https://news.google.com/rss/search?q=when:1d+site:opensecrets.org&hl=en-US&gl=US&ceid=US:en"),
    ("The Markup","https://news.google.com/rss/search?q=when:1d+site:themarkup.org&hl=en-US&gl=US&ceid=US:en"),
    ("Governing Magazine","https://news.google.com/rss/search?q=when:1d+site:governing.com&hl=en-US&gl=US&ceid=US:en"),
    ("Government Executive","https://news.google.com/rss/search?q=when:1d+site:govexec.com&hl=en-US&gl=US&ceid=US:en"),
    ("Federal News Network","https://news.google.com/rss/search?q=when:1d+site:federalnewsnetwork.com&hl=en-US&gl=US&ceid=US:en"),
    ("Defense One","https://news.google.com/rss/search?q=when:1d+site:defenseone.com&hl=en-US&gl=US&ceid=US:en"),
    ("War on the Rocks","https://news.google.com/rss/search?q=when:1d+site:warontherocks.com&hl=en-US&gl=US&ceid=US:en"),
    ("National Defense Magazine","https://news.google.com/rss/search?q=when:1d+site:nationaldefensemagazine.org&hl=en-US&gl=US&ceid=US:en"),
    ("NewsNation","https://news.google.com/rss/search?q=when:1d+site:newsnationnow.com&hl=en-US&gl=US&ceid=US:en"),
    ("Straight Arrow News","https://news.google.com/rss/search?q=when:1d+site:straightarrownews.com&hl=en-US&gl=US&ceid=US:en"),
]

SPORTS_SOURCES = [
    ("Broad Sports","https://news.google.com/rss/search?q=march+madness+OR+college+basketball+OR+ncaa+tournament+OR+nfl+OR+nba+OR+mlb+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters Sports","https://news.google.com/rss/search?q=reuters+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP Sports","https://news.google.com/rss/search?q=associated+press+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AFP Sports","https://news.google.com/rss/search?q=afp+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC Sport","https://news.google.com/rss/search?q=bbc+sport+news+OR+football+OR+cricket+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ESPN","https://news.google.com/rss/search?q=espn+news+sports+OR+nfl+OR+nba+OR+mlb+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sky Sports","https://news.google.com/rss/search?q=sky+sports+news+OR+premier+league+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Athletic","https://news.google.com/rss/search?q=the+athletic+news+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sports Illustrated","https://news.google.com/rss/search?q=when:1d+site:si.com+sports+OR+nfl+OR+nba+OR+mlb&hl=en-US&gl=US&ceid=US:en"),
    ("CBS Sports","https://news.google.com/rss/search?q=when:1d+site:cbssports.com&hl=en-US&gl=US&ceid=US:en"),
    ("FOX Sports","https://news.google.com/rss/search?q=fox+sports+news+OR+nfl+OR+nba+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NBC Sports","https://news.google.com/rss/search?q=nbc+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Yahoo Sports","https://news.google.com/rss/search?q=yahoo+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bleacher Report","https://news.google.com/rss/search?q=bleacher+report+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Sporting News","https://news.google.com/rss/search?q=sporting+news+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("USA Today Sports","https://news.google.com/rss/search?q=when:1d+site:usatoday.com+sports&hl=en-US&gl=US&ceid=US:en"),
    ("NPR Sports","https://news.google.com/rss/search?q=site:npr.org+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian Sport","https://news.google.com/rss/search?q=the+guardian+sport+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NYT Sport","https://news.google.com/rss/search?q=site:nytimes.com+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg Sports","https://news.google.com/rss/search?q=bloomberg+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Front Office Sports","https://news.google.com/rss/search?q=front+office+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sportico","https://news.google.com/rss/search?q=sportico+sports+business+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sports Business Journal","https://news.google.com/rss/search?q=sports+business+journal+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Defector","https://news.google.com/rss/search?q=defector+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The GIST","https://news.google.com/rss/search?q=the+gist+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Ringer","https://news.google.com/rss/search?q=the+ringer+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Yardbarker","https://news.google.com/rss/search?q=yardbarker+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("SB Nation","https://news.google.com/rss/search?q=sbnation+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sportskeeda","https://news.google.com/rss/search?q=sportskeeda+sports+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Goal.com","https://news.google.com/rss/search?q=goal.com+soccer+football+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Marca English","https://news.google.com/rss/search?q=marca+english+soccer+sport+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AS USA","https://news.google.com/rss/search?q=as+usa+sport+soccer+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("L'Equipe","https://news.google.com/rss/search?q=lequipe+sport+france+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Cricbuzz","https://news.google.com/rss/search?q=cricbuzz+cricket+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ESPNcricinfo","https://news.google.com/rss/search?q=espncricinfo+cricket+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("theScore","https://news.google.com/rss/search?q=thescore+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MMA Fighting","https://news.google.com/rss/search?q=mma+fighting+ufc+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BoxingScene","https://news.google.com/rss/search?q=boxing+scene+boxing+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Golf Digest","https://news.google.com/rss/search?q=golf+digest+pga+golf+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Motorsport.com","https://news.google.com/rss/search?q=motorsport+f1+racing+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Autosport","https://news.google.com/rss/search?q=autosport+f1+motorsport+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Eurosport","https://news.google.com/rss/search?q=eurosport+sports+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TalkSport","https://news.google.com/rss/search?q=talksport+football+sport+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Daily Mail Sport","https://news.google.com/rss/search?q=daily+mail+sport+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Independent Sport","https://news.google.com/rss/search?q=independent+sport+football+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Players Tribune","https://news.google.com/rss/search?q=players+tribune+athlete+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

TECH_SOURCES = [
    ("Broad Tech and Life","https://news.google.com/rss/search?q=technology+news+OR+ai+OR+tech+OR+gaming+OR+wearable+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters Technology","https://news.google.com/rss/search?q=reuters+technology+ai+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP Technology","https://news.google.com/rss/search?q=associated+press+technology+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AFP Technology","https://news.google.com/rss/search?q=afp+technology+ai+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC Technology","https://news.google.com/rss/search?q=bbc+technology+ai+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Wired","https://news.google.com/rss/search?q=wired+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MIT Technology Review","https://news.google.com/rss/search?q=mit+technology+review+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Verge","https://news.google.com/rss/search?q=the+verge+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TechCrunch","https://news.google.com/rss/search?q=techcrunch+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Engadget","https://news.google.com/rss/search?q=engadget+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CNET","https://news.google.com/rss/search?q=cnet+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("ZDNet","https://news.google.com/rss/search?q=zdnet+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("IEEE Spectrum","https://news.google.com/rss/search?q=ieee+spectrum+news+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Nature","https://news.google.com/rss/search?q=nature+news+science+OR+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Ars Technica","https://news.google.com/rss/search?q=ars+technica+tech+OR+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Mashable","https://news.google.com/rss/search?q=mashable+tech+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Gizmodo","https://news.google.com/rss/search?q=gizmodo+tech+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TechRadar","https://news.google.com/rss/search?q=techradar+tech+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("VentureBeat","https://news.google.com/rss/search?q=venturebeat+ai+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Information","https://news.google.com/rss/search?q=the+information+tech+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Axios Technology","https://news.google.com/rss/search?q=site:axios.com+technology+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg Technology","https://news.google.com/rss/search?q=bloomberg+technology+ai+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NYT Technology","https://news.google.com/rss/search?q=site:nytimes.com+technology+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("WSJ Technology","https://news.google.com/rss/search?q=site:wsj.com+technology+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("WaPo Technology","https://news.google.com/rss/search?q=site:washingtonpost.com+technology+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Guardian Technology","https://news.google.com/rss/search?q=guardian+technology+ai+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Popular Science","https://news.google.com/rss/search?q=popular+science+tech+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Scientific American","https://news.google.com/rss/search?q=scientific+american+tech+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("New Scientist","https://news.google.com/rss/search?q=new+scientist+tech+science+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Next Web","https://news.google.com/rss/search?q=the+next+web+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Tom's Hardware","https://news.google.com/rss/search?q=toms+hardware+tech+gpu+cpu+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Android Authority","https://news.google.com/rss/search?q=android+authority+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MacRumors","https://news.google.com/rss/search?q=macrumors+apple+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("9to5Mac","https://news.google.com/rss/search?q=9to5mac+apple+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BleepingComputer","https://news.google.com/rss/search?q=bleepingcomputer+cybersecurity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Krebs on Security","https://news.google.com/rss/search?q=krebs+security+cyber+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("IGN","https://news.google.com/rss/search?q=ign+gaming+tech+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Polygon","https://news.google.com/rss/search?q=polygon+gaming+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Kotaku","https://news.google.com/rss/search?q=kotaku+gaming+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("GamesIndustry.biz","https://news.google.com/rss/search?q=gamesindustry+biz+gaming+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("PC Gamer","https://news.google.com/rss/search?q=pc+gamer+gaming+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

CULTURE_SOURCES = [
    ("Broad Culture","https://news.google.com/rss/search?q=celebrity+news+OR+hollywood+OR+fashion+week+OR+met+gala+OR+red+carpet+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters Culture","https://news.google.com/rss/search?q=reuters+entertainment+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP Entertainment","https://news.google.com/rss/search?q=associated+press+entertainment+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AFP Culture","https://news.google.com/rss/search?q=afp+culture+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC Culture","https://news.google.com/rss/search?q=bbc+culture+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NYT Arts","https://news.google.com/rss/search?q=new+york+times+arts+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("WaPo Arts","https://news.google.com/rss/search?q=washington+post+arts+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("LA Times Entertainment","https://news.google.com/rss/search?q=los+angeles+times+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian Arts","https://news.google.com/rss/search?q=the+guardian+arts+culture+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Vanity Fair","https://news.google.com/rss/search?q=vanity+fair+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Vogue","https://news.google.com/rss/search?q=vogue+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Harper's Bazaar","https://news.google.com/rss/search?q=harpers+bazaar+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Elle","https://news.google.com/rss/search?q=elle+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("GQ","https://news.google.com/rss/search?q=gq+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Esquire","https://news.google.com/rss/search?q=esquire+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Cut","https://news.google.com/rss/search?q=the+cut+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Refinery29","https://news.google.com/rss/search?q=refinery29+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("TMZ","https://news.google.com/rss/search?q=tmz+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("E! News","https://news.google.com/rss/search?q=e!+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("People Magazine","https://news.google.com/rss/search?q=people+magazine+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hollywood Reporter","https://news.google.com/rss/search?q=hollywood+reporter+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Variety","https://news.google.com/rss/search?q=variety+news+hollywood+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Deadline","https://news.google.com/rss/search?q=deadline+hollywood+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Entertainment Weekly","https://news.google.com/rss/search?q=entertainment+weekly+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Billboard","https://news.google.com/rss/search?q=billboard+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Rolling Stone","https://news.google.com/rss/search?q=rolling+stone+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Pitchfork","https://news.google.com/rss/search?q=pitchfork+news+music+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Complex","https://news.google.com/rss/search?q=complex+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Screen Rant","https://news.google.com/rss/search?q=screen+rant+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Collider","https://news.google.com/rss/search?q=collider+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("IndieWire","https://news.google.com/rss/search?q=indiewire+news+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Vulture","https://news.google.com/rss/search?q=vulture+entertainment+culture+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Wrap","https://news.google.com/rss/search?q=the+wrap+hollywood+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("A.V. Club","https://news.google.com/rss/search?q=av+club+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NME","https://news.google.com/rss/search?q=nme+music+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Consequence of Sound","https://news.google.com/rss/search?q=consequence+of+sound+music+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Stereogum","https://news.google.com/rss/search?q=stereogum+music+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hollywood Life","https://news.google.com/rss/search?q=hollywood+life+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Just Jared","https://news.google.com/rss/search?q=just+jared+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("PopSugar","https://news.google.com/rss/search?q=popsugar+news+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("US Weekly","https://news.google.com/rss/search?q=us+weekly+celebrity+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Daily Mail Entertainment","https://news.google.com/rss/search?q=daily+mail+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Teen Vogue","https://news.google.com/rss/search?q=teen+vogue+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Nylon Magazine","https://news.google.com/rss/search?q=nylon+magazine+news+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Women's Wear Daily","https://news.google.com/rss/search?q=womens+wear+daily+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Fashionista","https://news.google.com/rss/search?q=fashionista+fashion+trends+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Dazed","https://news.google.com/rss/search?q=dazed+magazine+fashion+culture+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Art Newspaper","https://news.google.com/rss/search?q=the+art+newspaper+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hyperallergic","https://news.google.com/rss/search?q=hyperallergic+art+culture+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Artforum","https://news.google.com/rss/search?q=artforum+art+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Frieze","https://news.google.com/rss/search?q=frieze+art+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Business of Fashion","https://news.google.com/rss/search?q=business+of+fashion+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("PetaPixel","https://news.google.com/rss/search?q=petapixel+photography+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Literary Hub","https://news.google.com/rss/search?q=literary+hub+books+culture+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Publishers Weekly","https://news.google.com/rss/search?q=publishers+weekly+books+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Book Riot","https://news.google.com/rss/search?q=book+riot+books+reading+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Variety Latino","https://news.google.com/rss/search?q=variety+latino+entertainment+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Broadway World","https://news.google.com/rss/search?q=broadway+world+theater+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Cosmopolitan","https://news.google.com/rss/search?q=cosmopolitan+celebrity+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Glamour","https://news.google.com/rss/search?q=glamour+magazine+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("W Magazine","https://news.google.com/rss/search?q=w+magazine+fashion+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

BUSINESS_SOURCES = [
    ("Broad Business","https://news.google.com/rss/search?q=stock+market+OR+earnings+OR+economy+OR+wall+street+OR+federal+reserve+OR+inflation+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Reuters Finance","https://news.google.com/rss/search?q=site:reuters.com+business+OR+markets+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AP Business","https://news.google.com/rss/search?q=associated+press+business+OR+markets+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg","https://news.google.com/rss/search?q=site:bloomberg.com+markets+OR+business+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Wall Street Journal","https://news.google.com/rss/search?q=site:wsj.com+markets+OR+business+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times","https://news.google.com/rss/search?q=site:ft.com+markets+OR+business+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Economist","https://news.google.com/rss/search?q=site:economist.com+business+OR+finance+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CNBC","https://news.google.com/rss/search?q=site:cnbc.com+markets+OR+business+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Forbes","https://news.google.com/rss/search?q=site:forbes.com+business+OR+finance+OR+investing+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Business Insider","https://news.google.com/rss/search?q=business+insider+markets+OR+business+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Fortune","https://news.google.com/rss/search?q=site:fortune.com+business+OR+finance+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MarketWatch","https://news.google.com/rss/search?q=site:marketwatch.com+markets+OR+stocks+OR+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Yahoo Finance","https://news.google.com/rss/search?q=yahoo+finance+markets+OR+stocks+OR+earnings+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Barron's","https://news.google.com/rss/search?q=barrons+investing+OR+markets+OR+stocks+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Seeking Alpha","https://news.google.com/rss/search?q=seeking+alpha+stocks+OR+investing+OR+earnings+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Street","https://news.google.com/rss/search?q=thestreet+investing+OR+markets+OR+stocks+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Harvard Business Review","https://news.google.com/rss/search?q=site:hbr.org+business+OR+management+OR+strategy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Entrepreneur","https://news.google.com/rss/search?q=site:entrepreneur.com+business+OR+startup+OR+small+business+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Inc Magazine","https://news.google.com/rss/search?q=site:inc.com+business+OR+startup+OR+small+business+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Fast Company","https://news.google.com/rss/search?q=site:fastcompany.com+business+OR+innovation+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Investopedia","https://news.google.com/rss/search?q=investopedia+investing+OR+finance+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Morningstar","https://news.google.com/rss/search?q=morningstar+investing+OR+funds+OR+stocks+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Kiplinger","https://news.google.com/rss/search?q=kiplinger+personal+finance+OR+investing+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NerdWallet","https://news.google.com/rss/search?q=nerdwallet+personal+finance+OR+investing+OR+credit+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bankrate","https://news.google.com/rss/search?q=bankrate+mortgage+OR+savings+OR+rates+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CoinDesk","https://news.google.com/rss/search?q=coindesk+crypto+OR+bitcoin+OR+blockchain+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Block","https://news.google.com/rss/search?q=theblock+crypto+OR+bitcoin+OR+defi+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Decrypt","https://news.google.com/rss/search?q=decrypt+crypto+OR+bitcoin+OR+web3+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("HousingWire","https://news.google.com/rss/search?q=housingwire+real+estate+OR+mortgage+OR+housing+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Inman","https://news.google.com/rss/search?q=inman+real+estate+OR+housing+OR+mortgage+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bisnow","https://news.google.com/rss/search?q=bisnow+commercial+real+estate+OR+cre+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bitcoin Magazine","https://news.google.com/rss/search?q=bitcoin+magazine+bitcoin+OR+crypto+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BeInCrypto","https://news.google.com/rss/search?q=beincrypto+crypto+OR+bitcoin+OR+defi+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CoinTelegraph","https://news.google.com/rss/search?q=cointelegraph+crypto+OR+bitcoin+OR+blockchain+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Ledger Insights","https://news.google.com/rss/search?q=ledger+insights+blockchain+OR+enterprise+crypto+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Blockworks","https://news.google.com/rss/search?q=blockworks+crypto+OR+bitcoin+OR+defi+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bankless","https://news.google.com/rss/search?q=bankless+defi+OR+ethereum+OR+web3+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CryptoSlate","https://news.google.com/rss/search?q=cryptoslate+crypto+OR+bitcoin+OR+altcoin+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Real Vision","https://news.google.com/rss/search?q=real+vision+markets+OR+macro+OR+investing+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("FinViz","https://news.google.com/rss/search?q=finviz+stocks+OR+markets+OR+screener+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("bplans","https://news.google.com/rss/search?q=bplans+small+business+OR+startup+OR+business+plan+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Startups.com","https://news.google.com/rss/search?q=startups+com+startup+OR+venture+capital+OR+funding+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("SCORE","https://news.google.com/rss/search?q=score+org+small+business+OR+mentorship+OR+business+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Zillow Research","https://news.google.com/rss/search?q=zillow+research+housing+market+OR+home+prices+OR+rents+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Zacks","https://news.google.com/rss/search?q=zacks+investment+stocks+OR+earnings+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Investing.com","https://news.google.com/rss/search?q=investing+com+markets+OR+stocks+OR+forex+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NYT Business","https://news.google.com/rss/search?q=site:nytimes.com+business+OR+economy+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Washington Post Business","https://news.google.com/rss/search?q=site:washingtonpost.com+business+OR+economy+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Guardian Business","https://news.google.com/rss/search?q=the+guardian+business+OR+economy+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CBS News Business","https://news.google.com/rss/search?q=site:cbsnews.com+business+OR+economy+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("PBS Business","https://news.google.com/rss/search?q=site:pbs.org+business+OR+economy+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("SEC News","https://news.google.com/rss/search?q=sec+gov+securities+OR+enforcement+OR+investor+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("FDIC News","https://news.google.com/rss/search?q=fdic+banking+OR+bank+failure+OR+deposit+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("CFPB News","https://news.google.com/rss/search?q=cfpb+consumer+finance+OR+credit+OR+banking+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("SBA News","https://news.google.com/rss/search?q=sba+small+business+OR+loan+OR+entrepreneur+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Stock Analysis","https://news.google.com/rss/search?q=stock+analysis+earnings+OR+stocks+OR+markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("GlobeNewswire Business","https://news.google.com/rss/search?q=globenewswire+earnings+OR+business+announcement+when:1d&hl=en-US&gl=US&ceid=US:en"),
]

WORLD_SOURCES = [
    # Broad sweeps
    ("Broad World","https://news.google.com/rss/search?q=europe+OR+asia+OR+japan+OR+china+OR+india+OR+uk+OR+france+OR+germany+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Broad Asia","https://news.google.com/rss/search?q=asia+pacific+OR+southeast+asia+OR+east+asia+OR+south+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Broad Europe","https://news.google.com/rss/search?q=european+union+OR+nato+OR+ukraine+OR+eu+summit+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Global wires
    ("Reuters World","https://news.google.com/rss/search?q=reuters+europe+OR+reuters+asia+OR+reuters+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Associated Press World","https://news.google.com/rss/search?q=associated+press+europe+OR+associated+press+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Agence France-Presse","https://news.google.com/rss/search?q=afp+europe+OR+afp+asia+OR+agence+france+presse+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("BBC World","https://news.google.com/rss/search?q=bbc+news+europe+OR+bbc+news+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Economist","https://news.google.com/rss/search?q=the+economist+europe+OR+the+economist+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Financial Times","https://news.google.com/rss/search?q=financial+times+europe+OR+financial+times+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Bloomberg World","https://news.google.com/rss/search?q=bloomberg+europe+OR+bloomberg+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Al Jazeera World","https://news.google.com/rss/search?q=al+jazeera+europe+OR+al+jazeera+asia+OR+al+jazeera+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Europe
    ("Euronews","https://news.google.com/rss/search?q=euronews+europe+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("France 24","https://news.google.com/rss/search?q=france24+europe+OR+france24+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Deutsche Welle","https://news.google.com/rss/search?q=dw+news+europe+OR+dw+news+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian Europe","https://news.google.com/rss/search?q=the+guardian+europe+OR+the+guardian+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Politico Europe","https://news.google.com/rss/search?q=politico+europe+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Le Monde","https://news.google.com/rss/search?q=le+monde+international+OR+le+monde+europe+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Der Spiegel","https://news.google.com/rss/search?q=der+spiegel+international+OR+spiegel+europe+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("El Pais","https://news.google.com/rss/search?q=el+pais+europe+OR+el+pais+international+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Times of London","https://news.google.com/rss/search?q=the+times+london+europe+OR+times+of+london+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Telegraph Europe","https://news.google.com/rss/search?q=the+telegraph+europe+OR+telegraph+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Irish Times","https://news.google.com/rss/search?q=irish+times+europe+OR+irish+times+international+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Local Europe","https://news.google.com/rss/search?q=the+local+europe+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Neue Zurcher Zeitung","https://news.google.com/rss/search?q=neue+zurcher+zeitung+OR+nzz+international+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("La Repubblica","https://news.google.com/rss/search?q=la+repubblica+italy+europe+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Le Figaro","https://news.google.com/rss/search?q=le+figaro+france+europe+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Frankfurter Allgemeine","https://news.google.com/rss/search?q=frankfurter+allgemeine+OR+faz+germany+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Aftenposten","https://news.google.com/rss/search?q=aftenposten+norway+scandinavia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Dagens Nyheter","https://news.google.com/rss/search?q=dagens+nyheter+sweden+europe+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Rzeczpospolita","https://news.google.com/rss/search?q=rzeczpospolita+poland+europe+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Japan
    ("Nikkei Asia","https://news.google.com/rss/search?q=nikkei+asia+japan+economy+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Japan Times","https://news.google.com/rss/search?q=japan+times+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Asahi Shimbun English","https://news.google.com/rss/search?q=asahi+shimbun+english+japan+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("NHK World","https://news.google.com/rss/search?q=nhk+world+japan+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Kyodo News","https://news.google.com/rss/search?q=kyodo+news+japan+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Japan Forward","https://news.google.com/rss/search?q=japan+forward+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Southeast Asia
    ("Bangkok Post","https://news.google.com/rss/search?q=bangkok+post+thailand+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Nation Thailand","https://news.google.com/rss/search?q=the+nation+thailand+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Straits Times","https://news.google.com/rss/search?q=straits+times+singapore+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("South China Morning Post","https://news.google.com/rss/search?q=south+china+morning+post+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Jakarta Post","https://news.google.com/rss/search?q=jakarta+post+indonesia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Star Malaysia","https://news.google.com/rss/search?q=the+star+malaysia+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("VnExpress","https://news.google.com/rss/search?q=vnexpress+vietnam+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Philippine Daily Inquirer","https://news.google.com/rss/search?q=philippine+daily+inquirer+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Diplomat","https://news.google.com/rss/search?q=the+diplomat+asia+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Asia Times","https://news.google.com/rss/search?q=asia+times+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Korea / India
    ("Korea Herald","https://news.google.com/rss/search?q=korea+herald+south+korea+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Korea Times","https://news.google.com/rss/search?q=korea+times+seoul+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Hindustan Times","https://news.google.com/rss/search?q=hindustan+times+india+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("The Hindu","https://news.google.com/rss/search?q=the+hindu+india+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Pacific
    ("The Australian","https://news.google.com/rss/search?q=the+australian+asia+OR+the+australian+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Sydney Morning Herald","https://news.google.com/rss/search?q=sydney+morning+herald+asia+OR+smh+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
    # Think tanks / analysis
    ("East Asia Forum","https://news.google.com/rss/search?q=east+asia+forum+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Eurasia Review","https://news.google.com/rss/search?q=eurasia+review+news+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Foreign Affairs World","https://news.google.com/rss/search?q=foreign+affairs+europe+OR+foreign+affairs+asia+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Council on Foreign Relations","https://news.google.com/rss/search?q=cfr+europe+OR+cfr+asia+OR+council+foreign+relations+world+when:1d&hl=en-US&gl=US&ceid=US:en"),
]
def normalize_title(title):
    if " - " in title:
        title = title.rsplit(" - ", 1)[0]
    return title.strip().lower()

def fetch_section(sources, keywords, pattern, blocklist):
    matches = []
    seen_title = set()
    source_count = defaultdict(int)  # keyed by URL

    for source_name, url in sources:
        if source_count[url] >= 5:
            continue
        for attempt in range(3):
            try:
                print(f"  Fetching {source_name}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    feed = feedparser.parse(response.read().decode('utf-8', errors='ignore'))
                if feed.bozo:
                    break
                print(f"  {source_name} returned {len(feed.entries)} entries")
                for entry in feed.entries:
                    if source_count[url] >= 5:
                        break
                    raw_title = entry.title.strip()
                    norm_title = normalize_title(raw_title)
                    link = entry.get('link', '#')
                    if norm_title in seen_title:
                        continue
                    title_lower = raw_title.lower()
                    if blocklist and any(block in title_lower for block in blocklist):
                        continue
                    if any(phrase in title_lower for phrase in JOB_FILTER_PHRASES):
                        continue
                    if title_matches_keywords(title_lower, pattern):
                        ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                        ts = calendar.timegm(ts_struct) if ts_struct else time.time()
                        matches.append((ts, raw_title, source_name, link))
                        seen_title.add(norm_title)
                        source_count[url] += 1
                break
            except Exception as e:
                print(f"    Attempt {attempt+1} failed: {str(e)}")
                time.sleep(2)

    matches.sort(reverse=True, key=lambda x: x[0])
    return matches

# ====================== FETCH ALL ======================
middle_matches   = fetch_section(MIDDLE_EAST_SOURCES, ME_KEYWORDS, ME_PATTERN, ME_BLOCKLIST)
us_matches       = fetch_section(US_POLITICS_SOURCES, US_KEYWORDS, US_PATTERN, US_BLOCKLIST)
sports_matches   = fetch_section(SPORTS_SOURCES, SPORTS_KEYWORDS, SPORTS_PATTERN, SPORTS_BLOCKLIST)
tech_matches     = fetch_section(TECH_SOURCES, TECH_KEYWORDS, TECH_PATTERN, TECH_BLOCKLIST)
culture_matches  = fetch_section(CULTURE_SOURCES, CULTURE_KEYWORDS, CULTURE_PATTERN, CULTURE_BLOCKLIST)
world_matches    = fetch_section(WORLD_SOURCES, WORLD_KEYWORDS, WORLD_PATTERN, WORLD_BLOCKLIST)
business_matches = fetch_section(BUSINESS_SOURCES, BUSINESS_KEYWORDS, BUSINESS_PATTERN, BUSINESS_BLOCKLIST)

# ====================== TIME SPLIT (3h breaking / 21h daily, bidirectional spillover) ======================
THREE_HOURS      = 3 * 3600
TWENTY_ONE_HOURS = 21 * 3600
MAX_ITEMS        = 30

def split_breaking_daily(all_matches, max_items=MAX_ITEMS):
    now = time.time()
    breaking_raw = [m for m in all_matches if (now - m[0]) <= THREE_HOURS]
    daily_raw    = [m for m in all_matches if THREE_HOURS < (now - m[0]) <= THREE_HOURS + TWENTY_ONE_HOURS]
    breaking_filled = list(breaking_raw[:max_items])
    if len(breaking_filled) < max_items:
        needed = max_items - len(breaking_filled)
        spillover = [m for m in daily_raw if m not in breaking_filled]
        breaking_filled.extend(spillover[:needed])
    daily_filled = [m for m in daily_raw if m not in breaking_filled][:max_items]
    if len(daily_filled) < max_items:
        needed = max_items - len(daily_filled)
        spillover = [m for m in breaking_raw if m not in daily_filled and m not in breaking_filled[:max_items]]
        daily_filled.extend(spillover[:needed])
    return breaking_filled[:max_items], daily_filled[:max_items]

us_breaking,      us_recent      = split_breaking_daily(us_matches)
middle_breaking,  middle_recent  = split_breaking_daily(middle_matches)
sports_breaking,  sports_recent  = split_breaking_daily(sports_matches)
tech_breaking,    tech_recent    = split_breaking_daily(tech_matches)
def split_culture(all_matches, max_items=MAX_ITEMS):
    SEVENTY_TWO_HOURS = 72 * 3600
    now = time.time()
    breaking_raw = [m for m in all_matches if (now - m[0]) <= THREE_HOURS]
    daily_raw    = [m for m in all_matches if THREE_HOURS < (now - m[0]) <= SEVENTY_TWO_HOURS]
    breaking_filled = list(breaking_raw[:max_items])
    if len(breaking_filled) < max_items:
        needed = max_items - len(breaking_filled)
        spillover = [m for m in daily_raw if m not in breaking_filled]
        breaking_filled.extend(spillover[:needed])
    daily_filled = [m for m in daily_raw if m not in breaking_filled][:max_items]
    if len(daily_filled) < max_items:
        needed = max_items - len(daily_filled)
        spillover = [m for m in breaking_raw if m not in daily_filled and m not in breaking_filled[:max_items]]
        daily_filled.extend(spillover[:needed])
    return breaking_filled[:max_items], daily_filled[:max_items]

culture_breaking, culture_recent = split_culture(culture_matches)
world_breaking,   world_recent   = split_breaking_daily(world_matches)
business_breaking, business_recent = split_breaking_daily(business_matches)

# ====================== PDT TIMESTAMP ======================
PDT_OFFSET = timedelta(hours=-7)

def ts_to_pdt(ts):
    dt_utc = datetime.utcfromtimestamp(ts)
    dt_pdt = dt_utc + PDT_OFFSET
    return dt_pdt.strftime("%-I:%M %p PDT")

# ====================== TOPIC CLUSTERING ======================
# Groups headlines that share 3+ significant words (ignoring stopwords).
# Headlines in a cluster are shown together under a story header with a source-count badge.

STOPWORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","as","is","was","are","were","be","been","being","have",
    "has","had","do","does","did","will","would","could","should","may",
    "might","shall","its","it","this","that","these","those","says","say",
    "said","after","over","into","about","up","out","than","then","new",
    "just","more","also","amid","amid","amid","report","reports","amid",
    "amid","under","amid","amid","amid","amid","amid","amid",
}

def headline_tokens(title):
    words = re.findall(r'[a-zA-Z]{3,}', title.lower())
    return set(w for w in words if w not in STOPWORDS)

# Sources that produce high volumes of short, similarly-worded blurbs and should
# never be the seed of a cluster or count toward a multi-source cluster badge.
CLUSTER_EXCLUDED_SOURCES = {
    "just jared", "justjared", "just jared jr",
    "hollywood life", "hollywoodlife",
}

def _is_cluster_excluded(source_name):
    return any(excl in source_name.lower() for excl in CLUSTER_EXCLUDED_SOURCES)

def cluster_items(items, min_shared=3):
    """
    Returns a list of clusters. Each cluster is a list of (ts, title, source, link).
    Single-item clusters are just solo headlines. Multi-item clusters are grouped stories.

    Rules:
    - Sources in CLUSTER_EXCLUDED_SOURCES are never used as a cluster seed and
      are never merged into another cluster — they always appear solo.
    - A single source can contribute at most 1 article to any given cluster,
      so a multi-source badge always reflects genuine cross-outlet coverage.
    """
    used = [False] * len(items)
    clusters = []
    token_cache = [headline_tokens(it[1]) for it in items]

    for i in range(len(items)):
        if used[i]:
            continue
        seed_ts, seed_title, seed_source, seed_link = items[i]
        # Excluded sources always go solo — never seed a cluster
        if _is_cluster_excluded(seed_source):
            used[i] = True
            clusters.append([items[i]])
            continue
        cluster = [items[i]]
        used[i] = True
        sources_in_cluster = {seed_source.lower()}
        for j in range(i + 1, len(items)):
            if used[j]:
                continue
            ts_j, title_j, source_j, link_j = items[j]
            # Excluded sources never join a cluster
            if _is_cluster_excluded(source_j):
                continue
            # One article per source per cluster
            if source_j.lower() in sources_in_cluster:
                continue
            shared = len(token_cache[i] & token_cache[j])
            if shared >= min_shared:
                cluster.append(items[j])
                used[j] = True
                sources_in_cluster.add(source_j.lower())
        clusters.append(cluster)
    return clusters

# ====================== RENDER HEADLINES ======================
# Each item is (ts, title, source, link).
# Items published within 30 minutes get a "new" white dot.
# Items seen on previous visit (tracked via localStorage) get no dot.
# Clusters of 2+ headlines about same story are grouped with a source-count badge.

THIRTY_MIN = 1800

def render_column(items):
    """
    Cluster items, then render with new-dot indicators and story grouping.
    Returns HTML string.
    """
    now = time.time()
    clusters = cluster_items(items)
    out = ""
    for cluster in clusters:
        if len(cluster) == 1:
            ts, title, source, link = cluster[0]
            friendly = get_friendly_source(source)
            time_str = ts_to_pdt(ts)
            display_title = title[0].upper() + title[1:] if title else title
            is_hot = (now - ts) <= THIRTY_MIN
            # data-link used by JS for "seen" tracking; data-ts for breaking-news banner
            hot_dot = '<span class="new-dot" title="Published in the last 30 minutes">&#9679;</span> ' if is_hot else ''
            safe_dtitle = display_title.replace('"', '&quot;')
            anchor_id = "hl-" + hashlib.md5(link.encode()).hexdigest()[:8]
            out += (
                f'<div id="{anchor_id}" class="headline" data-link="{link}" data-ts="{int(ts)}">'
                f'{hot_dot}'
                f'<span class="title">{display_title}</span>'
                f' <span class="ts-label">{time_str}</span>'
                f' <span class="src-label">\u2014 {friendly}</span>'
                f' <a class="link" href="{link}" target="_blank">[Full Article]</a>'
                f'</div>\n'
            )
        else:
            # Multi-source cluster: grouped story card with collapsible sub-items
            cluster.sort(key=lambda x: x[0], reverse=True)
            lead_ts, lead_title, lead_source, lead_link = cluster[0]
            display_title = lead_title[0].upper() + lead_title[1:] if lead_title else lead_title
            time_str = ts_to_pdt(lead_ts)
            is_hot = (now - lead_ts) <= THIRTY_MIN
            hot_dot = '<span class="new-dot" title="Published in the last 30 minutes">&#9679;</span> ' if is_hot else ''
            sources_list = [get_friendly_source(it[2]) for it in cluster]
            n_sources = len(sources_list)
            sources_str = ", ".join(sources_list)
            lead_friendly = get_friendly_source(lead_source)
            cluster_id = "cl-" + hashlib.md5(lead_link.encode()).hexdigest()[:8]
            out += (
                f'<div id="{cluster_id}-anchor" class="cluster" data-ts="{int(lead_ts)}">'
                f'<div class="cluster-header">'
                f'{hot_dot}'
                f'<span class="cluster-badge">{n_sources} sources</span>'
                f'<button class="cluster-toggle-btn" data-target="{cluster_id}" aria-label="Expand story coverage" title="Show/hide all coverage">&#9654; Show all coverage</button>'
                f'</div>\n'
                f'<div class="cluster-lead">'
                f'<span class="title">{display_title}</span>'
                f' <span class="ts-label">{time_str}</span>'
                f' <span class="src-label">\u2014 {lead_friendly}</span>'
                f' <a class="link" href="{lead_link}" target="_blank">[Full Article]</a>'
                f'</div>\n'
                f'<div id="{cluster_id}" class="cluster-items-wrap collapsed">\n'
                f'<div class="cluster-sources-line">{sources_str}</div>\n'
            )
            for ts, title, source, link in cluster:
                friendly = get_friendly_source(source)
                ts_str = ts_to_pdt(ts)
                dtitle = title[0].upper() + title[1:] if title else title
                out += (
                    f'<div class="cluster-item" data-link="{link}">'
                    f'<span class="title">{dtitle}</span>'
                    f' <span class="ts-label">{ts_str}</span>'
                    f' <span class="src-label">\u2014 {friendly}</span>'
                    f' <a class="link" href="{link}" target="_blank">[Full Article]</a>'
                    f'</div>\n'
                )
            out += '</div>\n'  # close cluster-items-wrap
            out += '</div>\n'  # close cluster
    return out

# ====================== SOURCE COUNT SUMMARY ======================
def source_summary(items):
    sources = set(get_friendly_source(it[2]) for it in items)
    return f'<p class="src-summary">{len(items)} headlines \u00b7 {len(sources)} sources</p>\n'

# ====================== TOP STORIES STRIP ======================
def build_top_stories(max_stories=10):
    """Pull the top multi-source clusters across all sections for the pinned strip."""
    all_section_items = [
        ("US",          us_breaking + us_recent),
        ("Middle East", middle_breaking + middle_recent),
        ("World",       world_breaking + world_recent),
        ("Tech",        tech_breaking + tech_recent),
        ("Business",    business_breaking + business_recent),
        ("Sports",      sports_breaking + sports_recent),
        ("Culture",     culture_breaking + culture_recent),
    ]
    top = []
    for section_label, items in all_section_items:
        clusters = cluster_items(items, min_shared=3)
        multi = [cl for cl in clusters if len(cl) >= 2]
        for cl in multi:
            cl.sort(key=lambda x: x[0], reverse=True)
            top.append((len(cl), cl[0][0], section_label, cl))
    top.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return top[:max_stories]

top_stories = build_top_stories()

# ====================== TRENDING TOPICS ======================
def build_trending_topics(max_topics=10):
    """Count keyword frequency across all sections to surface trending topics."""
    all_items = (
        us_breaking + us_recent +
        middle_breaking + middle_recent +
        world_breaking + world_recent +
        tech_breaking + tech_recent +
        business_breaking + business_recent +
        sports_breaking + sports_recent +
        culture_breaking + culture_recent
    )
    word_counts = defaultdict(int)
    skip = {
        "a","an","the","and","or","but","in","on","at","to","for","of","with",
        "by","from","as","is","was","are","were","be","been","have","has","had",
        "do","does","did","will","would","could","should","may","might","its",
        "it","this","that","these","those","says","said","after","over","into",
        "about","up","out","than","then","new","just","more","also","amid",
        "report","reports","under","after","amid","amid","amid","amid","amid",
        "how","why","what","who","when","where","amid","amid","now","amid",
        "amid","amid","amid","amid","amid","amid","amid","amid","amid","amid",
        "not","his","her","their","our","your","its","him","them","us","we",
        "he","she","they","amid","amid","amid","amid","amid","amid","amid",
    }
    for ts, title, source, link in all_items:
        words = re.findall(r'[a-zA-Z]{4,}', title.lower())
        for w in words:
            if w not in skip:
                word_counts[w] += 1
    # Only keep words that appear in 3+ headlines
    trending = [(count, word) for word, count in word_counts.items() if count >= 3]
    trending.sort(reverse=True)
    return trending[:max_topics]

trending_topics = build_trending_topics()

# ====================== BUILD HTML ======================
# Collect all timestamps across ALL items for the breaking-news banner check
all_items_flat = (
    us_breaking + us_recent +
    middle_breaking + middle_recent +
    world_breaking + world_recent +
    business_breaking + business_recent +
    sports_breaking + sports_recent +
    tech_breaking + tech_recent +
    culture_breaking + culture_recent
)
ONE_HOUR = 3600
BANNER_WINDOW = 45 * 60  # 45-minute window for breaking news banner
hot_items = sorted(
    [it for it in all_items_flat if (time.time() - it[0]) <= BANNER_WINDOW],
    key=lambda x: x[0], reverse=True
)
show_breaking_banner = len(hot_items) > 0

update_time = (datetime.utcnow() + PDT_OFFSET).strftime("%I:%M:%S %p PDT")

# Section color map for nav bar accents
SECTION_COLORS = {
    "us":       "#B30000",
    "mideast":  "#C05000",
    "world":    "#2E7D9A",
    "tech":     "#005F9E",
    "business": "#8B6914",
    "sports":   "#006B3C",
    "culture":  "#6B006B",
}

html_parts = []
html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Mitchell Post</title>
    <link rel="alternate" type="application/rss+xml" title="The Mitchell Post RSS Feed" href="feed.xml">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='8' fill='%23121212'/><rect x='2' y='2' width='60' height='60' rx='7' fill='none' stroke='%23B30000' stroke-width='3'/><text x='32' y='46' font-family='Arial,sans-serif' font-size='28' font-weight='bold' fill='%23FFFFFF' text-anchor='middle'>MP</text></svg>">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
    /* ── Reset & base ── */
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: #121212; color: #FFFFFF; font-family: Arial, sans-serif; line-height: 1.6;
            padding-top: 48px; font-size: 15px; }}
    body.large-text {{ font-size: 19px; }}

    /* ── Sticky nav bar ── */
    .sticky-nav {{
        position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
        background: #0A0A0A; border-bottom: 2px solid #B30000;
        display: flex; align-items: center; gap: 0; height: 48px;
        padding: 0 16px; overflow-x: auto; white-space: nowrap;
    }}
    .sticky-nav .site-name {{
        font-size: 1em; font-weight: bold; color: #FFFFFF;
        margin-right: 20px; flex-shrink: 0; letter-spacing: 0.03em;
    }}
    .sticky-nav a {{
        display: inline-block; padding: 0 14px; height: 48px; line-height: 48px;
        color: #cccccc; text-decoration: none; font-size: 0.82em;
        font-weight: bold; letter-spacing: 0.05em; text-transform: uppercase;
        border-left: 3px solid transparent; transition: color 0.15s, border-color 0.15s;
        flex-shrink: 0;
    }}
    .sticky-nav a:hover {{ color: #FFFFFF; }}
    .sticky-nav a.nav-active {{ color: #FFFFFF; background: rgba(255,255,255,0.06); }}
    .sticky-nav a.nav-us     {{ border-left-color: {SECTION_COLORS["us"]}; }}
    .sticky-nav a.nav-mideast{{ border-left-color: {SECTION_COLORS["mideast"]}; }}
    .sticky-nav a.nav-world  {{ border-left-color: {SECTION_COLORS["world"]}; }}
    .sticky-nav a.nav-tech   {{ border-left-color: {SECTION_COLORS["tech"]}; }}
    .sticky-nav a.nav-business{{ border-left-color: {SECTION_COLORS["business"]}; }}
    .sticky-nav a.nav-sports {{ border-left-color: {SECTION_COLORS["sports"]}; }}
    .sticky-nav a.nav-culture{{ border-left-color: {SECTION_COLORS["culture"]}; }}

    /* ── Breaking news banner (rotating) ── */
    .breaking-banner {{
        background: #B30000; color: #FFFFFF;
        padding: 9px 16px; font-size: 0.88em; font-weight: bold;
        display: flex; align-items: center; gap: 10px; flex-wrap: nowrap;
        animation: pulse-bg 3s ease-in-out infinite alternate;
        overflow: hidden;
    }}
    .breaking-banner .bb-label {{
        background: #FFFFFF; color: #B30000;
        padding: 2px 8px; border-radius: 3px; font-size: 0.76em;
        letter-spacing: 0.08em; flex-shrink: 0;
    }}
    .breaking-banner .bb-text {{
        flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        animation: slidein 0.4s ease;
    }}
    .breaking-banner .bb-time {{
        display: none;
    }}
    .breaking-banner .bb-counter {{
        font-size: 0.72em; opacity: 0.6; flex-shrink: 0;
    }}
    @keyframes pulse-bg {{
        from {{ background: #B30000; }}
        to   {{ background: #8a0000; }}
    }}
    @keyframes slidein {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ── Video banner — desktop only ── */
    .banner {{ background: #001B47; width: 100%; position: relative; overflow: hidden; }}
    /* Desktop: 2 rows of 4 in a CSS grid */
    .video-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-template-rows: repeat(2, auto);
        gap: 8px;
        padding: 10px;
    }}
    .youtube-inset {{ border-radius: 4px; overflow: hidden; aspect-ratio: 16/9; width: 100%; }}
    .youtube-inset iframe {{ width: 100%; height: 100%; border: none; display: block; }}

    /* ── Section titles and layout ── */
    .section-title {{
        font-size: 1.6em; margin: 0 0 6px; font-weight: bold;
        text-decoration: underline; text-decoration-thickness: 2px;
    }}
    .section-title.us-color     {{ color: {SECTION_COLORS["us"]};       text-decoration-color: {SECTION_COLORS["us"]}; }}
    .section-title.mideast-color{{ color: {SECTION_COLORS["mideast"]};  text-decoration-color: {SECTION_COLORS["mideast"]}; }}
    .section-title.world-color  {{ color: {SECTION_COLORS["world"]};    text-decoration-color: {SECTION_COLORS["world"]}; }}
    .section-title.tech-color   {{ color: {SECTION_COLORS["tech"]};     text-decoration-color: {SECTION_COLORS["tech"]}; }}
    .section-title.business-color{{ color: {SECTION_COLORS["business"]}; text-decoration-color: {SECTION_COLORS["business"]}; }}
    .section-title.sports-color {{ color: {SECTION_COLORS["sports"]};   text-decoration-color: {SECTION_COLORS["sports"]}; }}
    .section-title.culture-color{{ color: {SECTION_COLORS["culture"]};  text-decoration-color: {SECTION_COLORS["culture"]}; }}

    .top-divider {{ border: 0; height: 3px; background: #222222; margin: 28px 0; }}
    .src-summary {{ color: #666666; font-size: 0.78em; margin-bottom: 12px; }}

    /* ── Headlines ── */
    .headline {{
        margin-bottom: 14px; padding-bottom: 10px;
        border-bottom: 1px solid #222222; line-height: 1.5;
    }}
    .headline.seen-item {{ opacity: 0.55; }}
    .title {{ color: #FFFFFF; font-size: 1em; }}
    .ts-label {{ color: #888888; font-size: 0.78em; margin-left: 4px; }}
    .src-label {{ color: #666666; font-size: 0.88em; }}
    .new-dot {{ color: #FFFFFF; font-size: 0.55em; vertical-align: middle; margin-right: 2px; }}

    /* ── Story clusters ── */
    .cluster {{
        margin-bottom: 16px; padding: 10px 12px 4px 12px;
        border-left: 3px solid #444; border-bottom: 1px solid #222222;
        background: #1a1a1a;
    }}
    .cluster-header {{ margin-bottom: 6px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
    .cluster-badge {{
        background: #333; color: #cccccc; font-size: 0.72em;
        padding: 2px 7px; border-radius: 10px; font-weight: bold;
        letter-spacing: 0.04em; flex-shrink: 0;
    }}
    .cluster-sources {{ color: #555555; font-size: 0.75em; }}
    .cluster-item {{
        margin-bottom: 8px; padding-bottom: 8px;
        border-bottom: 1px solid #262626; line-height: 1.5;
    }}
    .cluster-item:last-child {{ border-bottom: none; margin-bottom: 0; }}
    .cluster-item.seen-item {{ opacity: 0.55; }}

    /* ── Full Article link ── */
    .link {{
        color: #545454; text-decoration: underline;
        font-size: 0.85em; margin-left: 6px;
        display: inline-block; padding: 0;
    }}
    .link:hover {{ color: #FFFFFF; }}

    /* ── Layout containers ── */
    .container {{ display: flex; flex-wrap: wrap; gap: 30px; max-width: 1400px; margin: 0 auto; padding: 0 20px; align-items: flex-start; }}
    .column {{ flex: 1; min-width: 300px; }}
    .section-wrap {{ padding: 0 0 10px 0; }}

    /* ── Per-section cluster tint colors ── */
    #section-us       .cluster {{ border-left-color: #4a0000; background: #1a0505; }}
    #section-mideast  .cluster {{ border-left-color: #4a2000; background: #1a0d00; }}
    #section-world    .cluster {{ border-left-color: #0d3040; background: #051218; }}
    #section-tech     .cluster {{ border-left-color: #002040; background: #060f1a; }}
    #section-business .cluster {{ border-left-color: #3d2d00; background: #191100; }}
    #section-sports   .cluster {{ border-left-color: #002a18; background: #04120a; }}
    #section-culture  .cluster {{ border-left-color: #300030; background: #120512; }}
    /* ── Light mode overrides ── */
    body.light-mode {{
        background: #FFFFFF !important;
        color: #000000 !important;
    }}
    body.light-mode .sticky-nav {{
        background: #F0F0F0 !important;
        border-bottom-color: #B30000 !important;
    }}
    body.light-mode .sticky-nav .site-name {{ color: #000000 !important; }}
    body.light-mode .sticky-nav a {{ color: #333333 !important; }}
    body.light-mode .sticky-nav a:hover {{ color: #000000 !important; }}
    body.light-mode .breaking-banner {{ background: #B30000 !important; }}
    body.light-mode .banner {{ background: #D8E4F0 !important; }}
    body.light-mode .title {{ color: #000000 !important; }}
    body.light-mode .ts-label {{ color: #555555 !important; }}
    body.light-mode .src-label {{ color: #444444 !important; }}
    body.light-mode .link {{ color: #333333 !important; }}
    body.light-mode .link:hover {{ color: #000000 !important; }}
    body.light-mode .top-divider {{ background: #CCCCCC !important; }}
    body.light-mode .src-summary {{ color: #555555 !important; }}
    body.light-mode .headline {{ border-bottom-color: #CCCCCC !important; }}
    body.light-mode .cluster {{
        background: #F5F5F5 !important;
        border-left-color: #999999 !important;
    }}
    body.light-mode .cluster-item {{ border-bottom-color: #DDDDDD !important; }}
    body.light-mode .cluster-badge {{ background: #DDDDDD !important; color: #000000 !important; }}
    body.light-mode .cluster-sources {{ color: #555555 !important; }}
    body.light-mode .top-story-card {{ background: #F0F0F0 !important; }}
    body.light-mode .top-stories-title {{ color: #444444 !important; border-bottom-color: #CCCCCC !important; }}
    body.light-mode .ts-headline {{ color: #000000 !important; }}
    body.light-mode .ts-link {{ color: #333333 !important; }}
    body.light-mode .ts-link:hover {{ color: #000000 !important; }}
    body.light-mode .ts-badge {{ background: #DDDDDD !important; color: #000000 !important; }}
    body.light-mode .site-footer {{
        background: #EEEEEE !important;
        border-top-color: #CCCCCC !important;
        color: #333333 !important;
    }}
    body.light-mode .site-footer h1 {{ color: #888888 !important; }}
    body.light-mode .site-footer .byline {{ color: #555555 !important; }}
    body.light-mode .site-footer .update {{ color: #777777 !important; }}
    body.light-mode #section-us       .cluster {{ border-left-color: #B30000 !important; background: #FFF0F0 !important; }}
    body.light-mode #section-mideast  .cluster {{ border-left-color: #C05000 !important; background: #FFF5EE !important; }}
    body.light-mode #section-tech     .cluster {{ border-left-color: #005F9E !important; background: #EEF4FB !important; }}
    body.light-mode #section-business .cluster {{ border-left-color: #8B6914 !important; background: #FBF8EE !important; }}
    body.light-mode #section-sports   .cluster {{ border-left-color: #006B3C !important; background: #EEF8F3 !important; }}
    body.light-mode #section-culture  .cluster {{ border-left-color: #6B006B !important; background: #F8EEF8 !important; }}
    body.light-mode .search-bar-wrap {{ background: #EEEEEE !important; border-color: #CCCCCC !important; }}
    body.light-mode .search-bar-wrap input {{
        background: #FFFFFF !important; color: #000000 !important;
        border-color: #AAAAAA !important;
    }}
    body.light-mode .search-bar-wrap input::placeholder {{ color: #888888 !important; }}
    body.light-mode .search-bar-wrap button {{
        background: #B30000 !important; color: #FFFFFF !important;
    }}

    /* ── Light mode toggle slider ── */
    .light-toggle-wrap {{
        display: flex; align-items: center; gap: 7px;
        margin-left: auto; flex-shrink: 0; padding-left: 16px;
    }}
    .light-toggle-label {{
        font-size: 0.72em; color: #aaaaaa; letter-spacing: 0.04em;
        text-transform: uppercase; user-select: none; white-space: nowrap;
    }}
    body.light-mode .light-toggle-label {{ color: #444444; }}
    .toggle-switch {{ position: relative; display: inline-block; width: 36px; height: 20px; flex-shrink: 0; }}
    .toggle-switch input {{ opacity: 0; width: 0; height: 0; }}
    .toggle-slider {{
        position: absolute; cursor: pointer; inset: 0;
        background: #333; border-radius: 20px; transition: background 0.2s;
    }}
    .toggle-slider:before {{
        content: ""; position: absolute;
        width: 14px; height: 14px; border-radius: 50%;
        left: 3px; top: 3px;
        background: #aaaaaa; transition: transform 0.2s, background 0.2s;
    }}
    .toggle-switch input:checked + .toggle-slider {{ background: #dddddd; }}
    .toggle-switch input:checked + .toggle-slider:before {{
        transform: translateX(16px); background: #000000;
    }}

    /* ── Search bar ── */
    .search-bar-wrap {{
        max-width: 1400px; margin: 0 auto 18px auto; padding: 12px 20px;
        background: #1a1a1a; border-top: 1px solid #2a2a2a;
        border-bottom: 1px solid #2a2a2a;
        display: flex; align-items: center; gap: 10px;
    }}
    .search-bar-wrap input {{
        flex: 1; padding: 8px 14px; border-radius: 4px;
        border: 1px solid #444; background: #121212; color: #FFFFFF;
        font-size: 0.95em; outline: none;
        transition: border-color 0.15s;
    }}
    .search-bar-wrap input:focus {{ border-color: #B30000; }}
    .search-bar-wrap input::placeholder {{ color: #666; }}
    .search-bar-wrap button {{
        padding: 8px 18px; border-radius: 4px; border: none;
        background: #B30000; color: #FFFFFF; font-size: 0.9em;
        font-weight: bold; cursor: pointer; letter-spacing: 0.04em;
        transition: background 0.15s; white-space: nowrap;
    }}
    .search-bar-wrap button:hover {{ background: #8a0000; }}

    /* ── Site footer ── */
    .site-footer {{
        margin-top: 50px; padding: 30px 20px 50px 20px;
        border-top: 2px solid #222222; text-align: center;
        background: #0d0d0d; color: #555;
    }}
    .site-footer h1 {{ font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.08em; color: #555; margin-bottom: 4px; }}
    .site-footer .byline {{ font-size: 0.85em; color: #666; display: block; margin-bottom: 4px; }}
    .site-footer .update {{ font-size: 0.78em; color: #444; display: block; }}

    /* ── Back to Top button ── */
    .back-to-top-btn {{
        display: block; margin: 32px auto 0 auto;
        background: none; border: 2px solid #B30000;
        color: #FFFFFF; font-size: 2em; font-weight: bold;
        letter-spacing: 0.06em; padding: 18px 48px;
        border-radius: 6px; cursor: pointer;
        transition: background 0.18s, color 0.18s;
        text-transform: uppercase;
    }}
    .back-to-top-btn:hover {{ background: #B30000; color: #fff; }}
    body.light-mode .back-to-top-btn {{ color: #000; border-color: #B30000; }}
    body.light-mode .back-to-top-btn:hover {{ background: #B30000; color: #fff; }}

    /* ── Top Stories strip ── */
    .top-stories-strip {{
        max-width: 1400px; margin: 0 auto 20px auto; padding: 0 20px;
    }}
    .top-stories-title {{
        font-size: 0.72em; font-weight: bold; letter-spacing: 0.1em;
        text-transform: uppercase; color: #888888; margin-bottom: 10px;
        padding-bottom: 4px; border-bottom: 1px solid #2a2a2a;
    }}
    .top-story-card {{
        background: #1a0505; border-left: 3px solid #B30000;
        padding: 10px 14px; margin-bottom: 8px; border-radius: 2px;
    }}
    .top-story-card .ts-section-tag {{
        font-size: 0.68em; font-weight: bold; letter-spacing: 0.08em;
        text-transform: uppercase; margin-right: 8px;
        padding: 1px 6px; border-radius: 8px; display: inline-block;
    }}
    .ts-section-us      {{ background: #4a0000; color: #ffaaaa; }}
    .ts-section-mideast {{ background: #4a2000; color: #ffcc99; }}
    .ts-section-world   {{ background: #0d3040; color: #99ccee; }}
    .ts-section-tech    {{ background: #002040; color: #99bbdd; }}
    .ts-section-business{{ background: #3d2d00; color: #ddcc88; }}
    .ts-section-sports  {{ background: #002a18; color: #88ddaa; }}
    .ts-section-culture {{ background: #300030; color: #ddaadd; }}
    .top-story-card .ts-badge {{
        background: #333; color: #ccc; font-size: 0.68em;
        padding: 1px 6px; border-radius: 8px; margin-right: 8px;
    }}
    .top-story-card .ts-headline {{ color: #FFFFFF; font-size: 0.95em; }}
    .top-story-card .ts-link {{ color: #545454; text-decoration: underline; font-size: 0.8em; margin-left: 6px; }}
    .top-story-card .ts-link:hover {{ color: #FFFFFF; }}

    /* ── Section collapse ── */
    .section-collapse-btn {{
        background: none; border: none; cursor: pointer;
        color: inherit; font-size: 1em; padding: 0 0 0 8px;
        line-height: 1; opacity: 0.6; transition: opacity 0.15s;
        vertical-align: middle; flex-shrink: 0;
    }}
    .section-collapse-btn:hover {{ opacity: 1; }}
    .section-title-row {{ display: flex; align-items: center; margin-bottom: 6px; }}
    .section-title-row .section-title {{ margin-bottom: 0; }}
    .section-columns {{ transition: none; }}
    .section-columns.collapsed {{ display: none; }}

    /* ── Mobile overrides ── */
    @media (max-width: 900px) {{
        /* Hide video section entirely — don't even load layout space */
        .banner {{ display: none !important; }}

        body {{ padding-top: 48px; font-size: 16px; }}

        .sticky-nav {{ gap: 0; padding: 0 8px; }}
        .sticky-nav .site-name {{ font-size: 0.85em; margin-right: 10px; }}
        .sticky-nav a {{ padding: 0 10px; font-size: 0.72em; }}

        .container {{ flex-direction: column; gap: 0; padding: 0 14px; }}
        .column {{ min-width: 0; width: 100%; }}

        /* Larger tap targets for headlines */
        .headline, .cluster-item {{
            padding-bottom: 14px;
            margin-bottom: 16px;
        }}
        .title {{ font-size: 1.05em; line-height: 1.55; }}

        /* Full Article button — large, easy to tap */
        .link {{
            display: inline-block;
            margin-top: 6px;
            margin-left: 0;
            padding: 6px 12px;
            background: #1e1e1e;
            border: 1px solid #333;
            border-radius: 4px;
            font-size: 0.9em;
            color: #aaaaaa;
        }}
        .link:hover, .link:active {{ background: #2a2a2a; color: #FFFFFF; }}

        .ts-label {{ font-size: 0.82em; }}
        .src-summary {{ font-size: 0.82em; }}
        .bb-counter {{ display: none !important; }}
        .section-title {{ font-size: 1.3em; }}
        .top-divider {{ margin: 18px 0; }}

        /* Cluster cards on mobile */
        .cluster {{ padding: 8px 10px 4px 10px; }}
        .cluster-badge {{ font-size: 0.78em; }}
        /* Light mode Full Article button on mobile */
        body.light-mode .link {{
            background: #eeeeee !important;
            border-color: #999999 !important;
            color: #000000 !important;
        }}
        body.light-mode .link:hover, body.light-mode .link:active {{
            background: #cccccc !important;
            color: #000000 !important;
        }}
    }}
    /* ── Floating light/dark toggle for mobile ── */
    .float-mode-btn {{
        display: none;
        position: fixed; bottom: 20px; right: 16px; z-index: 2000;
        background: #222; color: #fff; border: 1px solid #444;
        border-radius: 50px; padding: 8px 14px;
        font-size: 0.78em; font-weight: bold; letter-spacing: 0.04em;
        cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        transition: background 0.2s, color 0.2s;
        user-select: none;
    }}
    body.light-mode .float-mode-btn {{
        background: #eeeeee; color: #000000; border-color: #bbbbbb;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    @media (max-width: 900px) {{
        .float-mode-btn {{ display: block; }}
    }}

    /* ── Print stylesheet ── */
    @media print {{
        .sticky-nav, .banner, .breaking-banner,
        .top-stories-strip, .section-collapse-btn, .link,
        .site-footer .update, script {{ display: none !important; }}
        body {{ background: #FFFFFF !important; color: #000000 !important;
                font-size: 11pt; padding-top: 0 !important; }}
        .container {{ display: block !important; }}
        .column {{ width: 100% !important; }}
        .headline, .cluster {{ border-color: #cccccc !important; background: none !important; }}
        .title {{ color: #000000 !important; font-size: 10pt; }}
        .ts-label, .src-label {{ color: #444444 !important; }}
        .section-title {{ color: #000000 !important; border-bottom: 1pt solid #000; }}
        .cluster {{ border-left-color: #000 !important; }}
        .cluster-badge {{ background: #eee !important; color: #000 !important; }}
        a {{ color: #000000 !important; text-decoration: none !important; }}
        .site-footer {{ border-top: 1pt solid #000 !important;
                        background: none !important; color: #000 !important; }}
        .site-footer h1 {{ color: #000000 !important; }}
        .section-columns.collapsed {{ display: block !important; }}
    }}

    /* ── Cluster collapsible toggle ── */
    .cluster-lead {{ margin-bottom: 6px; }}
    .cluster-items-wrap {{ transition: none; }}
    .cluster-items-wrap.collapsed {{ display: none; }}
    .cluster-toggle-btn {{
        background: none; border: 1px solid #444; border-radius: 10px;
        color: #888; font-size: 0.7em; padding: 2px 8px; cursor: pointer;
        letter-spacing: 0.03em; transition: color 0.15s, border-color 0.15s;
        margin-left: 4px; flex-shrink: 0;
    }}
    .cluster-toggle-btn:hover {{ color: #fff; border-color: #888; }}
    .cluster-toggle-btn.open {{ color: #ccc; border-color: #666; }}
    .cluster-sources-line {{
        color: #555; font-size: 0.73em; margin-bottom: 6px;
        padding-bottom: 4px; border-bottom: 1px solid #252525;
    }}
    body.light-mode .cluster-toggle-btn {{ color: #555; border-color: #aaa; }}
    body.light-mode .cluster-toggle-btn:hover {{ color: #000; border-color: #555; }}
    body.light-mode .cluster-sources-line {{ color: #777; border-bottom-color: #ddd; }}

    /* ── Breaking banner upgrade ── */
    .bb-close {{ display: none; }}
    .bb-section-pill {{
        font-size: 0.7em; font-weight: bold; letter-spacing: 0.07em;
        text-transform: uppercase; padding: 2px 7px; border-radius: 3px;
        flex-shrink: 0; margin-left: 4px;
    }}
    @media (max-width: 900px) {{
        .bb-section-pill {{ display: none !important; }}
    }}

    /* ── Updated-ago in nav ── */
    .nav-updated-ago {{
        font-size: 0.65em; color: #666; margin-right: 10px;
        white-space: nowrap; flex-shrink: 0; letter-spacing: 0.02em;
    }}
    body.light-mode .nav-updated-ago {{ color: #999; }}

    /* ── Top Stories 2-column layout ── */
    .top-stories-2col {{
        display: flex; gap: 0; align-items: stretch; width: 100%;
    }}
    .ts-col {{ flex: 1; min-width: 0; padding: 0 24px 0 0; }}
    .ts-divider-left {{ border-left: 1px solid #2a2a2a; padding-left: 24px; padding-right: 0; }}
    body.light-mode .ts-divider-left {{ border-left-color: #ddd; }}
    @media (max-width: 900px) {{
        .top-stories-2col {{ flex-direction: column; }}
        .ts-divider-left {{ border-left: none; border-top: 1px solid #2a2a2a; padding-left: 0; padding-top: 14px; margin-top: 14px; }}
        body.light-mode .ts-divider-left {{ border-top-color: #ddd; }}
    }}

    /* ── MRO jump-to-story label ── */
    .mro-jump {{
        color: #545454; font-size: 0.78em; margin-left: 6px;
        text-decoration: underline; cursor: pointer;
        transition: color 0.15s;
    }}
    .mro-card:hover .mro-jump {{ color: #FFFFFF; }}
    body.light-mode .mro-jump {{ color: #888; }}
    body.light-mode .mro-card:hover .mro-jump {{ color: #000; }}

    /* ── Daily Briefing card accent ── */
    .db-card {{ border-left-color: #005F9E !important; }}

    /* ── Trending Topics ── */
    .trend-tags-wrap {{ display: flex; flex-wrap: wrap; gap: 8px; padding-top: 4px; }}
    .trend-tag {{
        display: inline-flex; align-items: center; gap: 6px;
        border: 1px solid #444; border-radius: 20px;
        padding: 4px 12px; text-decoration: none;
        transition: background 0.15s, border-color 0.15s;
        background: #1a1a1a;
    }}
    .trend-tag:hover {{ background: #252525; }}
    .trend-word {{ color: #ddd; font-size: 0.82em; font-weight: bold; letter-spacing: 0.02em; }}
    .trend-count {{
        background: #333; color: #999; font-size: 0.68em;
        padding: 1px 6px; border-radius: 8px; font-weight: bold;
    }}
    body.light-mode .trend-tag {{ background: #f0f0f0; border-color: #ccc; }}
    body.light-mode .trend-tag:hover {{ background: #e4e4e4; }}
    body.light-mode .trend-word {{ color: #222; }}
    body.light-mode .trend-count {{ background: #ddd; color: #444; }}

    /* ── Search bar on-page results ── */
    .headline.search-hidden, .cluster.search-hidden {{ display: none !important; }}
    .headline.search-match {{ outline: 1px solid #B30000; }}

    /* ── Footer additions ── */
    .site-footer .mission {{
        font-size: 0.82em; color: #666; display: block;
        margin-bottom: 8px; max-width: 600px; margin-left: auto; margin-right: auto;
    }}
    body.light-mode .site-footer .mission {{ color: #777; }}
    .homepage-wrap {{ margin-top: 22px; }}
    .set-homepage-btn {{
        background: none; border: 1px solid #333; border-radius: 20px;
        color: #666; font-size: 0.78em; padding: 6px 16px; cursor: pointer;
        transition: border-color 0.15s, color 0.15s; letter-spacing: 0.03em;
    }}
    .set-homepage-btn:hover {{ border-color: #888; color: #ccc; }}
    body.light-mode .set-homepage-btn {{ border-color: #ccc; color: #888; }}
    body.light-mode .set-homepage-btn:hover {{ border-color: #888; color: #333; }}
    .homepage-instructions {{
        margin-top: 14px; padding: 14px 18px;
        background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 6px;
        font-size: 0.8em; color: #888; line-height: 1.9; text-align: left;
        display: inline-block; max-width: 560px;
    }}
    body.light-mode .homepage-instructions {{ background: #f0f0f0; border-color: #ddd; color: #555; }}
    .homepage-instructions code {{ color: #B30000; font-size: 0.9em; }}
    .hp-browser {{ display: block; }}

    </style>
</head>
<body>

<!-- ══ STICKY NAVIGATION BAR ══ -->
<nav class="sticky-nav">
    <a href="#" class="site-name" aria-label="Back to top">The Mitchell Post</a>
    <a href="#section-us"       class="nav-us">US News</a>
    <a href="#section-mideast"  class="nav-mideast">Middle East</a>
    <a href="#section-world"    class="nav-world">Asia, Europe &amp; World</a>
    <a href="#section-tech"     class="nav-tech">Tech &amp; Life</a>
    <a href="#section-business" class="nav-business">Business</a>
    <a href="#section-sports"   class="nav-sports">Sports</a>
    <a href="#section-culture"  class="nav-culture">Culture</a>
    <div class="light-toggle-wrap">
        <span class="nav-updated-ago" id="nav-updated-ago" title="Time since last update"></span>
        <span class="light-toggle-label">Dark/Light Mode</span>
        <label class="toggle-switch" title="Toggle light/dark mode">
            <input type="checkbox" id="light-mode-toggle">
            <span class="toggle-slider"></span>
        </label>
    </div>
</nav>

<!-- ══ FLOATING LIGHT/DARK TOGGLE (mobile only) ══ -->
<button class="float-mode-btn" id="float-mode-btn" aria-label="Toggle light/dark mode">🌙</button>

""")

# Rotating breaking news banner (all items < 1 hour)
if show_breaking_banner:
    import json as _json_banner
    # Build a quick lookup: link -> section label
    _link_to_section = {}
    for _sec_label, _sec_items in [
        ("US", us_breaking + us_recent),
        ("Middle East", middle_breaking + middle_recent),
        ("World", world_breaking + world_recent),
        ("Tech", tech_breaking + tech_recent),
        ("Business", business_breaking + business_recent),
        ("Sports", sports_breaking + sports_recent),
        ("Culture", culture_breaking + culture_recent),
    ]:
        for _ts, _ttl, _src, _lnk in _sec_items:
            if _lnk not in _link_to_section:
                _link_to_section[_lnk] = _sec_label
    _section_colors_bb = {
        "US": "#B30000", "Middle East": "#C05000", "World": "#2E7D9A",
        "Tech": "#005F9E", "Business": "#8B6914", "Sports": "#006B3C", "Culture": "#6B006B",
    }
    banner_data = [
        {
            "title": it[1][:140].replace('"', '&quot;'),
            "link":  it[3],
            "time":  ts_to_pdt(it[0]),
            "section": _link_to_section.get(it[3], ""),
            "scolor":  _section_colors_bb.get(_link_to_section.get(it[3], ""), "#555"),
        }
        for it in hot_items[:20]
    ]
    banner_json = _json_banner.dumps(banner_data)
    html_parts.append(
        f'<div class="breaking-banner" id="breaking-banner">'
        f'<span class="bb-label">&#9679; BREAKING</span>'
        f'<span class="bb-text" id="bb-text"></span>'
        f'<span class="bb-section-pill" id="bb-section-pill" style="display:none"></span>'
        f'<span class="bb-time" id="bb-time"></span>'
        f'<span class="bb-counter" id="bb-counter"></span>'
        f'<button class="bb-close" id="bb-close" aria-label="Dismiss banner" title="Dismiss">&#10005;</button>'
        f'</div>'
        f'<script>window._bbItems = {banner_json}; window._bbUpdateTs = {int(time.time())};</script>\n'
    )

html_parts.append("")  # Video banner moved below MRO strip — see after search bar

def section_block(section_id, color_class, breaking_items, recent_items,
                  breaking_title, recent_title):
    b_summary = source_summary(breaking_items) if breaking_items else ''
    r_summary = source_summary(recent_items) if recent_items else ''
    b_content = render_column(breaking_items) if breaking_items else '<p style="color:#666">No breaking news in the last 3 hours.</p>\n'
    r_content = render_column(recent_items) if recent_items else '<p style="color:#666">No additional headlines right now.</p>\n'
    return (
        f'<div id="{section_id}" class="section-wrap">\n'
        f'<div class="container">\n'
        f'<div class="column">\n'
        f'<div class="section-title-row">'
        f'<h2 class="section-title {color_class}">{breaking_title}</h2>'
        f'<button class="section-collapse-btn" data-target="{section_id}-cols" aria-label="Collapse section" title="Collapse / expand">&#9660;</button>'
        f'</div>\n'
        f'</div>\n'
        f'</div>\n'
        f'<div id="{section_id}-cols" class="section-columns">\n'
        f'<div class="container">\n'
        f'<div class="column">\n'
        f'{b_summary}'
        f'{b_content}'
        f'</div>\n'
        f'<div class="column">\n'
        f'<div class="section-title-row">'
        f'<h2 class="section-title {color_class}">{recent_title}</h2>'
        f'</div>\n'
        f'{r_summary}'
        f'{r_content}'
        f'</div>\n'
        f'</div>\n'
        f'</div>\n'
        f'</div>\n'
    )

# ── Daily Briefing: top 5 stories by source count ──
def build_daily_briefing(max_items=10):
    """Pick top weighted stories across all sections for a daily briefing digest."""
    all_section_items = [
        ("US",          us_breaking + us_recent),
        ("Middle East", middle_breaking + middle_recent),
        ("World",       world_breaking + world_recent),
        ("Tech",        tech_breaking + tech_recent),
        ("Business",    business_breaking + business_recent),
        ("Sports",      sports_breaking + sports_recent),
        ("Culture",     culture_breaking + culture_recent),
    ]
    scored = []
    for section_label, items in all_section_items:
        clusters = cluster_items(items, min_shared=3)
        for cl in clusters:
            cl.sort(key=lambda x: x[0], reverse=True)
            # weight: source count * recency bonus
            age_hours = (time.time() - cl[0][0]) / 3600
            recency_bonus = max(0, 12 - age_hours) / 12
            score = len(cl) + recency_bonus * 2
            scored.append((score, section_label, cl))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:max_items]

daily_briefing = build_daily_briefing()

# ── Most Reported On strip HTML ──
if top_stories or daily_briefing:
    # Merge top_stories and daily_briefing into a single deduped ranked list of 10
    # top_stories: list of (n_src, lead_ts, section_label, cluster)
    # daily_briefing: list of (score, section_label, cluster)
    seen_headlines = set()
    combined_cards = []

    def _card_entry(section_label, cluster, n_src):
        lead_ts2, lead_title, lead_source, lead_link = cluster[0]
        norm = normalize_title(lead_title)
        return norm, section_label, cluster, n_src, lead_ts2, lead_title, lead_link

    # First pass: top_stories
    for n_src, lead_ts, section_label, cluster in top_stories:
        norm, sl, cl, ns, lts, lt, ll = _card_entry(section_label, cluster, n_src)
        if norm not in seen_headlines:
            seen_headlines.add(norm)
            combined_cards.append((sl, cl, ns, lts, lt, ll))

    # Second pass: daily_briefing (skip already-seen)
    for score, section_label, cluster in daily_briefing:
        norm, sl, cl, ns, lts, lt, ll = _card_entry(section_label, cluster, len(cluster))
        if norm not in seen_headlines:
            seen_headlines.add(norm)
            combined_cards.append((sl, cl, ns, lts, lt, ll))

    # Trim to 10
    combined_cards = combined_cards[:10]

    # Split into two columns of 5
    col1_cards = combined_cards[:5]
    col2_cards = combined_cards[5:10]

    def render_mro_cards(cards):
        html = ''
        section_css_map = {
            "US":          "ts-section-us",
            "Middle East": "ts-section-mideast",
            "World":       "ts-section-world",
            "Tech":        "ts-section-tech",
            "Business":    "ts-section-business",
            "Sports":      "ts-section-sports",
            "Culture":     "ts-section-culture",
        }
        for section_label, cluster, n_src, lead_ts2, lead_title, lead_link in cards:
            safe_title = lead_title.replace('<','&lt;').replace('>','&gt;')
            safe_title = safe_title[0].upper() + safe_title[1:] if safe_title else safe_title
            # Build the same anchor ID used by render_column for this story
            link_hash = hashlib.md5(lead_link.encode()).hexdigest()[:8]
            # Could be a cluster lead (cl-HASH-anchor) or a single headline (hl-HASH)
            # We embed both candidates; JS will find whichever exists
            anchor_cluster = f"cl-{link_hash}-anchor"
            anchor_single  = f"hl-{link_hash}"
            tag_css = section_css_map.get(section_label, "")
            html += (
                f'<div class="top-story-card mro-card" '
                f'data-anchor-cluster="{anchor_cluster}" data-anchor-single="{anchor_single}" '
                f'style="cursor:pointer" title="Jump to story on this page">'
                f'<span class="ts-section-tag {tag_css}">{section_label}</span>'
                f'<span class="ts-badge">{n_src} sources</span>'
                f'<span class="ts-headline">{safe_title}</span>'
                f'<span class="ts-link mro-jump">[↓ Go to story]</span>'
                f'</div>\n'
            )
        return html

    col1_html = render_mro_cards(col1_cards)
    col2_html = render_mro_cards(col2_cards)

    # Build trending topics tags
    trend_tags = ''
    SECTION_TOPIC_COLORS = {
        "iran": "#C05000", "israel": "#C05000", "trump": "#B30000",
        "tariff": "#B30000", "tariffs": "#B30000", "gaza": "#C05000",
    }
    for count, word in trending_topics:
        color = SECTION_TOPIC_COLORS.get(word, "#444")
        trend_tags += (
            f'<a class="trend-tag" href="https://news.google.com/search?q={word}&hl=en-US&gl=US&ceid=US:en" '
            f'target="_blank" style="border-color:{color}">'
            f'<span class="trend-word">{word.title()}</span>'
            f'<span class="trend-count">{count}</span>'
            f'</a>\n'
        )

    ts_html = f'''<div class="top-stories-strip">
  <p class="top-stories-title">Most Reported On</p>
  <div class="top-stories-2col">
    <div class="ts-col">
      {col1_html}
    </div>
    <div class="ts-col ts-divider-left">
      {col2_html}
    </div>
  </div>
</div>\n'''
    ts_html += '''<div class="search-bar-wrap">
    <input type="text" id="news-search-input" placeholder="Search headlines on this page... (Enter for Google News)" aria-label="Search news">
    <button id="news-search-btn">Search</button>
    <span id="search-result-count" style="font-size:0.8em;color:#888;white-space:nowrap;"></span>
</div>\n'''
    ts_html += '''<!-- ══ VIDEO BANNER — desktop only, hidden on mobile via CSS ══ -->
<div class="banner">
    <div class="video-grid">
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/TBlxk1kH9dM?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/Ap-UM1O9RBU?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/LuKwFajn37U?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/gCNeDWCI0vo?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/b_ERc4vcRHI?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/nya02XlHG1Q?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/_6dRRfnYJws?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe data-src="https://www.youtube.com/embed/pykpO5kQJ98?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
    </div>
</div>\n'''
    html_parts.append(ts_html)


# ── Build sections in user-preferred order (default order, JS reorders on page) ──
SECTION_DATA = [
    ("section-us",       "us-color",       us_breaking,       us_recent,       "Breaking US News",                  "Today&#39;s US Headlines"),
    ("section-mideast",  "mideast-color",  middle_breaking,   middle_recent,   "Middle East Breaking News",         "Today&#39;s Middle East Headlines"),
    ("section-world",    "world-color",    world_breaking,    world_recent,    "Asia, Europe &amp; World Breaking", "Today&#39;s Asia, Europe &amp; World Headlines"),
    ("section-tech",     "tech-color",     tech_breaking,     tech_recent,     "Tech &amp; Life Breaking News",     "Today&#39;s Tech &amp; Life Headlines"),
    ("section-business", "business-color", business_breaking, business_recent, "Business Breaking News",            "Today&#39;s Business Headlines"),
    ("section-sports",   "sports-color",   sports_breaking,   sports_recent,   "Sports Breaking News",              "Today&#39;s Sports Headlines"),
    ("section-culture",  "culture-color",  culture_breaking,  culture_recent,  "Culture Breaking News",             "Today&#39;s Culture Headlines"),
]
html_parts.append('<div id="sections-wrapper">\n')
for i, (sid, sc, bi, ri, bt, rt) in enumerate(SECTION_DATA):
    html_parts.append(section_block(sid, sc, bi, ri, bt, rt))
    if i < len(SECTION_DATA) - 1:
        html_parts.append('<hr class="top-divider">\n')
html_parts.append('</div>\n')

html_parts.append("""
<!-- ══ YOUTUBE AUTO-MUTE ══ -->
<script>
// ── YT loader: desktop only, mobile gets zero YouTube requests ──
var players = [];
var IS_MOBILE = window.innerWidth <= 900;

// Load YT API only on desktop — zero network cost on mobile
if (!IS_MOBILE) {
    var ytScript = document.createElement('script');
    ytScript.src = 'https://www.youtube.com/iframe_api';
    document.head.appendChild(ytScript);
}

if (!IS_MOBILE) {
    // Activate iframes by moving data-src -> src
    document.querySelectorAll('.youtube-inset iframe[data-src]').forEach(function(iframe) {
        iframe.src = iframe.getAttribute('data-src');
        iframe.removeAttribute('data-src');
    });
}

function onYouTubeIframeAPIReady() {
    if (IS_MOBILE) return;
    setTimeout(function() {
        document.querySelectorAll('.youtube-inset iframe').forEach(function(iframe) {
            var p = new YT.Player(iframe, {
                events: {
                    onReady: function(e) { e.target.mute(); },
                    onStateChange: function(e) {
                        if (e.data === YT.PlayerState.PLAYING) {
                            players.forEach(function(other) {
                                if (other !== e.target) other.mute();
                            });
                        }
                    }
                }
            });
            players.push(p);
        });
    }, 1200);
}

document.addEventListener('DOMContentLoaded', function() {

// ── MRO CARD SMOOTH SCROLL ──
(function() {
    var NAV_HEIGHT = 56; // sticky nav height + a little breathing room
    document.querySelectorAll('.mro-card').forEach(function(card) {
        card.addEventListener('click', function() {
            var anchorCluster = card.getAttribute('data-anchor-cluster');
            var anchorSingle  = card.getAttribute('data-anchor-single');
            var target = document.getElementById(anchorCluster) || document.getElementById(anchorSingle);
            if (!target) return;
            // If the story is inside a collapsed section, expand it first
            var section = target.closest('.section-columns');
            if (section && section.classList.contains('collapsed')) {
                section.classList.remove('collapsed');
                var btn = document.querySelector('[data-target="' + section.id + '"]');
                if (btn) btn.textContent = '▼';
            }
            // If it's a cluster that's collapsed, expand it
            var clusterItems = target.querySelector('.cluster-items-wrap');
            if (clusterItems && clusterItems.classList.contains('collapsed')) {
                clusterItems.classList.remove('collapsed');
                var toggleBtn = target.querySelector('.cluster-toggle-btn');
                if (toggleBtn) { toggleBtn.textContent = '▲ Hide coverage'; toggleBtn.classList.add('open'); }
            }
            var top = target.getBoundingClientRect().top + window.pageYOffset - NAV_HEIGHT;
            window.scrollTo({ top: top, behavior: 'smooth' });
            // Brief highlight flash
            target.style.transition = 'outline 0s';
            target.style.outline = '2px solid #B30000';
            setTimeout(function() {
                target.style.transition = 'outline 0.8s';
                target.style.outline = 'none';
            }, 1200);
        });
    });
})();


(function() {
    var LKEY = 'mp_light_mode';
    var toggle = document.getElementById('light-mode-toggle');
    var floatBtn = document.getElementById('float-mode-btn');
    if (!toggle) return;
    function setMode(on) {
        if (on) { document.body.classList.add('light-mode'); toggle.checked = true; }
        else     { document.body.classList.remove('light-mode'); toggle.checked = false; }
        var iconLabel = document.getElementById('mode-icon-label');
        if (iconLabel) iconLabel.textContent = on ? '💡' : '🌙';
        if (floatBtn) floatBtn.textContent = on ? '💡' : '🌙';
        try { localStorage.setItem(LKEY, on ? '1' : '0'); } catch(e) {}
    }
    // Restore preference
    var saved = null;
    try { saved = localStorage.getItem(LKEY); } catch(e) {}
    if (saved === '1') setMode(true);
    toggle.addEventListener('change', function() { setMode(toggle.checked); });
    if (floatBtn) floatBtn.addEventListener('click', function() { setMode(!document.body.classList.contains('light-mode')); });
})();

// ── NEWS SEARCH BAR — two-tier: live filter first, Google News fallback ──
(function() {
    var input = document.getElementById('news-search-input');
    var btn   = document.getElementById('news-search-btn');
    var countEl = document.getElementById('search-result-count');
    if (!input || !btn) return;

    var allHeadlines = Array.from(document.querySelectorAll('.headline, .cluster'));

    function clearFilter() {
        allHeadlines.forEach(function(el) {
            el.classList.remove('search-hidden', 'search-match');
        });
        if (countEl) countEl.textContent = '';
    }

    function liveFilter(q) {
        if (!q) { clearFilter(); return; }
        var lower = q.toLowerCase();
        var matches = 0;
        var firstMatch = null;
        allHeadlines.forEach(function(el) {
            var text = (el.textContent || '').toLowerCase();
            if (text.indexOf(lower) !== -1) {
                el.classList.remove('search-hidden');
                el.classList.add('search-match');
                if (!firstMatch) firstMatch = el;
                matches++;
            } else {
                el.classList.add('search-hidden');
                el.classList.remove('search-match');
            }
        });
        // Expand any collapsed sections that contain matches
        document.querySelectorAll('.search-match').forEach(function(el) {
            var section = el.closest('.section-columns');
            if (section && section.classList.contains('collapsed')) {
                section.classList.remove('collapsed');
                var btn = document.querySelector('[data-target="' + section.id + '"]');
                if (btn) btn.innerHTML = '&#9660;';
            }
        });
        // Scroll to first match
        if (firstMatch) {
            var NAV_H = 64;
            var top = firstMatch.getBoundingClientRect().top + window.pageYOffset - NAV_H;
            window.scrollTo({ top: top, behavior: 'smooth' });
        }
        if (countEl) {
            if (matches > 0) {
                countEl.textContent = matches + ' match' + (matches !== 1 ? 'es' : '') + ' on this page';
                countEl.style.color = '#aaa';
                countEl.style.cursor = 'default';
                countEl.onclick = null;
            } else {
                countEl.textContent = 'No matches \u2014 try Google News \u2192';
                countEl.style.color = '#B30000';
                countEl.style.cursor = 'pointer';
                countEl.onclick = function() {
                    window.open('https://news.google.com/search?q=' + encodeURIComponent(input.value.trim()) + '&hl=en-US&gl=US&ceid=US:en', '_blank');
                };
            }
        }
    }

    function googleFallback() {
        var q = input.value.trim();
        if (!q) return;
        window.open('https://news.google.com/search?q=' + encodeURIComponent(q) + '&hl=en-US&gl=US&ceid=US:en', '_blank');
    }

    var debounceTimer = null;
    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function() { liveFilter(input.value.trim()); }, 180);
    });

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            var q = input.value.trim();
            // If there are live matches, Enter just keeps filter; if none, go to Google News
            var matches = document.querySelectorAll('.search-match').length;
            if (matches === 0 && q) googleFallback();
        }
        if (e.key === 'Escape') { input.value = ''; clearFilter(); }
    });

    btn.addEventListener('click', function() {
        var q = input.value.trim();
        if (!q) return;
        var matches = document.querySelectorAll('.search-match').length;
        if (matches === 0) googleFallback();
        // If there are matches, button click just shows "Search Google News for more"
        else window.open('https://news.google.com/search?q=' + encodeURIComponent(q) + '&hl=en-US&gl=US&ceid=US:en', '_blank');
    });

    // Update button label when there are live matches
    input.addEventListener('input', function() {
        setTimeout(function() {
            var matches = document.querySelectorAll('.search-match').length;
            if (input.value.trim()) {
                btn.textContent = matches > 0 ? 'More on Google \u2192' : 'Search Google \u2192';
            } else {
                btn.textContent = 'Search';
            }
        }, 200);
    });
})();

// ── ROTATING BREAKING BANNER ──
(function() {
    var items = window._bbItems || [];
    var banner = document.getElementById('breaking-banner');
    if (!items.length || !banner) return;
    var textEl    = document.getElementById('bb-text');
    var timeEl    = document.getElementById('bb-time');
    var counterEl = document.getElementById('bb-counter');
    var closeBtn  = document.getElementById('bb-close');
    var sectionPill = document.getElementById('bb-section-pill');
    var idx = 0;
    var IS_MOBILE_BB = window.innerWidth <= 900;
    function show(i) {
        var item = items[i % items.length];
        if (!item) return;
        if (textEl) {
            textEl.style.animation = 'none';
            void textEl.offsetWidth;
            textEl.style.animation = '';
            textEl.textContent = item.title;
        }
        if (timeEl)    timeEl.textContent = item.time;
        if (counterEl) counterEl.textContent = (i + 1) + ' / ' + items.length;
        if (sectionPill && !IS_MOBILE_BB && item.section) {
            sectionPill.textContent = item.section;
            sectionPill.style.display = 'inline';
            sectionPill.style.background = (item.scolor || '#555') + '33';
            sectionPill.style.color = '#fff';
            sectionPill.style.border = '1px solid ' + (item.scolor || '#555');
        } else if (sectionPill) {
            sectionPill.style.display = 'none';
        }
    }
    show(0);
    var ticker = null;
    if (items.length > 1) {
        ticker = setInterval(function() { idx = (idx + 1) % items.length; show(idx); }, 5000);
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            banner.style.display = 'none';
            if (ticker) clearInterval(ticker);
        });
    }
})();

// ── READ-ARTICLE DIMMING (click-only) ──
(function() {
    var READ_KEY = 'mp_read_links';
    var readLinks = new Set();
    try { var raw = localStorage.getItem(READ_KEY); if (raw) readLinks = new Set(JSON.parse(raw)); } catch(e) {}
    function saveRead() { try { localStorage.setItem(READ_KEY, JSON.stringify([...readLinks].slice(-2000))); } catch(e) {} }
    document.querySelectorAll('[data-link]').forEach(function(el) {
        var lnk = el.getAttribute('data-link');
        if (lnk && readLinks.has(lnk)) el.classList.add('seen-item');
    });
    document.addEventListener('click', function(e) {
        var link = e.target.closest('.link, .ts-link');
        if (!link) return;
        var article = link.closest('[data-link]') || link.closest('.top-story-card');
        if (!article) return;
        var lnk = article.getAttribute('data-link') || link.getAttribute('href');
        if (lnk && lnk !== '#') { readLinks.add(lnk); article.classList.add('seen-item'); saveRead(); }
    });
})();

// ── SECTION COLLAPSE ──
(function() {
    var CKEY = 'mp_collapsed';
    var SKEY = 'mp_scroll';
    var collapsed = new Set();
    try { var raw = localStorage.getItem(CKEY); if (raw) collapsed = new Set(JSON.parse(raw)); } catch(e) {}
    function saveCollapsed() { try { localStorage.setItem(CKEY, JSON.stringify([...collapsed])); } catch(e) {} }
    collapsed.forEach(function(id) {
        var el  = document.getElementById(id);
        var btn = document.querySelector('[data-target="' + id + '"]');
        if (el)  el.classList.add('collapsed');
        if (btn) btn.innerHTML = '&#9654;';
    });
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.section-collapse-btn');
        if (!btn) return;
        var targetId = btn.getAttribute('data-target');
        var target   = document.getElementById(targetId);
        if (!target) return;
        if (target.classList.contains('collapsed')) {
            target.classList.remove('collapsed'); btn.innerHTML = '&#9660;'; collapsed.delete(targetId);
        } else {
            target.classList.add('collapsed');    btn.innerHTML = '&#9654;'; collapsed.add(targetId);
        }
        saveCollapsed();
    });
    // Restore scroll position
    try {
        var savedScroll = localStorage.getItem(SKEY);
        if (savedScroll) window.scrollTo(0, parseInt(savedScroll, 10));
    } catch(e) {}
    // Save scroll position on unload
    window.addEventListener('beforeunload', function() {
        try { localStorage.setItem(SKEY, Math.round(window.pageYOffset)); } catch(e) {}
    });
})();

// ── CLUSTER EXPAND/COLLAPSE ──
(function() {
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.cluster-toggle-btn');
        if (!btn) return;
        var targetId = btn.getAttribute('data-target');
        var wrap = document.getElementById(targetId);
        if (!wrap) return;
        if (wrap.classList.contains('collapsed')) {
            wrap.classList.remove('collapsed');
            btn.innerHTML = '&#9660; Hide coverage';
            btn.classList.add('open');
        } else {
            wrap.classList.add('collapsed');
            btn.innerHTML = '&#9654; Show all coverage';
            btn.classList.remove('open');
        }
    });
})();

// ── SCROLL SPY — highlight active nav section ──
(function() {
    var sections = [
        { id: 'section-us',       cls: 'nav-us' },
        { id: 'section-mideast',  cls: 'nav-mideast' },
        { id: 'section-world',    cls: 'nav-world' },
        { id: 'section-tech',     cls: 'nav-tech' },
        { id: 'section-business', cls: 'nav-business' },
        { id: 'section-sports',   cls: 'nav-sports' },
        { id: 'section-culture',  cls: 'nav-culture' },
    ];
    var navLinks = {};
    sections.forEach(function(s) {
        navLinks[s.cls] = document.querySelector('.sticky-nav a.' + s.cls);
    });
    function onScroll() {
        var scrollY = window.pageYOffset + 80;
        var active = null;
        for (var i = sections.length - 1; i >= 0; i--) {
            var el = document.getElementById(sections[i].id);
            if (el && el.offsetTop <= scrollY) { active = sections[i].cls; break; }
        }
        sections.forEach(function(s) {
            var link = navLinks[s.cls];
            if (!link) return;
            if (s.cls === active) link.classList.add('nav-active');
            else link.classList.remove('nav-active');
        });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
})();

// ── UPDATED X MINUTES AGO ──
(function() {
    var el = document.getElementById('nav-updated-ago');
    if (!el || !window._bbUpdateTs) return;
    function tick() {
        var diff = Math.floor((Date.now() / 1000) - window._bbUpdateTs);
        var str = '';
        if (diff < 60) str = 'Updated just now';
        else if (diff < 3600) str = 'Updated ' + Math.floor(diff / 60) + 'm ago';
        else str = 'Updated ' + Math.floor(diff / 3600) + 'h ago';
        el.textContent = str;
    }
    tick();
    setInterval(tick, 30000);
})();

// ── AUTO-REFRESH via feed.json polling ──
(function() {
    var FEED_URL = 'feed.json';
    var POLL_MS  = 5 * 60 * 1000; // 5 minutes
    var lastUpdated = null;

    function checkForUpdates() {
        fetch(FEED_URL + '?_=' + Date.now())
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var newUpdated = data.updated || null;
                if (lastUpdated === null) {
                    lastUpdated = newUpdated;
                    return;
                }
                if (newUpdated && newUpdated !== lastUpdated) {
                    lastUpdated = newUpdated;
                    showRefreshToast();
                }
            })
            .catch(function() {});
    }

    function showRefreshToast() {
        var toast = document.getElementById('refresh-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'refresh-toast';
            toast.style.cssText = [
                'position:fixed','bottom:70px','left:50%','transform:translateX(-50%)',
                'background:#B30000','color:#fff','padding:10px 22px','border-radius:6px',
                'font-size:0.85em','font-weight:bold','z-index:9999',
                'box-shadow:0 4px 16px rgba(0,0,0,0.5)','letter-spacing:0.04em',
                'display:flex','align-items:center','gap:12px'
            ].join(';');
            var msg = document.createElement('span');
            msg.textContent = '🔄 New headlines available — click to refresh';
            msg.style.cursor = 'pointer';
            msg.addEventListener('click', function() { location.reload(); });
            var closeX = document.createElement('button');
            closeX.textContent = '✕';
            closeX.title = 'Dismiss';
            closeX.style.cssText = 'background:none;border:none;color:#fff;font-size:1em;cursor:pointer;padding:0;opacity:0.7;flex-shrink:0;';
            closeX.addEventListener('click', function(e) {
                e.stopPropagation();
                toast.style.display = 'none';
            });
            toast.appendChild(msg);
            toast.appendChild(closeX);
            document.body.appendChild(toast);
        }
        toast.style.display = 'flex';
    }

    setInterval(checkForUpdates, POLL_MS);
    setTimeout(checkForUpdates, 10000); // first check after 10s
})();

}); // end DOMContentLoaded


</script>

</body></html>
""")

html_parts.append(f'''<footer class="site-footer">
    <button class="back-to-top-btn" onclick="window.scrollTo({{top:0,behavior:\'smooth\'}})">&#8679; Back to Top</button>
    <div style="margin-top:28px;">
        <h1>The Mitchell Post</h1>
        <span class="byline">By Sean Mitchell</span>
        <span class="mission">Curated news from reliable sources updated regularly.</span>
        <span class="update">Last updated: {update_time}</span>
    </div>
    <div class="homepage-wrap">
        <button class="set-homepage-btn" id="set-homepage-btn" onclick="document.getElementById(\'homepage-instructions\').style.display=document.getElementById(\'homepage-instructions\').style.display===\'block\'?\'none\':\'block\'">🏠 Set as My Homepage</button>
        <div id="homepage-instructions" class="homepage-instructions" style="display:none">
            <strong>How to set The Mitchell Post as your homepage:</strong><br>
            <span class="hp-browser"><b>Chrome:</b> Settings → On startup → Open a specific page → Add <code>https://theseanmitchell.github.io/TheMitchellPost/</code></span><br>
            <span class="hp-browser"><b>Firefox:</b> Settings → Home → Homepage → Custom URLs → paste the URL above</span><br>
            <span class="hp-browser"><b>Safari:</b> Preferences → General → Homepage → paste the URL above</span><br>
            <span class="hp-browser"><b>Edge:</b> Settings → Start, home, and new tabs → Open these pages → Add the URL above</span>
        </div>
    </div>
</footer>
''')

html = "".join(html_parts)

try:
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"SUCCESS: index.html saved to {INDEX_HTML}")
except Exception as e:
    print(f"ERROR saving file: {str(e)}")

# ── Write RSS feed ──
RSS_FILE = os.path.join(CURRENT_DIR, "feed.xml")
try:
    import xml.etree.ElementTree as ET
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "The Mitchell Post"
    ET.SubElement(channel, "link").text = "https://theseanmitchell.github.io/TheMitchellPost/"
    ET.SubElement(channel, "description").text = "Curated news from reliable sources — US, Middle East, Tech, Sports & Culture — updated continuously."
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    rss_items = sorted(all_items_flat, key=lambda x: x[0], reverse=True)[:50]
    for ts, title, source, link in rss_items:
        item_el = ET.SubElement(channel, "item")
        ET.SubElement(item_el, "title").text = title
        ET.SubElement(item_el, "link").text = link
        ET.SubElement(item_el, "guid").text = link
        pub_dt = datetime.utcfromtimestamp(ts).strftime("%a, %d %b %Y %H:%M:%S +0000")
        ET.SubElement(item_el, "pubDate").text = pub_dt
        ET.SubElement(item_el, "source").text = get_friendly_source(source)
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    with open(RSS_FILE, "wb") as rf:
        tree.write(rf, xml_declaration=True, encoding="utf-8")
    print(f"SUCCESS: feed.xml saved ({len(rss_items)} items)")
except Exception as e:
    print(f"WARNING: feed.xml not saved: {str(e)}")


import json as _json
try:
    feed_items = []
    sections = [
        ("US News",               us_breaking + us_recent),
        ("Middle East",           middle_breaking + middle_recent),
        ("Asia, Europe & World",  world_breaking + world_recent),
        ("Tech & Life",           tech_breaking + tech_recent),
        ("Business",              business_breaking + business_recent),
        ("Sports",                sports_breaking + sports_recent),
        ("Culture",               culture_breaking + culture_recent),
    ]
    for section_name, items in sections:
        for ts, title, source, link in items:
            feed_items.append({
                "section":   section_name,
                "title":     title,
                "source":    get_friendly_source(source),
                "link":      link,
                "published": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
    feed_items.sort(key=lambda x: x["published"], reverse=True)
    feed_doc = {
        "version":       "1.1",
        "title":         "The Mitchell Post",
        "home_page_url": "https://mitchellpost.github.io",
        "description":   "Curated news across US, Middle East, Asia/Europe/World, Tech, Sports, and Culture",
        "updated":       (datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": feed_items
    }
    with open(FEED_JSON, "w", encoding="utf-8") as fj:
        _json.dump(feed_doc, fj, ensure_ascii=False, indent=2)
    print(f"SUCCESS: feed.json saved ({len(feed_items)} items)")
except Exception as e:
    print(f"WARNING: feed.json not saved: {str(e)}")

# ── Write _headers for GitHub Pages caching ──
try:
    headers_content = """/*
  Cache-Control: public, max-age=300, stale-while-revalidate=60
/feed.json
  Cache-Control: public, max-age=300
"""
    with open(HEADERS_FILE, "w") as hf:
        hf.write(headers_content)
    print("SUCCESS: _headers written")
except Exception as e:
    print(f"WARNING: _headers not written: {str(e)}")

print("\nScript finished.")
print("Files saved to current directory.")
