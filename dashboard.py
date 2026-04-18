import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
import xml.etree.ElementTree as ET
import re

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Disease Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"],
[data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: #f4f5f7 !important;
    color: #1a1a2e !important;
    color-scheme: light !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 1.5rem 2rem 1.5rem !important; max-width: 1600px; }
div[data-testid="stDecoration"] { display: none; }

/* ── Navbar buttons via st.columns ── */
.nav-bar-wrap {
    background: #ffffff;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 20px;
    padding: 0 8px;
    border-bottom: 1px solid #e0e6ed;
}
.nav-bar-wrap [data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    align-items: center !important;
    background: transparent !important;
    flex-wrap: wrap !important;
}
/* Every button in the navbar */
.nav-bar-wrap button {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    color: #4a5568 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 16px 8px !important;
    width: 100% !important;
    white-space: nowrap !important;
    transition: color 0.15s, border-color 0.15s !important;
}
.nav-bar-wrap button:hover {
    color: #1565c0 !important;
    border-bottom-color: #4a8fd4 !important;
    background: rgba(21,101,192,0.04) !important;
}
/* Active page button */
.nav-bar-wrap button:focus {
    color: #1565c0 !important;
    border-bottom-color: #1565c0 !important;
    box-shadow: none !important;
}
.nav-status {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.7rem; font-weight: 600; color: #1e7e45 !important;
    background: rgba(39,174,96,0.10); border: 1px solid rgba(39,174,96,0.35);
    border-radius: 20px; padding: 5px 11px; white-space: nowrap; margin: 6px 0;
}
.pulse-dot { width: 6px; height: 6px; background: #27ae60; border-radius: 50%;
    animation: pulse 2s infinite; display: inline-block; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.3)} }

