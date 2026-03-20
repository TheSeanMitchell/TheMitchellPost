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
    "viral fashion content","viral entertainment content","xbiz news","avn awards",
    "onlyfans news","adult entertainment industry","glamour photography",
    "editorial photography","high end fashion shoots","luxury brand collaborations",
    "designer campaigns","fashion advertising","celebrity endorsements","product collaborations",
    "influencer marketing fashion","influencer partnerships","beauty collaborations",
    "makeup influencer trends","skincare influencer trends","sports illustrated swimsuit",
    "si swimsuit","miss universe","miss america","miss world","pageant news",
    "miami swim week 2026","bikini runway 2026","bikini flavors resort 2026",
    "slay swimwear 2026","papi swim 2026","bikini beach spring summer 2026",
    "naked summer miami","sophie rain bikini","kylie jenner golden bikini 2026",
    "alix earle pearl bikini 2026","sports illustrated swimsuit issue 2026",
    "playboy playmates 2026","onlyfans top creators 2026","kpop demon hunters",
    "teyana taylor red carpet 2026","2016 fashion revival 2026",
    "librarian chic fashion 2026","faux fur trend 2026","bomber jacket comeback 2026",
    "skinny jeans 2026","knee high boots revival 2026","triangl bikinis 2026",
    "kylie jenner lip kits revival","laufey style 2026","iris law outfits 2026",
    "pinkpantheress fashion 2026","alex consani modeling 2026","lily rose depp looks 2026",
    "gen z celeb outfits 2026","synthetic celebrities ai idols 2026",
    "immersive entertainment trends 2026","k pop comebacks 2026","blackpink tour fashion",
    "bts solo style","newjeans runway looks","playboy centerfold 2026",
    "glamour nude shoots 2026","high end lingerie fashion shows",
    "swimwear catalog models 2026","fitness bikini competitors 2026",
    "miss universe bikini round 2026","pageant modeling tips",
    "influencer bikini try on hauls","tiktok swimsuit challenges",
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
]
CULTURE_KEYWORDS = set(kw.lower() for kw in RAW_CULTURE_KEYWORDS)

# ====================== BLOCKLISTS ======================
ME_BLOCKLIST    = {"trump"}
US_BLOCKLIST    = {"iran"}
SPORTS_BLOCKLIST = set()
TECH_BLOCKLIST   = set()
CULTURE_BLOCKLIST= set()

# Pre-compile all patterns once
ME_PATTERN      = make_keyword_pattern(ME_KEYWORDS)
US_PATTERN      = make_keyword_pattern(US_KEYWORDS)
SPORTS_PATTERN  = make_keyword_pattern(SPORTS_KEYWORDS)
TECH_PATTERN    = make_keyword_pattern(TECH_KEYWORDS)
CULTURE_PATTERN = make_keyword_pattern(CULTURE_KEYWORDS)

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

# ====================== FETCH FUNCTION ======================
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
                    if title_matches_keywords(title_lower, pattern):
                        ts_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                        ts = time.mktime(ts_struct) if ts_struct else time.time()
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
middle_matches  = fetch_section(MIDDLE_EAST_SOURCES, ME_KEYWORDS, ME_PATTERN, ME_BLOCKLIST)
us_matches      = fetch_section(US_POLITICS_SOURCES, US_KEYWORDS, US_PATTERN, US_BLOCKLIST)
sports_matches  = fetch_section(SPORTS_SOURCES, SPORTS_KEYWORDS, SPORTS_PATTERN, SPORTS_BLOCKLIST)
tech_matches    = fetch_section(TECH_SOURCES, TECH_KEYWORDS, TECH_PATTERN, TECH_BLOCKLIST)
culture_matches = fetch_section(CULTURE_SOURCES, CULTURE_KEYWORDS, CULTURE_PATTERN, CULTURE_BLOCKLIST)

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