/* ── KPI cards ── */
.kpi-card { background: #fff; border: 1px solid #e0e6ed; border-radius: 10px; padding: 20px 24px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
.kpi-num  { font-size: 2.4rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.kpi-label{ font-size: 0.78rem; font-weight: 500; color: #6b7c93; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }

/* ── Titles ── */
.section-title    { font-size: 1.05rem; font-weight: 700; color: #0d1b2a; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #1565c0; display: inline-block; }
.section-subtitle { font-size: 0.9rem; font-weight: 600; color: #1a3a5c; margin-bottom: 10px; }

/* ── DON card ── */
.don-card { display:block; background:#fff; border:1px solid #e0e6ed; border-left:4px solid #1565c0; border-radius:8px; padding:14px 16px; margin-bottom:10px; text-decoration:none !important; transition:box-shadow 0.15s; }
.don-card:hover { box-shadow:0 4px 14px rgba(0,0,0,0.08); }
.don-title { font-size:0.88rem; font-weight:700; color:#0d1b2a; line-height:1.45; margin-bottom:6px; }
.don-meta  { font-size:0.72rem; color:#6b7c93; }
.don-link  { font-size:0.75rem; font-weight:600; color:#1565c0; margin-top:8px; }

/* ── Article card ── */
.article-card { display:block; background:#fff; border:1px solid #e0e6ed; border-radius:10px; padding:18px; margin-bottom:14px; text-decoration:none !important; transition:transform 0.15s,box-shadow 0.15s; }
.article-card:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,0.09); border-color:#1565c0; }
.article-meta  { font-size:0.72rem; color:#1565c0; font-weight:600; margin-bottom:7px; }
.article-title { font-size:0.88rem; font-weight:700; color:#0d1b2a; line-height:1.45; margin-bottom:8px; }
.article-desc  { font-size:0.8rem; color:#5a6a7e; line-height:1.5; }
.article-link  { font-size:0.75rem; font-weight:600; color:#1565c0; margin-top:10px; }
.source-badge  { display:inline-block; font-size:0.68rem; font-weight:700; padding:2px 8px; border-radius:4px; margin-right:6px; text-transform:uppercase; }

/* ── Authority links ── */
.authority-link { display:block; text-align:center; background:#fff; border:1px solid #c5d3e0; border-radius:8px; padding:12px; font-size:0.82rem; font-weight:600; color:#1565c0 !important; text-decoration:none !important; transition:background 0.15s; margin-bottom:10px; }
.authority-link:hover { background:#e8f0fe; }

/* ── Disclaimer ── */
.disclaimer { background:#f0f4ff; border:1px solid #c5d3e0; border-radius:8px; padding:12px 16px; font-size:0.78rem; color:#34495e; margin-bottom:16px; line-height:1.6; }
.disclaimer a { color:#1565c0; }

/* ── Table ── */
.data-table { width:100%; border-collapse:collapse; background:#fff; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.04); font-size:0.85rem; }
.data-table th { background:#0d1b2a; color:#c8d6e5; font-weight:600; font-size:0.75rem; letter-spacing:0.08em; text-transform:uppercase; padding:12px 16px; text-align:left; }
.data-table td { padding:11px 16px; border-bottom:1px solid #edf0f4; color:#2c3e50; }
.data-table tr:last-child td { border-bottom:none; }
.data-table tr:hover td { background:#f7f9fc; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap:0; border-bottom:2px solid #e0e6ed !important; background:transparent !important; }
.stTabs [data-baseweb="tab"] { font-size:0.85rem !important; font-weight:600 !important; color:#6b7c93 !important; padding:10px 20px !important; border-radius:0 !important; background:transparent !important; }
.stTabs [aria-selected="true"] { color:#1565c0 !important; border-bottom:2px solid #1565c0 !important; }

/* ── Misc ── */
.feed-error { background:#fff8e1; border:1px solid #ffe082; border-radius:8px; padding:14px 18px; font-size:0.83rem; color:#6d4c00; }
.feed-error a { color:#1565c0; }
.footer { text-align:center; font-size:0.72rem; color:#a0aebe; margin-top:40px; padding-top:16px; border-top:1px solid #e0e6ed; }
.footer a { color:#7a9cc4; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PLACE → COORDINATES DICTIONARY
# Used to match place names in article titles/descriptions to map coordinates.
# Covers countries, major cities, and outbreak-prone regions.
# ══════════════════════════════════════════════════════════════════════════════
PLACES = {
    # Africa
    "nigeria": (9.082, 8.675), "lagos": (6.524, 3.379), "abuja": (9.057, 7.499),
    "congo": (-4.322, 15.322), "democratic republic of the congo": (-4.038, 21.759),
    "drc": (-4.038, 21.759), "kinshasa": (-4.322, 15.322),
    "ethiopia": (9.145, 40.489), "addis ababa": (9.025, 38.747),
    "kenya": (-0.023, 37.906), "nairobi": (-1.286, 36.818),
    "tanzania": (-6.369, 34.889), "dar es salaam": (-6.792, 39.209),
    "uganda": (1.373, 32.290), "kampala": (0.347, 32.583),
    "rwanda": (-1.940, 29.874), "kigali": (-1.944, 30.061),
    "ghana": (7.946, -1.023), "accra": (5.560, -0.197),
    "cameroon": (3.848, 11.502), "yaoundé": (3.848, 11.502),
    "south africa": (-30.559, 22.938), "johannesburg": (-26.205, 28.050), "cape town": (-33.924, 18.424),
    "egypt": (26.820, 30.802), "cairo": (30.044, 31.235),
    "somalia": (5.152, 46.199), "mogadishu": (2.046, 45.343),
    "sudan": (12.862, 30.217), "khartoum": (15.500, 32.560),
    "zambia": (-13.133, 27.849), "lusaka": (-15.417, 28.283),
    "zimbabwe": (-19.015, 29.154), "harare": (-17.829, 31.052),
    "mozambique": (-18.665, 35.530), "maputo": (-25.966, 32.573),
    "malawi": (-13.254, 34.302), "lilongwe": (-13.967, 33.787),
    "guinea": (11.804, -15.180), "conakry": (9.537, -13.677),
    "sierra leone": (8.460, -11.779), "freetown": (8.484, -13.234),
    "liberia": (6.428, -9.430), "monrovia": (6.300, -10.797),
    "burkina faso": (12.364, -1.530), "ouagadougou": (12.365, -1.534),
    "mali": (17.570, -3.996), "bamako": (12.650, -8.000),
    "senegal": (14.497, -14.452), "dakar": (14.693, -17.447),
    "chad": (15.454, 18.732), "n'djamena": (12.107, 15.043),
    "central african republic": (6.611, 20.939), "bangui": (4.361, 18.555),
    "angola": (-11.202, 17.874), "luanda": (-8.836, 13.234),
    "madagascar": (-18.767, 46.869), "antananarivo": (-18.910, 47.536),
    "mauritania": (21.007, -10.940), "nouakchott": (18.079, -15.965),
    "gabon": (-0.803, 11.609), "libreville": (0.416, 9.468),
    "equatorial guinea": (1.650, 10.268), "malabo": (3.750, 8.783),
    "burundi": (-3.373, 29.919), "bujumbura": (-3.382, 29.362),
    "eritrea": (15.179, 39.782), "asmara": (15.339, 38.931),
    "djibouti": (11.825, 42.590),
    "morocco": (31.792, -7.092), "rabat": (34.020, -6.842), "casablanca": (33.590, -7.620),
    "algeria": (28.034, 1.660), "algiers": (36.752, 3.042),
    "tunisia": (33.887, 9.537), "tunis": (36.819, 10.166),
    "libya": (26.335, 17.228), "tripoli": (32.902, 13.180),
    "east africa": (1.0, 37.0), "west africa": (12.0, -2.0),
    "central africa": (-2.0, 20.0), "southern africa": (-25.0, 27.0),
    "horn of africa": (8.0, 44.0),

    # Asia
    "china": (35.861, 104.195), "beijing": (39.904, 116.407), "shanghai": (31.230, 121.474),
    "wuhan": (30.593, 114.305), "guangzhou": (23.130, 113.264), "shenzhen": (22.543, 114.058),
    "india": (20.594, 78.963), "delhi": (28.613, 77.209), "new delhi": (28.613, 77.209),
    "mumbai": (19.076, 72.877), "kolkata": (22.572, 88.363), "chennai": (13.083, 80.270),
    "hyderabad": (17.385, 78.486), "bangalore": (12.972, 77.581), "pune": (18.520, 73.856),
    "kerala": (10.850, 76.271), "rajasthan": (27.023, 74.217),
    "pakistan": (30.375, 69.345), "karachi": (24.861, 67.010), "lahore": (31.549, 74.344),
    "islamabad": (33.729, 73.094),
    "bangladesh": (23.685, 90.356), "dhaka": (23.811, 90.413),
    "indonesia": (-0.789, 113.921), "jakarta": (-6.208, 106.846),
    "philippines": (12.880, 121.774), "manila": (14.599, 120.984),
    "vietnam": (14.059, 108.278), "hanoi": (21.028, 105.834), "ho chi minh": (10.776, 106.701),
    "viet nam": (14.059, 108.278),
    "thailand": (15.870, 100.993), "bangkok": (13.756, 100.502),
    "myanmar": (21.914, 95.956), "yangon": (16.867, 96.195),
    "cambodia": (12.566, 104.991), "phnom penh": (11.562, 104.916),
    "laos": (19.856, 102.495), "vientiane": (17.975, 102.633),
    "malaysia": (4.211, 101.976), "kuala lumpur": (3.140, 101.687),
    "singapore": (1.352, 103.820),
    "japan": (36.205, 138.252), "tokyo": (35.690, 139.692),
    "south korea": (35.908, 127.767), "seoul": (37.566, 126.978),
    "north korea": (40.340, 127.510),
    "taiwan": (23.698, 120.961), "taipei": (25.032, 121.565),
    "nepal": (28.395, 84.124), "kathmandu": (27.700, 85.316),
    "sri lanka": (7.873, 80.772), "colombo": (6.927, 79.862),
    "afghanistan": (33.939, 67.710), "kabul": (34.528, 69.172),
    "iran": (32.427, 53.688), "tehran": (35.694, 51.421),
    "iraq": (33.224, 43.679), "baghdad": (33.341, 44.401),
    "saudi arabia": (23.886, 45.079), "riyadh": (24.688, 46.724),
    "yemen": (15.552, 48.516), "sanaa": (15.369, 44.191),
    "turkey": (38.964, 35.243), "istanbul": (41.015, 28.980), "ankara": (39.921, 32.854),
    "uzbekistan": (41.377, 64.586), "tashkent": (41.300, 69.240),
    "kazakhstan": (48.020, 66.924), "almaty": (43.238, 76.946),
    "mongolia": (46.863, 103.847), "ulaanbaatar": (47.886, 106.906),
    "southeast asia": (13.0, 105.0),

    # Middle East
    "jordan": (30.586, 36.238), "amman": (31.957, 35.946),
    "lebanon": (33.855, 35.862), "beirut": (33.889, 35.501),
    "syria": (34.802, 38.997), "damascus": (33.510, 36.292),
    "israel": (31.046, 34.852), "tel aviv": (32.087, 34.789),
    "palestine": (31.952, 35.233), "gaza": (31.354, 34.309),
    "kuwait": (29.311, 47.482), "doha": (25.286, 51.533), "qatar": (25.354, 51.184),
    "uae": (23.424, 53.848), "dubai": (25.204, 55.271), "abu dhabi": (24.453, 54.377),

    # Europe
    "ukraine": (48.379, 31.166), "kyiv": (50.450, 30.523),
    "russia": (61.524, 105.319), "moscow": (55.751, 37.618),
    "germany": (51.165, 10.452), "berlin": (52.520, 13.405),
    "france": (46.228, 2.214), "paris": (48.857, 2.347),
    "italy": (41.872, 12.567), "rome": (41.902, 12.496),
    "spain": (40.463, -3.749), "madrid": (40.416, -3.703),
    "uk": (55.378, -3.436), "united kingdom": (55.378, -3.436),
    "london": (51.508, -0.128),
    "poland": (51.920, 19.145), "warsaw": (52.229, 21.012),
    "netherlands": (52.133, 5.291), "amsterdam": (52.373, 4.890),
    "greece": (39.074, 21.824), "athens": (37.979, 23.716),
    "romania": (45.943, 24.967), "bucharest": (44.426, 26.103),
    "serbia": (44.017, 21.006), "belgrade": (44.787, 20.457),
    "europe": (54.526, 15.255),

    # Americas
    "united states": (37.090, -95.713), "usa": (37.090, -95.713),
    "new york": (40.713, -74.006), "los angeles": (34.052, -118.244),
    "chicago": (41.878, -87.630), "miami": (25.774, -80.190),
    "texas": (31.000, -100.000), "california": (36.778, -119.418),
    "canada": (56.130, -106.347), "toronto": (43.653, -79.383),
    "mexico": (23.635, -102.553), "mexico city": (19.433, -99.133),
    "brazil": (-14.235, -51.925), "são paulo": (-23.550, -46.633),
    "rio de janeiro": (-22.907, -43.173), "brasilia": (-15.780, -47.930),
    "colombia": (4.571, -74.297), "bogota": (4.711, -74.073),
    "peru": (-9.190, -75.016), "lima": (-12.046, -77.043),
    "argentina": (-38.416, -63.617), "buenos aires": (-34.604, -58.382),
    "venezuela": (6.424, -66.590), "caracas": (10.480, -66.904),
    "chile": (-35.675, -71.543), "santiago": (-33.459, -70.648),
    "ecuador": (-1.832, -78.183), "quito": (-0.229, -78.525),
    "bolivia": (-16.291, -63.589), "la paz": (-16.500, -68.150),
    "haiti": (18.972, -72.285), "port-au-prince": (18.543, -72.338),
    "cuba": (21.522, -77.782), "havana": (23.113, -82.367),
    "dominican republic": (18.736, -70.163),
    "guatemala": (15.784, -90.231), "panama": (8.538, -80.783),
    "el salvador": (13.794, -88.897), "honduras": (15.200, -86.242),
    "nicaragua": (12.865, -85.207),
    "south america": (-8.784, -55.492), "latin america": (2.0, -78.0),
    "caribbean": (18.0, -72.0),

    # Oceania
    "australia": (-25.274, 133.775), "sydney": (-33.869, 151.209), "melbourne": (-37.814, 144.963),
    "new zealand": (-40.901, 174.886), "auckland": (-36.848, 174.763),
    "papua new guinea": (-6.315, 143.955), "port moresby": (-9.443, 147.180),
}

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
PAGES = ["Overview", "Global News", "India Focus", "Expert Advisories", "Outbreak Map", "Vaccines & Treatments"]

DISEASE_KEYWORDS = [
    "disease","virus","outbreak","epidemic","pandemic","infection","pathogen",
    "vaccine","flu","dengue","cholera","mpox","H5N1","WHO","CDC","ICMR",
    "health alert","antimicrobial","resistant","fever","zoonotic","emerging",
    "surveillance","quarantine","antiviral","mortality","morbidity","contagious","immunization",
]
INDIA_KEYWORDS = ["india","indian","icmr","mohfw","delhi","mumbai","kerala","bengal","rajasthan","chennai","hyderabad","pune","kolkata"]
EXPERT_KEYWORDS = ["expert","scientist","researcher","epidemiologist","virologist","government","ministry","advisory","warning","alert","WHO","CDC","lancet","nejm","study","research","policy"]

RSS_SOURCES = {
    "who_don": [("WHO DON","#1565c0","https://www.who.int/rss-feeds/news-english.xml")],
    "global":  [
        ("WHO",    "#1565c0","https://www.who.int/rss-feeds/news-english.xml"),
        ("Reuters","#c0392b","https://feeds.reuters.com/reuters/healthNews"),
        ("CDC",    "#27ae60","https://tools.cdc.gov/api/v2/resources/media/132608.rss"),
    ],
    "india": [
        ("The Hindu",      "#b71c1c","https://www.thehindu.com/sci-tech/health/feeder/default.rss"),
        ("Times of India", "#e65100","https://timesofindia.indiatimes.com/rssfeeds/3908999.cms"),
        ("NDTV Health",    "#1a237e","https://feeds.feedburner.com/ndtvnews-health"),
    ],
    "journals": [
        ("The Lancet","#6a1b9a","https://www.thelancet.com/rssfeed/lancet_online.xml"),
        ("NEJM",      "#004d40","https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm"),
        ("STAT News", "#f57f17","https://www.statnews.com/feed/"),
    ],
    "vaccines": [
        ("WHO",      "#1565c0","https://www.who.int/rss-feeds/news-english.xml"),
        ("Reuters",  "#c0392b","https://feeds.reuters.com/reuters/healthNews"),
        ("STAT News","#f57f17","https://www.statnews.com/feed/"),
    ],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DiseaseIntelligence/2.0)"}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "page" not in st.session_state:
    st.session_state.page = "Overview"

# Per-render dedup: reset at the top of every run so each full page render
# starts fresh. Articles seen in section A won't appear in section B.
if "seen_urls" not in st.session_state:
    st.session_state.seen_urls = set()

# ══════════════════════════════════════════════════════════════════════════════
# RSS HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()

def parse_date(raw):
    for fmt in ("%a, %d %b %Y %H:%M:%S %z","%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z","%Y-%m-%dT%H:%M:%SZ","%Y-%m-%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%d %b %Y")
        except Exception:
            pass
    return raw[:10] if raw else ""

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rss(url: str) -> list:
    try:
        r = requests.get(url, timeout=12, headers=HEADERS)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        for item in list(root.iter("item")) + list(root.iter("{http://www.w3.org/2005/Atom}entry")):
            title = strip_html(item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "")
            link  = (item.findtext("link") or item.findtext("{http://www.w3.org/2005/Atom}link") or "").strip()
            if not link:
                le = item.find("{http://www.w3.org/2005/Atom}link")
                link = le.get("href","") if le is not None else ""
            desc = strip_html(
                item.findtext("description") or
                item.findtext("{http://www.w3.org/2005/Atom}summary") or
                item.findtext("{http://www.w3.org/2005/Atom}content") or ""
            )[:220]
            pub = parse_date(
                item.findtext("pubDate") or
                item.findtext("{http://www.w3.org/2005/Atom}published") or
                item.findtext("{http://www.w3.org/2005/Atom}updated") or ""
            )
            if title and link:
                items.append({"title": title, "url": link, "description": desc, "date": pub})
        return items
    except Exception:
        return []

def fetch_multi(sources, keywords=None, max_per_source=8):
    results, seen_titles = [], set()
    for label, color, url in sources:
        count = 0
        for item in fetch_rss(url):
            if count >= max_per_source:
                break
            text = (item["title"] + " " + item["description"]).lower()
            if keywords and not any(k.lower() in text for k in keywords):
                continue
            key = item["title"][:60].lower().strip()
            if key in seen_titles:
                continue
            seen_titles.add(key)
            item["source_label"] = label
            item["source_color"]  = color
            results.append(item)
            count += 1
    return results

# ══════════════════════════════════════════════════════════════════════════════
# WHO DISEASE OUTBREAK NEWS — tries JSON API, falls back to RSS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_who_don(limit: int = 50) -> list:
    # 1. Official JSON API
    try:
        url = f"https://www.who.int/api/news/diseaseoutbreaknews?sf_culture=en&$top={limit}&$orderby=NewsDate+desc"
        r = requests.get(url, timeout=14, headers=HEADERS)
        r.raise_for_status()
        raw = r.json()
        items = raw if isinstance(raw, list) else raw.get("value", raw.get("items", []))
        results = []
        for item in items:
            title   = strip_html(item.get("Title") or item.get("title") or "")
            summary = strip_html(item.get("Summary") or item.get("summary") or item.get("Text") or "")[:250]
            date_raw = (item.get("NewsDate") or item.get("PublicationDate") or item.get("DateCreated") or "")[:10]
            date    = parse_date(date_raw) if date_raw else ""
            url_part = item.get("ItemDefaultUrl") or item.get("Url") or item.get("UrlName") or ""
            link = ("https://www.who.int" + url_part) if url_part and not url_part.startswith("http") else url_part
            if not link:
                link = "https://www.who.int/emergencies/disease-outbreak-news"
            if title:
                results.append({"title": title, "summary": summary, "date": date, "url": link})
        if results:
            return results
    except Exception:
        pass
    # 2. RSS fallback
    try:
        r = requests.get("https://www.who.int/rss-feeds/news-english.xml", timeout=12, headers=HEADERS)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        results = []
        for item in root.iter("item"):
            title = strip_html(item.findtext("title") or "")
            link  = (item.findtext("link") or "").strip()
            desc  = strip_html(item.findtext("description") or "")[:250]
            pub   = parse_date(item.findtext("pubDate") or "")
            if title and link:
                results.append({"title": title, "summary": desc, "date": pub, "url": link})
        return results[:limit]
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════════════════════
# MAP: match place names in article text against PLACES dict
# ══════════════════════════════════════════════════════════════════════════════
def build_outbreak_map(articles: list) -> folium.Map:
    """
    Scans title+description of each article for place names from PLACES dict.
    Places a circle marker for each match, linked to the article URL.
    Multiple articles for the same place stack into one popup.
    """
    # Sort by length desc so "new york" matches before "york"
    sorted_places = sorted(PLACES.keys(), key=len, reverse=True)

    # Collect: place -> list of matching articles
    place_hits: dict = {}
    for art in articles:
        text = (art.get("title","") + " " + art.get("description","") + " " + art.get("summary","")).lower()
        for place in sorted_places:
            if place in text:
                # Avoid substring matches for short names (e.g. "mali" inside "somalia")
                pattern = r'\b' + re.escape(place) + r'\b'
                if re.search(pattern, text):
                    if place not in place_hits:
                        place_hits[place] = []
                    # Avoid adding the same article to the same place twice
                    if not any(a["url"] == art["url"] for a in place_hits[place]):
                        place_hits[place].append(art)

    m = folium.Map(location=[20, 15], zoom_start=2, tiles="CartoDB positron", prefer_canvas=True)

    for place, arts in place_hits.items():
        lat, lon = PLACES[place]
        n = len(arts)
        color  = "#c0392b" if n >= 3 else "#e67e22" if n == 2 else "#1565c0"
        radius = min(7 + n * 3, 22)
        art_html = "".join([
            f"<div style='margin:5px 0;font-size:12px'>"
            f"<a href='{a['url']}' target='_blank' style='color:#1565c0;font-weight:600'>"
            f"{a['title'][:70]}{'…' if len(a['title'])>70 else ''}</a>"
            f"<span style='color:#999;margin-left:6px;font-size:11px'>{a.get('date','')}</span>"
            f"</div>"
            for a in arts[:5]
        ])
        popup_html = (
            f"<div style='font-family:sans-serif;min-width:240px;max-width:340px;padding:4px'>"
            f"<b style='font-size:14px;color:#0d1b2a'>{place.title()}</b>"
            f"<div style='font-size:11px;color:#888;margin:3px 0 8px'>{n} article{'s' if n>1 else ''}</div>"
            f"<hr style='margin:0 0 8px;border:none;border-top:1px solid #eee'>"
            f"{art_html}"
            f"</div>"
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius, color=color,
            fill=True, fill_color=color, fill_opacity=0.65,
            popup=folium.Popup(popup_html, max_width=360),
            tooltip=f"{place.title()} — {n} article{'s' if n>1 else ''}",
        ).add_to(m)

    return m

# ══════════════════════════════════════════════════════════════════════════════
# RENDER HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def dedup_articles(articles: list) -> list:
    """Remove articles already shown this session."""
    fresh = []
    for a in articles:
        url = a.get("url","")
        if url and url not in st.session_state.seen_urls:
            fresh.append(a)
            st.session_state.seen_urls.add(url)
    return fresh

def article_card_html(a):
    title = a.get("title","").strip()
    url   = a.get("url","#")
    label = a.get("source_label","")
    color = a.get("source_color","#1565c0")
    desc  = a.get("description","").strip()[:170]
    date  = a.get("date","")
    desc_html = f'<div class="article-desc">{desc}</div>' if desc else ""
    return (
        f'<a class="article-card" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<div class="article-meta"><span class="source-badge" style="background:{color};color:#fff">{label}</span>&nbsp;{date}</div>'
        f'<div class="article-title">{title}</div>'
        f'{desc_html}'
        f'<div class="article-link">Read full article &rarr;</div>'
        f'</a>'
    )

def don_card_html(d):
    title = d.get("title","").strip()
    url   = d.get("url","#")
    date  = d.get("date","")
    return (
        f'<a class="don-card" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<div class="don-title">{title}</div>'
        f'<div class="don-meta">{date}</div>'
        f'</a>'
    )

def render_grid(articles, cols=2, fallback_links="", max_items=10):
    fresh = dedup_articles(articles)
    # Filter out articles with no meaningful title
    fresh = [a for a in fresh if a.get("title", "").strip()]
    # Sort by date descending and keep only top max_items
    def _sort_key(a):
        d = a.get("date", "")
        try:
            return datetime.strptime(d, "%d %b %Y")
        except Exception:
            return datetime.min
    fresh = sorted(fresh, key=_sort_key, reverse=True)[:max_items]
    if not fresh:
        st.markdown(
            f'<div class="feed-error">No articles available or feed unreachable. Sources: {fallback_links}</div>',
            unsafe_allow_html=True
        )
        return
    # Build per-column HTML and emit each column as ONE st.markdown call.
    # One st.markdown per card causes Streamlit to split/duplicate card rendering.
    col_html = [""] * cols
    for i, a in enumerate(fresh):
        col_html[i % cols] += article_card_html(a)
    columns = st.columns(cols)
    for col, html in zip(columns, col_html):
        if html:
            with col:
                st.markdown(f'<div>{html}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR — pure st.button, wrapped in a styled div
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="nav-bar-wrap">', unsafe_allow_html=True)
nav_cols = st.columns([1.5] * len(PAGES) + [1.4])
for col, p in zip(nav_cols[:-1], PAGES):
    with col:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
            st.session_state.seen_urls = set()
            st.rerun()
with nav_cols[-1]:
    st.markdown('<div class="nav-status"><span class="pulse-dot"></span>Live · WHO</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

page = st.session_state.page

# Sub-header
st.markdown(
    f'<div style="font-size:0.8rem;color:#6b7c93;margin-bottom:16px;padding:2px 2px 10px 2px;border-bottom:1px solid #e8ecf0;">'
    f'<b style="color:#0d1b2a">{page}</b> &nbsp;·&nbsp; '
    f'Global Epidemic &amp; Pandemic Preparedness &nbsp;·&nbsp; {datetime.utcnow().strftime("%A, %d %B %Y")} &nbsp;·&nbsp;'
    f'<span style="color:#a0aebe;">Updated {datetime.utcnow().strftime("%H:%M")} UTC</span>'
    f'</div>',
    unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

if page == "Overview":
    with st.spinner("Fetching WHO Disease Outbreak News…"):
        don_items = fetch_who_don(limit=50)

    total_reports      = len(don_items)
    this_month         = datetime.utcnow().strftime("%Y-%m")
    recent_count       = sum(1 for d in don_items if d.get("date","").startswith(this_month))

    kpi_cols = st.columns(2)
    for col, num, label, color in zip(
        kpi_cols,
        [total_reports, recent_count],
        ["WHO Reports Fetched", "Reports This Month"],
        ["#c0392b", "#2980b9"],
    ):
        with col:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-num" style="color:{color}">{num}</div>'
                f'<div class="kpi-label">{label}</div></div>',
                unsafe_allow_html=True
            )
    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.3, 1], gap="large")
    with col_left:
        st.markdown('<div class="section-title">WHO Disease Outbreak Reports</div>', unsafe_allow_html=True)
        if don_items:
            html = "".join(don_card_html(d) for d in don_items[:10] if d.get("title","").strip())
            for d in don_items[:10]:
                st.session_state.seen_urls.add(d["url"])
            st.markdown(f'<div>{html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="feed-error">Could not reach WHO. '
                '<a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">Visit WHO DON directly</a>.</div>',
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown('<div class="section-title">Latest Health News</div>', unsafe_allow_html=True)
        with st.spinner("Loading..."):
            _news_sources = [
                ("Reuters",   "#c0392b", "https://feeds.reuters.com/reuters/healthNews"),
                ("STAT News", "#f57f17", "https://www.statnews.com/feed/"),
                ("CDC",       "#27ae60", "https://tools.cdc.gov/api/v2/resources/media/132608.rss"),
            ]
            news = fetch_multi(_news_sources, keywords=DISEASE_KEYWORDS, max_per_source=6)
        news = [a for a in news if a.get("title","").strip()]
        def _sk(a):
            try: return datetime.strptime(a.get("date",""), "%d %b %Y")
            except: return datetime.min
        news = sorted(news, key=_sk, reverse=True)[:10]
        if news:
            cards_html = "".join(article_card_html(a) for a in news)
            st.markdown(f'<div>{cards_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="feed-error">Health news feeds unreachable. '
                '<a href="https://www.statnews.com" target="_blank">STAT News</a> | '
                '<a href="https://www.reuters.com/business/healthcare-pharmaceuticals/" target="_blank">Reuters Health</a></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Live Outbreak Map</div>', unsafe_allow_html=True)
    st.markdown("""<div class="disclaimer">
      Markers are placed by scanning live WHO &amp; Reuters articles for location mentions.
      Each marker links to the source article. Circle size = number of articles mentioning that location.
    </div>""", unsafe_allow_html=True)

    with st.spinner("Building map from live articles…"):
        all_articles = fetch_multi(RSS_SOURCES["global"], keywords=DISEASE_KEYWORDS, max_per_source=20)
        seen_map_urls = {a["url"] for a in all_articles}
        if don_items:
            for d in don_items:
                if "outbreak" not in d["title"].lower():
                    continue
                if d["url"] in seen_map_urls:
                    continue
                seen_map_urls.add(d["url"])
                all_articles.append({"title": d["title"], "description": d.get("summary",""), "url": d["url"], "date": d.get("date","")})
    st_folium(build_outbreak_map(all_articles), height=380, use_container_width=True)


elif page == "Global News":
    st.markdown('<div class="section-title">Global Disease and Epidemic News</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["All Sources", "WHO Bulletins", "Reuters Health"])
    with tab1:
        with st.spinner("Loading…"):
            articles = fetch_multi(RSS_SOURCES["global"], keywords=DISEASE_KEYWORDS, max_per_source=10)
        render_grid(articles, cols=3,
            fallback_links='<a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO</a> | '
                           '<a href="https://www.reuters.com/business/healthcare-pharmaceuticals/" target="_blank">Reuters</a>')
    with tab2:
        with st.spinner("Loading…"):
            who_articles = fetch_multi(RSS_SOURCES["who_don"], keywords=DISEASE_KEYWORDS, max_per_source=15)
        render_grid(who_articles, cols=3,
            fallback_links='<a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO DON</a>')
    with tab3:
        with st.spinner("Loading…"):
            reuters = fetch_multi(
                [("Reuters","#c0392b","https://feeds.reuters.com/reuters/healthNews")],
                keywords=DISEASE_KEYWORDS, max_per_source=15
            )
        render_grid(reuters, cols=3,
            fallback_links='<a href="https://www.reuters.com/business/healthcare-pharmaceuticals/" target="_blank">Reuters Health</a>')


elif page == "India Focus":
    st.markdown('<div class="section-title">India Disease Intelligence</div>', unsafe_allow_html=True)
    with st.spinner("Loading WHO reports…"):
        don_items = fetch_who_don(limit=60)
    india_terms = ["india","indian","delhi","mumbai","kerala","bengal","rajasthan","chennai","kolkata","hyderabad","pune"]
    india_don = [
        d for d in don_items
        if any(t in (d.get("title","") + " " + d.get("summary","")).lower() for t in india_terms)
    ]

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown('<div class="section-subtitle">WHO Reports — India</div>', unsafe_allow_html=True)
        if india_don:
            html = "".join(don_card_html(d) for d in india_don[:10] if d.get("title","").strip())
            for d in india_don[:10]:
                st.session_state.seen_urls.add(d["url"])
            st.markdown(f'<div>{html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="feed-error">No recent WHO DON reports mentioning India. '
                'Check <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO DON</a>.</div>',
                unsafe_allow_html=True
            )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Official India Health Authorities</div>', unsafe_allow_html=True)
        for name, url in [
            ("Ministry of Health and Family Welfare", "https://www.mohfw.gov.in"),
            ("ICMR — Indian Council of Medical Research", "https://www.icmr.gov.in"),
            ("NCDC — National Centre for Disease Control", "https://ncdc.mohfw.gov.in"),
            ("IDSP — Integrated Disease Surveillance", "https://idsp.mohfw.gov.in"),
        ]:
            st.markdown(f'<a class="authority-link" href="{url}" target="_blank">{name} &rarr;</a>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-subtitle">India Health News</div>', unsafe_allow_html=True)
        with st.spinner("Loading India feeds…"):
            india_articles = fetch_multi(
                RSS_SOURCES["india"], keywords=DISEASE_KEYWORDS + INDIA_KEYWORDS, max_per_source=6
            )
        render_grid(india_articles, cols=1,
            fallback_links='<a href="https://www.thehindu.com/sci-tech/health/" target="_blank">The Hindu Health</a> | '
                           '<a href="https://timesofindia.indiatimes.com/life-style/health-fitness" target="_blank">TOI Health</a>')


elif page == "Expert Advisories":
    st.markdown('<div class="section-title">Expert and Government Advisories</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["WHO / CDC", "Medical Journals", "Government Measures"])
    with tab1:
        with st.spinner("Loading…"):
            items = fetch_multi(RSS_SOURCES["who_don"], keywords=DISEASE_KEYWORDS, max_per_source=12)
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.who.int/news" target="_blank">WHO</a>')
    with tab2:
        with st.spinner("Loading…"):
            items = fetch_multi(RSS_SOURCES["journals"], keywords=DISEASE_KEYWORDS + EXPERT_KEYWORDS, max_per_source=8)
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.thelancet.com" target="_blank">The Lancet</a> | '
                           '<a href="https://www.nejm.org" target="_blank">NEJM</a>')
    with tab3:
        with st.spinner("Loading…"):
            gov_sources = [
                ("WHO",    "#1565c0","https://www.who.int/rss-feeds/news-english.xml"),
                ("Reuters","#c0392b","https://feeds.reuters.com/reuters/healthNews"),
            ]
            items = fetch_multi(
                gov_sources,
                keywords=EXPERT_KEYWORDS + ["government","ministry","policy","regulation","mandate"],
                max_per_source=10
            )
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.who.int/news" target="_blank">WHO</a>')


elif page == "Outbreak Map":
    st.markdown('<div class="section-title">Live Outbreak Map</div>', unsafe_allow_html=True)
    st.markdown("""<div class="disclaimer">
      <strong>How it works:</strong> Articles from WHO, Reuters, and CDC are scanned for location mentions
      (cities, countries, regions). Each location found gets a marker linked to the source article.
      Circle size = number of articles mentioning that location. All data is live from RSS feeds.
    </div>""", unsafe_allow_html=True)

    with st.spinner("Loading articles…"):
        all_articles = fetch_multi(RSS_SOURCES["global"], keywords=DISEASE_KEYWORDS, max_per_source=30)
        seen_map_urls = {a["url"] for a in all_articles}
        don_items = fetch_who_don(limit=60)
        for d in don_items:
            # Only include WHO DON items whose title contains "outbreak"
            if "outbreak" not in d["title"].lower():
                continue
            if d["url"] in seen_map_urls:
                continue
            seen_map_urls.add(d["url"])
            all_articles.append({
                "title": d["title"],
                "description": d.get("summary",""),
                "url": d["url"],
                "date": d.get("date",""),
                "source_label": "WHO DON",
                "source_color": "#1565c0",
            })

    st_folium(build_outbreak_map(all_articles), height=540, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Article Reference Table</div>', unsafe_allow_html=True)

    # Show all articles used to build the map
    sorted_articles = sorted(all_articles, key=lambda x: x.get("date",""), reverse=True)
    rows = "".join([
        f"<tr>"
        f"<td><span class='source-badge' style='background:{a.get('source_color','#888')};color:#fff'>{a.get('source_label','')}</span></td>"
        f"<td><a href='{a['url']}' target='_blank' style='color:#1565c0'>{a['title'][:80]}{'…' if len(a['title'])>80 else ''}</a></td>"
        f"<td>{a.get('date','')}</td>"
        f"</tr>"
        for a in sorted_articles[:50]
    ])
    st.markdown(
        f'<table class="data-table">'
        f'<thead><tr><th>Source</th><th>Article</th><th>Date</th></tr></thead>'
        f'<tbody>{rows}</tbody>'
        f'</table>',
        unsafe_allow_html=True
    )


elif page == "Vaccines & Treatments":
    st.markdown('<div class="section-title">Vaccines and New Treatments</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["New Vaccines", "Antiviral Drugs", "Clinical Trials"])
    with tab1:
        with st.spinner("Loading…"):
            items = fetch_multi(
                RSS_SOURCES["vaccines"],
                keywords=["vaccine","vaccination","immunization","approved","rollout","efficacy","booster","mRNA"],
                max_per_source=8
            )
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.who.int/news-room/vaccines" target="_blank">WHO Vaccines</a>')
    with tab2:
        with st.spinner("Loading…"):
            items = fetch_multi(
                RSS_SOURCES["vaccines"],
                keywords=["antiviral","drug","treatment","therapy","approved","FDA","EMA","medication","pill"],
                max_per_source=8
            )
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.fda.gov/drugs/drug-approvals-and-databases/drug-approvals" target="_blank">FDA</a>')
    with tab3:
        with st.spinner("Loading…"):
            trial_sources = [
                ("STAT News","#f57f17","https://www.statnews.com/feed/"),
                ("The Lancet","#6a1b9a","https://www.thelancet.com/rssfeed/lancet_online.xml"),
                ("NEJM",     "#004d40","https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm"),
            ]
            items = fetch_multi(
                trial_sources,
                keywords=["clinical trial","phase 2","phase 3","trial results","randomized","placebo","study"],
                max_per_source=8
            )
        render_grid(items, cols=2,
            fallback_links='<a href="https://clinicaltrials.gov" target="_blank">ClinicalTrials.gov</a>')

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">'
    'Data: <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO DON</a>'
    ' · <a href="https://feeds.reuters.com/reuters/healthNews" target="_blank">Reuters</a>'
    ' · <a href="https://www.thelancet.com" target="_blank">The Lancet</a>'
    ' · <a href="https://www.nejm.org" target="_blank">NEJM</a>'
    ' · <a href="https://www.statnews.com" target="_blank">STAT News</a>'
    ' &nbsp;·&nbsp; For internal clinical use only'
    '</div>',
    unsafe_allow_html=True
)