def cluster_items(items, min_shared=3):
    """
    Returns a list of clusters. Each cluster is a list of (ts, title, source, link).
    Single-item clusters are just solo headlines. Multi-item clusters are grouped stories.
    """
    used = [False] * len(items)
    clusters = []
    token_cache = [headline_tokens(it[1]) for it in items]

    for i in range(len(items)):
        if used[i]:
            continue
        cluster = [items[i]]
        used[i] = True
        for j in range(i + 1, len(items)):
            if used[j]:
                continue
            shared = len(token_cache[i] & token_cache[j])
            if shared >= min_shared:
                cluster.append(items[j])
                used[j] = True
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
            out += (
                f'<div class="headline" data-link="{link}" data-ts="{int(ts)}">'
                f'{hot_dot}'
                f'<span class="title">{display_title}</span>'
                f' <span class="ts-label">{time_str}</span>'
                f' <span class="src-label">\u2014 {friendly}</span>'
                f' <a class="link" href="{link}" target="_blank">[Full Article]</a>'
                f'</div>\n'
            )
        else:
            # Multi-source cluster: grouped story card
            cluster.sort(key=lambda x: x[0], reverse=True)
            lead_ts, lead_title, lead_source, lead_link = cluster[0]
            display_title = lead_title[0].upper() + lead_title[1:] if lead_title else lead_title
            time_str = ts_to_pdt(lead_ts)
            is_hot = (now - lead_ts) <= THIRTY_MIN
            hot_dot = '<span class="new-dot" title="Published in the last 30 minutes">&#9679;</span> ' if is_hot else ''
            sources_list = [get_friendly_source(it[2]) for it in cluster]
            n_sources = len(sources_list)
            sources_str = ", ".join(sources_list)
            out += (
                f'<div class="cluster" data-ts="{int(lead_ts)}">'
                f'<div class="cluster-header">'
                f'{hot_dot}'
                f'<span class="cluster-badge">{n_sources} sources</span>'
                f'<span class="cluster-sources">{sources_str}</span>'
                f'</div>\n'
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
            out += '</div>\n'
    return out

# ====================== SOURCE COUNT SUMMARY ======================
def source_summary(items):
    sources = set(get_friendly_source(it[2]) for it in items)
    return f'<p class="src-summary">{len(items)} headlines \u00b7 {len(sources)} sources</p>\n'


# ====================== TOP STORIES STRIP ======================
def build_top_stories(max_stories=5):
    """Pull the top multi-source clusters across all sections for the pinned strip."""
    all_section_items = [
        ("US",          us_breaking + us_recent),
        ("Middle East", middle_breaking + middle_recent),
        ("Tech",        tech_breaking + tech_recent),
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

# ====================== BUILD HTML ======================
# Collect all timestamps across ALL items for the breaking-news banner check
all_items_flat = (
    us_breaking + us_recent +
    middle_breaking + middle_recent +
    sports_breaking + sports_recent +
    tech_breaking + tech_recent +
    culture_breaking + culture_recent
)
ONE_HOUR = 3600
hot_items = sorted(
    [it for it in all_items_flat if (time.time() - it[0]) <= ONE_HOUR],
    key=lambda x: x[0], reverse=True
)
show_breaking_banner = len(hot_items) > 0

update_time = (datetime.utcnow() + PDT_OFFSET).strftime("%I:%M:%S %p PDT")

# Section color map for nav bar accents
SECTION_COLORS = {
    "us":      "#B30000",
    "mideast": "#C05000",
    "tech":    "#005F9E",
    "sports":  "#006B3C",
    "culture": "#6B006B",
}

html_parts = []
html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Mitchell Post</title>
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
    .sticky-nav a.nav-us     {{ border-left-color: {SECTION_COLORS["us"]}; }}
    .sticky-nav a.nav-mideast{{ border-left-color: {SECTION_COLORS["mideast"]}; }}
    .sticky-nav a.nav-tech   {{ border-left-color: {SECTION_COLORS["tech"]}; }}
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
        font-size: 0.76em; opacity: 0.8; flex-shrink: 0;
    }}
    .breaking-banner .bb-link {{
        color: #ffcccc; font-size: 0.78em; flex-shrink: 0; text-decoration: underline;
    }}
    .breaking-banner .bb-link:hover {{ color: #FFFFFF; }}
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
    .section-title.us-color     {{ color: {SECTION_COLORS["us"]};      text-decoration-color: {SECTION_COLORS["us"]}; }}
    .section-title.mideast-color{{ color: {SECTION_COLORS["mideast"]}; text-decoration-color: {SECTION_COLORS["mideast"]}; }}
    .section-title.tech-color   {{ color: {SECTION_COLORS["tech"]};    text-decoration-color: {SECTION_COLORS["tech"]}; }}
    .section-title.sports-color {{ color: {SECTION_COLORS["sports"]};  text-decoration-color: {SECTION_COLORS["sports"]}; }}
    .section-title.culture-color{{ color: {SECTION_COLORS["culture"]}; text-decoration-color: {SECTION_COLORS["culture"]}; }}

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
    .container {{ display: flex; flex-wrap: wrap; gap: 30px; max-width: 1400px; margin: 0 auto; padding: 0 20px; }}
    .column {{ flex: 1; min-width: 300px; }}
    .section-wrap {{ padding: 0 0 10px 0; }}

    /* ── Auto light mode on first visit (if system prefers light) ── */
    @media (prefers-color-scheme: light) {{
        body:not(.dark-forced):not(.light-mode) {{
            background: #FFFFFF; color: #000000;
        }}
    }}

    /* ── Light mode toggle pill ── */
    .nav-spacer {{ flex: 1 1 auto; min-width: 8px; }}
    .mode-toggle {{
        display: flex; align-items: center; gap: 7px;
        flex-shrink: 0; margin-left: 10px; cursor: pointer; user-select: none;
        background: none; border: none; padding: 0; font-family: inherit;
    }}
    .mode-toggle .mode-label {{
        font-size: 0.70em; color: #888888; font-weight: bold;
        letter-spacing: 0.06em; text-transform: uppercase;
    }}
    .toggle-pill {{
        width: 38px; height: 20px; border-radius: 10px;
        background: #333333; border: 1px solid #555;
        position: relative; transition: background 0.25s; flex-shrink: 0;
    }}
    .toggle-pill::after {{
        content: ''; position: absolute; top: 2px; left: 2px;
        width: 14px; height: 14px; border-radius: 50%;
        background: #888888; transition: left 0.25s, background 0.25s;
    }}
    body.light-mode .toggle-pill {{ background: #dde0e4; border-color: #bbb; }}
    body.light-mode .toggle-pill::after {{ left: 20px; background: #333; }}
    body.light-mode .mode-toggle .mode-label {{ color: #555; }}
    body.light-mode {{ background: #FFFFFF; color: #000000; }}
    body.light-mode .sticky-nav {{ background: #F5F5F5; border-bottom-color: #B30000; }}
    body.light-mode .sticky-nav .site-name {{ color: #000000; }}
    body.light-mode .sticky-nav .site-name:hover {{ color: #222222; }}
    body.light-mode .sticky-nav a {{ color: #111111; }}
    body.light-mode .sticky-nav a:hover {{ color: #000000; }}
    body.light-mode .breaking-banner {{ background: #B30000; color: #FFFFFF; }}
    body.light-mode .breaking-banner .bb-label {{ background: #FFFFFF; color: #B30000; }}
    body.light-mode .banner {{ background: #e6ecf5; }}
    body.light-mode .title {{ color: #000000; }}
    body.light-mode .ts-label {{ color: #444444; }}
    body.light-mode .src-label {{ color: #333333; }}
    body.light-mode .new-dot {{ color: #000000; }}
    body.light-mode .src-summary {{ color: #444444; }}
    body.light-mode .headline {{ border-bottom-color: #e4e4e4; }}
    body.light-mode .headline.seen-item {{ opacity: 0.38; }}
    body.light-mode .cluster {{ background: #F8F8F8; border-left-color: #ccc; border-bottom-color: #e4e4e4; }}
    body.light-mode .cluster-badge {{ background: #e0e0e0; color: #000000; }}
    body.light-mode .cluster-sources {{ color: #555555; }}
    body.light-mode .cluster-item {{ border-bottom-color: #eee; }}
    body.light-mode .link {{ color: #000000; }}
    body.light-mode .link:hover {{ color: #000000; }}
    body.light-mode .top-divider {{ background: #e4e4e4; }}
    body.light-mode .site-footer {{ background: #F5F5F5; border-top-color: #e0e0e0; }}
    body.light-mode .site-footer h1 {{ color: #000000; }}
    body.light-mode .site-footer .byline {{ color: #222222; }}
    body.light-mode .site-footer .update {{ color: #444444; }}
    /* ── Per-section cluster tint colors ── */
    #section-us      .cluster {{ border-left-color: #4a0000; background: #1a0505; }}
    #section-mideast .cluster {{ border-left-color: #4a2000; background: #1a0d00; }}
    #section-tech    .cluster {{ border-left-color: #002040; background: #060f1a; }}
    #section-sports  .cluster {{ border-left-color: #002a18; background: #04120a; }}
    #section-culture .cluster {{ border-left-color: #300030; background: #120512; }}
    /* Light mode tints */
    body.light-mode #section-us      .cluster {{ background: #fff5f5; border-left-color: #B30000; }}
    body.light-mode #section-mideast .cluster {{ background: #fff8f0; border-left-color: #C05000; }}
    body.light-mode #section-tech    .cluster {{ background: #f0f6ff; border-left-color: #005F9E; }}
    body.light-mode #section-sports  .cluster {{ background: #f0fff6; border-left-color: #006B3C; }}
    body.light-mode #section-culture .cluster {{ background: #fdf0ff; border-left-color: #6B006B; }}

    /* ── Site footer ── */
    .site-footer {{
        margin-top: 50px; padding: 30px 20px 40px 20px;
        border-top: 2px solid #222222; text-align: center;
        background: #0d0d0d; color: #555;
    }}
    .site-footer h1 {{ font-size: 1.8em; text-decoration: underline; color: #FFFFFF; margin-bottom: 6px; }}
    .site-footer .byline {{ font-size: 0.95em; color: #888; display: block; margin-bottom: 4px; }}
    .site-footer .update {{ font-size: 0.8em; color: #555; display: block; }}

    /* ── Search + AI bar ── */
    .search-bar-wrap {{
        max-width: 1400px; margin: 0 auto 20px auto; padding: 0 20px;
    }}
    .search-bar-inner {{
        display: flex; gap: 0; background: #1a1a1a;
        border: 1px solid #333; border-radius: 6px; overflow: hidden;
    }}
    .search-bar-inner input {{
        flex: 1; background: transparent; border: none; outline: none;
        color: #FFFFFF; font-size: 0.95em; padding: 10px 14px;
        font-family: Arial, sans-serif;
    }}
    .search-bar-inner input::placeholder {{ color: #666; }}
    .search-bar-btn {{
        background: #1e1e1e; border: none; border-left: 1px solid #333;
        color: #aaaaaa; font-size: 0.78em; font-weight: bold;
        letter-spacing: 0.05em; text-transform: uppercase;
        padding: 0 14px; cursor: pointer; transition: background 0.15s, color 0.15s;
        white-space: nowrap;
    }}
    .search-bar-btn:hover {{ background: #2a2a2a; color: #FFFFFF; }}
    .search-bar-btn.ai-btn {{ border-left-color: #333; color: #7aadff; }}
    .search-bar-btn.ai-btn:hover {{ background: #162030; color: #FFFFFF; }}
    /* AI response panel */
    .ai-response-panel {{
        display: none; margin-top: 8px; background: #161c26;
        border: 1px solid #1e3050; border-radius: 6px;
        padding: 14px 16px; font-size: 0.92em; line-height: 1.65;
        color: #d0d8e8; max-height: 400px; overflow-y: auto;
    }}
    .ai-response-panel.active {{ display: block; }}
    .ai-response-panel .ai-thinking {{
        color: #7aadff; font-style: italic; animation: blink 1s step-end infinite;
    }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    /* Light mode search */
    body.light-mode .search-bar-inner {{
        background: #FFFFFF; border-color: #cccccc;
    }}
    body.light-mode .search-bar-inner input {{ color: #000000; }}
    body.light-mode .search-bar-inner input::placeholder {{ color: #aaaaaa; }}
    body.light-mode .search-bar-btn {{ background: #F0F0F0; color: #333333; border-left-color: #cccccc; }}
    body.light-mode .search-bar-btn:hover {{ background: #E0E0E0; color: #000000; }}
    body.light-mode .search-bar-btn.ai-btn {{ color: #0055aa; }}
    body.light-mode .search-bar-btn.ai-btn:hover {{ background: #e6eef8; color: #000000; }}
    body.light-mode .ai-response-panel {{ background: #f0f4ff; border-color: #b0c4e8; color: #111111; }}

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
        background: #1a1a1a; border-left: 3px solid #B30000;
        padding: 10px 14px; margin-bottom: 8px; border-radius: 2px;
    }}
    .top-story-card .ts-section-tag {{
        font-size: 0.68em; font-weight: bold; letter-spacing: 0.08em;
        text-transform: uppercase; margin-right: 8px; opacity: 0.7;
    }}
    .top-story-card .ts-badge {{
        background: #333; color: #ccc; font-size: 0.68em;
        padding: 1px 6px; border-radius: 8px; margin-right: 8px;
    }}
    .top-story-card .ts-headline {{ color: #FFFFFF; font-size: 0.95em; }}
    .top-story-card .ts-link {{ color: #545454; text-decoration: underline; font-size: 0.8em; margin-left: 6px; }}
    .top-story-card .ts-link:hover {{ color: #FFFFFF; }}
    body.light-mode .top-stories-title {{ color: #555555; border-bottom-color: #e0e0e0; }}
    body.light-mode .top-story-card {{ background: #F4F4F4; border-left-color: #B30000; }}
    body.light-mode .top-story-card .ts-badge {{ background: #e0e0e0; color: #222222; }}
    body.light-mode .top-story-card .ts-headline {{ color: #000000; }}
    body.light-mode .top-story-card .ts-link {{ color: #777777; }}
    body.light-mode .top-story-card .ts-link:hover {{ color: #000000; }}

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
        .section-title {{ font-size: 1.3em; }}
        .top-divider {{ margin: 18px 0; }}

        /* Cluster cards on mobile */
        .cluster {{ padding: 8px 10px 4px 10px; }}
        .cluster-badge {{ font-size: 0.78em; }}
        /* Light mode Full Article button on mobile */
        body.light-mode .link {{
            background: #eeeeee; border-color: #999999; color: #000000;
        }}
        body.light-mode .link:hover, body.light-mode .link:active {{
            background: #cccccc; color: #000000;
        }}
    }}
    /* ── Drag-to-reorder sections ── */
    .sections-wrapper {{ outline: none; }}
    .section-wrap {{ cursor: default; transition: opacity 0.15s; }}
    .section-wrap.dragging {{ opacity: 0.4; }}
    .section-wrap.drag-over {{ outline: 2px dashed #555; outline-offset: -2px; }}
    .drag-handle {{
        display: inline-block; cursor: grab; opacity: 0.35;
        font-size: 0.85em; margin-left: 10px; vertical-align: middle;
        letter-spacing: -1px; user-select: none;
    }}
    .drag-handle:hover {{ opacity: 0.8; }}
    .drag-handle:active {{ cursor: grabbing; }}
    @media (max-width: 900px) {{ .drag-handle {{ display: none; }} }}

    /* ── Print stylesheet ── */
    @media print {{
        .sticky-nav, .banner, .breaking-banner, .search-bar-wrap,
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

    </style>
</head>
<body>

<!-- ══ STICKY NAVIGATION BAR ══ -->
<nav class="sticky-nav">
    <a href="#" class="site-name" aria-label="Back to top">The Mitchell Post</a>
    <a href="#section-us"      class="nav-us">US News</a>
    <a href="#section-mideast" class="nav-mideast">Middle East</a>
    <a href="#section-tech"    class="nav-tech">Tech &amp; Life</a>
    <a href="#section-sports"  class="nav-sports">Sports</a>
    <a href="#section-culture" class="nav-culture">Culture</a>
    <span class="nav-spacer"></span>
    <button class="mode-toggle" id="mode-toggle" title="Toggle light / dark mode" type="button">
        <span class="mode-label" id="mode-label">Light</span>
        <span class="toggle-pill"></span>
    </button>
</nav>

""")

# Rotating breaking news banner (all items < 1 hour)
if show_breaking_banner:
    import json as _json_banner
    banner_data = [
        {"title": it[1][:140].replace('"', '&quot;'), "link": it[3], "time": ts_to_pdt(it[0])}
        for it in hot_items[:20]
    ]
    banner_json = _json_banner.dumps(banner_data)
    html_parts.append(
        f'<div class="breaking-banner" id="breaking-banner">'
        f'<span class="bb-label">BREAKING</span>'
        f'<span class="bb-text" id="bb-text"></span>'
        f'<span class="bb-time" id="bb-time"></span>'
        f'<a class="bb-link" id="bb-link" href="#" target="_blank" style="display:none">[Read]</a>'
        f'<span class="bb-counter" id="bb-counter"></span>'
        f'</div>'
        f'<script>window._bbItems = {banner_json};</script>\n'
    )

html_parts.append(f"""
<!-- ══ VIDEO BANNER — desktop only, hidden on mobile via CSS ══ -->
<div class="banner">
    <div class="video-grid">
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/TBlxk1kH9dM?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/Ap-UM1O9RBU?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/LuKwFajn37U?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/gCNeDWCI0vo?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/b_ERc4vcRHI?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/nya02XlHG1Q?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/_6dRRfnYJws?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
        <div class="youtube-inset"><iframe src="https://www.youtube.com/embed/pykpO5kQJ98?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0&iv_load_policy=3&playsinline=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
    </div>
</div>

""")

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
        f'<span class="drag-handle" title="Drag to reorder">&#8942;&#8942;</span>'
        f'</div>\n'
        f'<div id="{section_id}-cols" class="section-columns">\n'
        f'{b_summary}'
        f'{b_content}'
        f'</div>\n'
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
    )

# ── Top Stories strip HTML ──
if top_stories:
    ts_html = '<div class="top-stories-strip"><p class="top-stories-title">Top Stories &mdash; Most Covered Right Now</p>\n'
    for n_src, lead_ts, section_label, cluster in top_stories:
        lead_ts2, lead_title, lead_source, lead_link = cluster[0]
        safe_title = lead_title.replace('<','&lt;').replace('>','&gt;')
        safe_title = safe_title[0].upper() + safe_title[1:] if safe_title else safe_title
        ts_html += (
            f'<div class="top-story-card">'
            f'<span class="ts-section-tag">{section_label}</span>'
            f'<span class="ts-badge">{n_src} sources</span>'
            f'<span class="ts-headline">{safe_title}</span>'
            f'<span class="ts-label"> {ts_to_pdt(lead_ts2)}</span>'
            f'<a class="ts-link" href="{lead_link}" target="_blank">[Read]</a>'
            f'</div>\n'
        )
    ts_html += '</div>\n'
    html_parts.append(ts_html)

# ── Search + AI bar HTML ──
html_parts.append('''<div class="search-bar-wrap">
    <div class="search-bar-inner">
        <input type="text" id="mp-search-input" placeholder="Search news (Enter) or ask AI (Ctrl+Enter / AI button)..." autocomplete="off" />
        <button class="search-bar-btn" id="search-btn" title="Search Brave News">&#x1F50E; News</button>
        <button class="search-bar-btn ai-btn" id="ai-btn" title="Ask AI — fact-check, summarize, explain">&#x2728; Ask AI</button>
    </div>
    <div class="ai-response-panel" id="ai-panel"></div>
</div>
''')

# ── Build sections in user-preferred order (default order, JS reorders on page) ──
SECTION_DATA = [
    ("section-us",      "us-color",      us_breaking,      us_recent,      "Breaking US News",          "Today&#39;s US Headlines"),
    ("section-mideast", "mideast-color", middle_breaking,  middle_recent,  "Middle East Breaking News", "Today&#39;s Middle East Headlines"),
    ("section-tech",    "tech-color",    tech_breaking,    tech_recent,    "Tech &amp; Life Breaking News", "Today&#39;s Tech &amp; Life Headlines"),
    ("section-sports",  "sports-color",  sports_breaking,  sports_recent,  "Sports Breaking News",      "Today&#39;s Sports Headlines"),
    ("section-culture", "culture-color", culture_breaking, culture_recent, "Culture Breaking News",     "Today&#39;s Culture Headlines"),
]
html_parts.append('<div id="sections-wrapper">\n')
for i, (sid, sc, bi, ri, bt, rt) in enumerate(SECTION_DATA):
    html_parts.append(section_block(sid, sc, bi, ri, bt, rt))
    if i < len(SECTION_DATA) - 1:
        html_parts.append('<hr class="top-divider">\n')
html_parts.append('</div>\n')

html_parts.append("""
<!-- ══ YOUTUBE AUTO-MUTE ══ -->
<script src="https://www.youtube.com/iframe_api"></script>
<script src="https://www.youtube.com/iframe_api"></script>
<script src="https://www.youtube.com/iframe_api"></script>
<script>
// ── YT auto-mute (must be global for YT API callback) ──
var players = [];
function onYouTubeIframeAPIReady() {
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

// ── ROTATING BREAKING BANNER ──
(function() {
    var items = window._bbItems || [];
    var banner = document.getElementById('breaking-banner');
    if (!items.length || !banner) return;
    var textEl    = document.getElementById('bb-text');
    var timeEl    = document.getElementById('bb-time');
    var linkEl    = document.getElementById('bb-link');
    var counterEl = document.getElementById('bb-counter');
    var idx = 0;
    function show(i) {
        var item = items[i % items.length];
        if (!item) return;
        if (textEl) {
            textEl.style.animation = 'none';
            void textEl.offsetWidth; // force reflow for animation restart
            textEl.style.animation = '';
            textEl.textContent = item.title;
        }
        if (timeEl)    timeEl.textContent = item.time;
        if (linkEl)  { linkEl.href = item.link; linkEl.style.display = 'inline'; }
        if (counterEl) counterEl.textContent = (i + 1) + ' / ' + items.length;
    }
    show(0);
    if (items.length > 1) {
        setInterval(function() { idx = (idx + 1) % items.length; show(idx); }, 6000);
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
})();

// ── SEARCH BAR ──
(function() {
    var input   = document.getElementById('mp-search-input');
    var srchBtn = document.getElementById('search-btn');
    var aiBtn   = document.getElementById('ai-btn');
    var panel   = document.getElementById('ai-panel');

    function openSearch() {
        var q = (input ? input.value : '').trim();
        if (!q) return;
        // Use anchor click trick — never blocked by popup blockers
        var a = document.createElement('a');
        a.href = 'https://search.brave.com/news?q=' + encodeURIComponent(q);
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function openAI() {
        var q = (input ? input.value : '').trim();
        if (!q) return;
        if (!panel) return;
        panel.className = 'ai-response-panel active';
        panel.innerHTML = '<span class="ai-thinking">Thinking\u2026</span>';
        fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: 'claude-sonnet-4-6',
                max_tokens: 1000,
                system: 'You are a news analysis assistant inside The Mitchell Post, a news aggregator. Be concise (under 250 words), factual, focused on news context and fact-checking. Plain text only, no markdown headers.',
                messages: [{ role: 'user', content: q }]
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var text = '';
            if (data.content) { data.content.forEach(function(b) { if (b.type === 'text') text += b.text; }); }
            else if (data.error) { text = 'Error: ' + data.error.message; }
            if (panel) panel.innerHTML = text.replace(/\n/g, '<br>');
        })
        .catch(function() { if (panel) panel.innerHTML = 'Could not reach AI. Check your connection.'; });
    }

    if (srchBtn) srchBtn.addEventListener('click', function(e) { e.preventDefault(); openSearch(); });
    if (aiBtn)   aiBtn.addEventListener('click',   function(e) { e.preventDefault(); openAI(); });
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (e.ctrlKey || e.metaKey) { openAI(); } else { openSearch(); }
            }
        });
    }
})();

// ── DRAG-TO-REORDER SECTIONS ──
(function() {
    var OKEY    = 'mp_section_order';
    var wrapper = document.getElementById('sections-wrapper');
    if (!wrapper) return;
    function getSections() { return Array.from(wrapper.querySelectorAll(':scope > .section-wrap')); }
    function getDividers() { return Array.from(wrapper.querySelectorAll(':scope > .top-divider')); }
    function saveOrder() {
        try { localStorage.setItem(OKEY, JSON.stringify(getSections().map(function(s) { return s.id; }))); } catch(e) {}
    }
    function restoreOrder() {
        var saved = null;
        try { saved = JSON.parse(localStorage.getItem(OKEY)); } catch(e) {}
        if (!saved || !saved.length) return;
        var smap = {}; getSections().forEach(function(s) { smap[s.id] = s; });
        var dividers = getDividers();
        while (wrapper.firstChild) wrapper.removeChild(wrapper.firstChild);
        saved.forEach(function(id, i) {
            if (smap[id]) wrapper.appendChild(smap[id]);
            if (i < saved.length - 1 && dividers[i]) wrapper.appendChild(dividers[i]);
        });
    }
    restoreOrder();
    var dragSrc = null;
    function attachDrag(section) {
        section.setAttribute('draggable', 'true');
        section.addEventListener('dragstart', function(e) { dragSrc = section; setTimeout(function() { section.classList.add('dragging'); }, 0); e.dataTransfer.effectAllowed = 'move'; });
        section.addEventListener('dragend',   function()  { section.classList.remove('dragging'); wrapper.querySelectorAll('.drag-over').forEach(function(el) { el.classList.remove('drag-over'); }); saveOrder(); });
        section.addEventListener('dragover',  function(e) { e.preventDefault(); if (section !== dragSrc) section.classList.add('drag-over'); return false; });
        section.addEventListener('dragleave', function()  { section.classList.remove('drag-over'); });
        section.addEventListener('drop',      function(e) { e.stopPropagation(); e.preventDefault(); section.classList.remove('drag-over'); if (!dragSrc || dragSrc === section) return; wrapper.insertBefore(dragSrc, section); saveOrder(); return false; });
    }
    getSections().forEach(attachDrag);
})();

// ── LIGHT / DARK MODE TOGGLE ──
// Uses a <button> (not <label>) for reliable click on all devices/browsers
(function() {
    var LKEY = 'mp_light_mode';
    var btn  = document.getElementById('mode-toggle');
    var lbl  = btn ? btn.querySelector('.mode-label') : null;

    function applyMode(light) {
        document.body.classList.toggle('light-mode', !!light);
        if (lbl) lbl.textContent = light ? 'Dark' : 'Light';
    }

    // Determine initial mode
    var sv = null;
    try { sv = localStorage.getItem(LKEY); } catch(e) {}
    if (sv === '1')      { applyMode(true); }
    else if (sv === '0') { applyMode(false); }
    else {
        var prefersLight = !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches);
        applyMode(prefersLight);
    }

    // Click handler on the button
    if (btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var isLight = document.body.classList.contains('light-mode');
            applyMode(!isLight);
            try { localStorage.setItem(LKEY, isLight ? '0' : '1'); } catch(e2) {}
        });
    }
})();

}); // end DOMContentLoaded
</script>

</body></html>
""")

html_parts.append(f'''<footer class="site-footer">
    <h1>The Mitchell Post</h1>
    <span class="byline">By Sean Mitchell</span>
    <span class="update">updated at {update_time}</span>
</footer>
''')

html = "".join(html_parts)

try:
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"SUCCESS: index.html saved to {INDEX_HTML}")
except Exception as e:
    print(f"ERROR saving file: {str(e)}")

# ── Write feed.json ──
import json as _json
try:
    feed_items = []
    sections = [
        ("US News",      us_breaking + us_recent),
        ("Middle East",  middle_breaking + middle_recent),
        ("Tech & Life",  tech_breaking + tech_recent),
        ("Sports",       sports_breaking + sports_recent),
        ("Culture",      culture_breaking + culture_recent),
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
        "description":   "Curated news across US, Middle East, Tech, Sports, and Culture",
        "updated":       (datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": feed_items
    }
    with open(FEED_JSON, "w", encoding="utf-8") as fj:
        _json.dump(feed_doc, fj, ensure_ascii=False, indent=2)
    print(f"SUCCESS: feed.json saved ({len(feed_items)} items)")
except Exception as e:
    print(f"WARNING: feed.json not saved: {str(e)}")

print("\nScript finished.")
print("Files saved to current directory.")
