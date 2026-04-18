import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
import xml.etree.ElementTree as ET
import re
import time

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

/* ── Force light theme ── */
html, body, [class*="css"],
[data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: #f4f5f7 !important;
    color: #1a1a2e !important;
    color-scheme: light !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"]        { display: none !important; }
.block-container { padding: 0 1.5rem 2rem 1.5rem !important; max-width: 1600px; }
div[data-testid="stDecoration"]  { display: none; }

/* ══════════════════════════════════
   NAVBAR  — pure HTML/CSS, no JS
   ══════════════════════════════════ */
.navbar {
    position: sticky; top: 0; z-index: 999;
    background: #0d1b2a;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.18);
    display: flex; align-items: center;
    padding: 0 20px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
/* hamburger checkbox — hidden */
#nav-toggle { display: none; }

.hamburger {
    display: none;
    flex-direction: column; justify-content: center; gap: 5px;
    cursor: pointer; padding: 14px 0; margin-left: auto;
}
.hamburger span {
    display: block; width: 22px; height: 2px;
    background: #c8d6e5; border-radius: 2px;
    transition: 0.2s;
}

.nav-links {
    display: flex; align-items: center; flex: 1;
}
.nav-links a {
    font-size: 0.82rem; font-weight: 600;
    color: #c8d6e5 !important; text-decoration: none !important;
    padding: 18px 14px;
    border-bottom: 3px solid transparent;
    transition: color 0.15s, border-color 0.15s;
    white-space: nowrap;
}
.nav-links a:hover       { color: #fff !important; border-bottom-color: #4a8fd4; }
.nav-links a.active      { color: #fff !important; border-bottom-color: #1565c0; background: rgba(21,101,192,0.12); }
.nav-spacer { flex: 1; }
.nav-status {
    display: flex; align-items: center; gap: 7px;
    font-size: 0.72rem; font-weight: 600; color: #27ae60 !important;
    background: rgba(39,174,96,0.12); border: 1px solid rgba(39,174,96,0.3);
    border-radius: 20px; padding: 6px 12px; white-space: nowrap;
}
.pulse-dot {
    width: 7px; height: 7px; background: #27ae60;
    border-radius: 50%; animation: pulse 2s infinite; display: inline-block;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.3)} }

/* ── Mobile navbar ── */
@media (max-width: 768px) {
    .hamburger { display: flex; }
    .nav-links {
        display: none; flex-direction: column; width: 100%;
        padding-bottom: 10px;
    }
    #nav-toggle:checked ~ .nav-links { display: flex; }
    .nav-links a { padding: 12px 4px; border-bottom: none; border-left: 3px solid transparent; }
    .nav-links a.active { border-left-color: #1565c0; border-bottom: none; }
    .nav-status { margin-bottom: 10px; }
}

/* ── KPI cards ── */
.kpi-card { background: #fff; border: 1px solid #e0e6ed; border-radius: 10px; padding: 20px 24px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
.kpi-num  { font-size: 2.4rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.kpi-label{ font-size: 0.78rem; font-weight: 500; color: #6b7c93; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }

/* ── Section titles ── */
.section-title    { font-size: 1.05rem; font-weight: 700; color: #0d1b2a; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #1565c0; display: inline-block; }
.section-subtitle { font-size: 0.9rem; font-weight: 600; color: #1a3a5c; margin-bottom: 10px; }

/* ── DON report card ── */
.don-card { display:block; background:#fff; border:1px solid #e0e6ed; border-left:4px solid #1565c0; border-radius:8px; padding:14px 16px; margin-bottom:10px; text-decoration:none !important; transition:box-shadow 0.15s; }
.don-card:hover { box-shadow:0 4px 14px rgba(0,0,0,0.08); }
.don-title { font-size:0.88rem; font-weight:700; color:#0d1b2a; line-height:1.45; margin-bottom:6px; }
.don-meta  { font-size:0.72rem; color:#6b7c93; }
.don-link  { font-size:0.75rem; font-weight:600; color:#1565c0; margin-top:8px; }

/* ── News article card ── */
.article-card { display:block; background:#fff; border:1px solid #e0e6ed; border-radius:10px; padding:18px; margin-bottom:14px; text-decoration:none !important; transition:transform 0.15s,box-shadow 0.15s; }
.article-card:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,0.09); border-color:#1565c0; }
.article-meta  { font-size:0.72rem; color:#1565c0; font-weight:600; margin-bottom:7px; }
.article-title { font-size:0.88rem; font-weight:700; color:#0d1b2a; line-height:1.45; margin-bottom:8px; }
.article-desc  { font-size:0.8rem; color:#5a6a7e; line-height:1.5; }
.article-link  { font-size:0.75rem; font-weight:600; color:#1565c0; margin-top:10px; }

.source-badge { display:inline-block; font-size:0.68rem; font-weight:700; padding:2px 8px; border-radius:4px; margin-right:6px; letter-spacing:0.04em; text-transform:uppercase; }

/* ── Authority links ── */
.authority-link { display:block; text-align:center; background:#fff; border:1px solid #c5d3e0; border-radius:8px; padding:12px; font-size:0.82rem; font-weight:600; color:#1565c0 !important; text-decoration:none !important; transition:background 0.15s; margin-bottom:10px; }
.authority-link:hover { background:#e8f0fe; }

/* ── Disclaimer box ── */
.disclaimer { background:#f0f4ff; border:1px solid #c5d3e0; border-radius:8px; padding:12px 16px; font-size:0.78rem; color:#34495e; margin-bottom:16px; line-height:1.6; }
.disclaimer a { color:#1565c0; }

/* ── Data table ── */
.data-table { width:100%; border-collapse:collapse; background:#fff; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.04); font-size:0.85rem; }
.data-table th { background:#0d1b2a; color:#c8d6e5; font-weight:600; font-size:0.75rem; letter-spacing:0.08em; text-transform:uppercase; padding:12px 16px; text-align:left; }
.data-table td { padding:11px 16px; border-bottom:1px solid #edf0f4; color:#2c3e50; }
.data-table tr:last-child td { border-bottom:none; }
.data-table tr:hover td { background:#f7f9fc; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap:0; border-bottom:2px solid #e0e6ed !important; background:transparent !important; }
.stTabs [data-baseweb="tab"] { font-size:0.85rem !important; font-weight:600 !important; color:#6b7c93 !important; padding:10px 20px !important; border-radius:0 !important; background:transparent !important; }
.stTabs [aria-selected="true"] { color:#1565c0 !important; border-bottom:2px solid #1565c0 !important; }

/* ── Feed error / footer ── */
.feed-error { background:#fff8e1; border:1px solid #ffe082; border-radius:8px; padding:14px 18px; font-size:0.83rem; color:#6d4c00; }
.feed-error a { color:#1565c0; font-weight:600; }
.footer { text-align:center; font-size:0.72rem; color:#a0aebe; margin-top:40px; padding-top:16px; border-top:1px solid #e0e6ed; }
.footer a { color:#7a9cc4; }
</style>
""", unsafe_allow_html=True)

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

COUNTRY_ALIASES = {
    "drc":"Democratic Republic of the Congo",
    "dr congo":"Democratic Republic of the Congo",
    "congo":"Republic of the Congo",
    "usa":"United States","uk":"United Kingdom","uae":"United Arab Emirates",
    "car":"Central African Republic","pdr lao":"Laos","lao pdr":"Laos",
    "viet nam":"Vietnam","republic of korea":"South Korea","dprk":"North Korea",
    "iran (islamic republic of)":"Iran","russian federation":"Russia",
    "syrian arab republic":"Syria","tanzania, united republic of":"Tanzania",
    "bolivia (plurinational state of)":"Bolivia",
    "venezuela (bolivarian republic of)":"Venezuela",
}

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL ARTICLE DEDUP
# ══════════════════════════════════════════════════════════════════════════════
if "seen_urls" not in st.session_state:
    st.session_state.seen_urls = set()
if "page" not in st.session_state:
    st.session_state.page = "Overview"

def filter_unseen(articles):
    return [a for a in articles if a.get("url") and a["url"] not in st.session_state.seen_urls]

def register_articles(articles):
    for a in articles:
        if a.get("url"):
            st.session_state.seen_urls.add(a["url"])

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

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DiseaseIntelligence/2.0)"}

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
# WHO DISEASE OUTBREAK NEWS
# Tries the JSON API first; falls back to RSS.
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_who_don(limit: int = 50) -> list:
    # 1. Official WHO JSON API
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
            link    = ("https://www.who.int" + url_part) if url_part and not url_part.startswith("http") else url_part
            if not link:
                link = "https://www.who.int/emergencies/disease-outbreak-news"
            if title:
                results.append({"title": title, "summary": summary, "date": date, "url": link})
        if results:
            return results
    except Exception:
        pass

    # 2. WHO RSS fallback
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
# LOCATION EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════
def extract_location(title: str) -> str:
    """
    WHO DON titles: 'Mpox – Democratic Republic of the Congo'
    Extract the part after ' – ' or ' - '.
    """
    for sep in [" \u2013 ", " \u2014 ", " - "]:
        if sep in title:
            loc = title.split(sep)[-1].strip()
            loc = re.sub(r"\s*\(update.*?\)\s*$", "", loc, flags=re.IGNORECASE).strip()
            loc = re.sub(r"\s*\(.*?\)\s*$", "", loc).strip()
            if 2 <= len(loc) <= 80:
                return loc
    # Also handle em-dash without spaces
    for sep in ["\u2013", "\u2014"]:
        if sep in title:
            loc = title.split(sep)[-1].strip()
            loc = re.sub(r"\s*\(.*?\)\s*$", "", loc).strip()
            if 2 <= len(loc) <= 80:
                return loc
    return ""

# ══════════════════════════════════════════════════════════════════════════════
# GEOCODING via Nominatim — each location cached individually so we don't
# redo geocoding on every render, and so cache_data can hash the string arg.
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=86400, show_spinner=False)
def geocode_single(location: str) -> tuple:
    """Returns (lat, lon) or (None, None). Cached 24h per location string."""
    if not location:
        return None, None
    canonical = COUNTRY_ALIASES.get(location.lower().strip(), location.strip())
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": canonical, "format": "json", "limit": 1},
            headers={"User-Agent": "DiseaseIntelligence/2.0 (public health research tool; non-commercial)"},
            timeout=8,
        )
        r.raise_for_status()
        res = r.json()
        if res:
            return float(res[0]["lat"]), float(res[0]["lon"])
    except Exception:
        pass
    return None, None

def build_map_data(don_items: list) -> list:
    """
    Groups WHO DON items by extracted country, geocodes each unique country
    (with Nominatim rate-limit sleep between new requests), returns list of:
    { country, lat, lon, reports: [{title, date, url}] }
    """
    by_country = {}
    for item in don_items:
        loc = extract_location(item.get("title", ""))
        if not loc:
            continue
        key = loc.lower().strip()
        if key not in by_country:
            lat, lon = geocode_single(loc)
            if lat is None:
                continue
            # Only sleep if this was a fresh (uncached) lookup —
            # we can't know for sure, so we sleep briefly regardless
            time.sleep(0.15)
            by_country[key] = {
                "country": loc,
                "lat": lat,
                "lon": lon,
                "reports": [],
            }
        by_country[key]["reports"].append({
            "title": item.get("title", ""),
            "date":  item.get("date", ""),
            "url":   item.get("url", "#"),
        })
    return list(by_country.values())

def build_folium_map(map_data: list) -> folium.Map:
    m = folium.Map(location=[20, 15], zoom_start=2, tiles="CartoDB positron", prefer_canvas=True)
    for entry in map_data:
        n      = len(entry["reports"])
        color  = "#c0392b" if n >= 4 else "#e67e22" if n >= 2 else "#1565c0"
        radius = min(7 + n * 3, 22)
        report_html = "".join([
            f"<div style='margin:5px 0;font-size:12px'>"
            f"<a href='{r['url']}' target='_blank' style='color:#1565c0;font-weight:600'>"
            f"{r['title'][:75]}{'…' if len(r['title'])>75 else ''}</a>"
            f"<span style='color:#999;margin-left:6px;font-size:11px'>{r['date']}</span></div>"
            for r in entry["reports"]
        ])
        popup_html = (
            f"<div style='font-family:sans-serif;min-width:260px;max-width:360px;padding:4px'>"
            f"<b style='font-size:14px;color:#0d1b2a'>{entry['country']}</b>"
            f"<div style='font-size:11px;color:#888;margin:3px 0 8px'>{n} WHO report{'s' if n>1 else ''}</div>"
            f"<hr style='margin:0 0 8px;border:none;border-top:1px solid #eee'>"
            f"{report_html}"
            f"<div style='font-size:10px;color:#bbb;margin-top:8px'>"
            f"Source: <a href='https://www.who.int/emergencies/disease-outbreak-news' target='_blank'>WHO DON</a></div>"
            f"</div>"
        )
        folium.CircleMarker(
            location=[entry["lat"], entry["lon"]],
            radius=radius, color=color,
            fill=True, fill_color=color, fill_opacity=0.6,
            popup=folium.Popup(popup_html, max_width=380),
            tooltip=f"{entry['country']} — {n} WHO report{'s' if n>1 else ''}",
        ).add_to(m)
    return m

# ══════════════════════════════════════════════════════════════════════════════
# RENDER HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def article_card_html(a):
    title = a.get("title","")[:115]
    url   = a.get("url","#")
    label = a.get("source_label","")
    color = a.get("source_color","#1565c0")
    desc  = a.get("description","")[:170]
    date  = a.get("date","")
    return (
        f'<a class="article-card" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<div class="article-meta"><span class="source-badge" style="background:{color};color:#fff">{label}</span>{date}</div>'
        f'<div class="article-title">{title}</div>'
        f'<div class="article-desc">{desc}</div>'
        f'<div class="article-link">Read full article &rarr;</div>'
        f'</a>'
    )

def don_card_html(d):
    title   = d.get("title","")[:120]
    url     = d.get("url","#")
    date    = d.get("date","")
    summary = d.get("summary","")[:200]
    return (
        f'<a class="don-card" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<div class="don-title">{title}</div>'
        + (f'<div class="article-desc">{summary}</div>' if summary else "")
        + f'<div class="don-meta">WHO Disease Outbreak News &nbsp;·&nbsp; {date}</div>'
        f'<div class="don-link">Read WHO report &rarr;</div>'
        f'</a>'
    )

def render_grid(articles, cols=2, fallback_links=""):
    fresh = filter_unseen(articles)
    if not fresh:
        st.markdown(
            f'<div class="feed-error">No new articles available (already shown elsewhere or feed unavailable). '
            f'Sources: {fallback_links}</div>',
            unsafe_allow_html=True
        )
        return
    register_articles(fresh)
    columns = st.columns(cols)
    for i, a in enumerate(fresh):
        with columns[i % cols]:
            st.markdown(article_card_html(a), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR  — pure HTML, no JS dependency
# Navigation state is managed by query params + session_state.
# ══════════════════════════════════════════════════════════════════════════════
# Sync page from query params on first load
qp = st.query_params
if "p" in qp and qp["p"] in PAGES:
    st.session_state.page = qp["p"]

page = st.session_state.page

def nav_link(label, current):
    cls   = "active" if label == current else ""
    # URL encode spaces
    href  = f"?p={label.replace(' ', '+')}"
    return f'<a href="{href}" class="{cls}">{label}</a>'

nav_html = (
    '<nav class="navbar">'
    '<input type="checkbox" id="nav-toggle">'
    '<label class="hamburger" for="nav-toggle">'
    '<span></span><span></span><span></span>'
    '</label>'
    '<div class="nav-links">'
    + "".join(nav_link(p, page) for p in PAGES)
    + '<span class="nav-spacer"></span>'
    '<div class="nav-status"><span class="pulse-dot"></span>Live · WHO</div>'
    '</div>'
    '</nav>'
)
st.markdown(nav_html, unsafe_allow_html=True)

# Handle query param navigation (full page reload via href)
if "p" in qp and qp["p"] != st.session_state.page:
    st.session_state.page = qp["p"]
    st.session_state.seen_urls = set()
    st.rerun()

# Sub-header
st.markdown(
    f'<div style="font-size:0.8rem;color:#6b7c93;margin-bottom:16px;padding:2px 2px 10px 2px;border-bottom:1px solid #e8ecf0;">'
    f'<b style="color:#0d1b2a">{page}</b> &nbsp;·&nbsp;'
    f'Global Epidemic &amp; Pandemic Preparedness &nbsp;·&nbsp; {datetime.utcnow().strftime("%A, %d %B %Y")} &nbsp;·&nbsp;'
    f'<span style="color:#a0aebe;">Updated {datetime.utcnow().strftime("%H:%M")} UTC</span>'
    f'</div>',
    unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
if page == "Overview":
    with st.spinner("Fetching WHO Disease Outbreak News…"):
        don_items = fetch_who_don(limit=50)

    # KPI — 3 cards (removed "data source" card)
    total_reports     = len(don_items)
    countries_affected = len(set(
        extract_location(d["title"]) for d in don_items
        if extract_location(d["title"])
    ))
    this_month = datetime.utcnow().strftime("%Y-%m")
    recent_count = sum(1 for d in don_items if d.get("date","").startswith(this_month))

    kpi_cols = st.columns(3)
    for col, num, label, color in zip(
        kpi_cols,
        [total_reports, countries_affected, recent_count],
        ["WHO Reports (latest batch)", "Countries / Regions Affected", "Reports This Month"],
        ["#c0392b", "#e67e22", "#2980b9"],
    ):
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-num" style="color:{color}">{num}</div>'
                f'<div class="kpi-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.3, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-title">WHO Disease Outbreak Reports</div>', unsafe_allow_html=True)
        if don_items:
            for d in don_items[:15]:
                register_articles([{"url": d["url"]}])
                st.markdown(don_card_html(d), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="feed-error">Could not reach WHO. '
                '<a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">Visit WHO DON directly</a>.</div>',
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown('<div class="section-title">Latest Health News</div>', unsafe_allow_html=True)
        with st.spinner("Loading news…"):
            news = fetch_multi(RSS_SOURCES["global"], keywords=DISEASE_KEYWORDS, max_per_source=6)
        render_grid(news, cols=1,
            fallback_links='<a href="https://www.who.int/news" target="_blank">WHO</a> | '
                           '<a href="https://www.reuters.com/business/healthcare-pharmaceuticals/" target="_blank">Reuters</a>')

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Live Outbreak Map</div>', unsafe_allow_html=True)
    st.markdown("""<div class="disclaimer">
      <strong>About this map:</strong> Markers are placed from live
      <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO Disease Outbreak News</a>
      reports. The country is extracted from the report title (e.g. "Mpox – Congo") and geocoded via
      <a href="https://nominatim.openstreetmap.org" target="_blank">OpenStreetMap Nominatim</a>.
      Circle size = number of WHO reports for that location.
      <strong>No case counts or severity ratings are estimated or fabricated.</strong>
    </div>""", unsafe_allow_html=True)

    if don_items:
        with st.spinner("Geocoding outbreak locations (this may take ~30s on first load)…"):
            map_data = build_map_data(don_items)
        if map_data:
            st_folium(build_folium_map(map_data), height=380, use_container_width=True)
        else:
            st.warning("Map geocoding returned no results. Nominatim may be rate-limiting — refresh in 60 seconds.")
    else:
        st.info("WHO data unavailable. Map will load once WHO API is reachable.")

# ── GLOBAL NEWS ───────────────────────────────────────────────────────────────
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

# ── INDIA FOCUS ───────────────────────────────────────────────────────────────
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
            for d in india_don[:10]:
                register_articles([{"url": d["url"]}])
                st.markdown(don_card_html(d), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="feed-error">No recent WHO DON reports mentioning India in the current batch. '
                'Check <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO DON</a> directly.</div>',
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

# ── EXPERT ADVISORIES ─────────────────────────────────────────────────────────
elif page == "Expert Advisories":
    st.markdown('<div class="section-title">Expert and Government Advisories</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["WHO / CDC", "Medical Journals", "Government Measures"])
    with tab1:
        with st.spinner("Loading…"):
            items = fetch_multi(RSS_SOURCES["who_don"], keywords=DISEASE_KEYWORDS, max_per_source=12)
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.who.int/news" target="_blank">WHO</a> | '
                           '<a href="https://www.cdc.gov/media/dpk/diseases-and-conditions/index.html" target="_blank">CDC</a>')
    with tab2:
        with st.spinner("Loading…"):
            items = fetch_multi(RSS_SOURCES["journals"], keywords=DISEASE_KEYWORDS + EXPERT_KEYWORDS, max_per_source=8)
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.thelancet.com" target="_blank">The Lancet</a> | '
                           '<a href="https://www.nejm.org" target="_blank">NEJM</a> | '
                           '<a href="https://www.statnews.com" target="_blank">STAT News</a>')
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
            fallback_links='<a href="https://www.who.int/news" target="_blank">WHO</a> | '
                           '<a href="https://ecdc.europa.eu/en/threats-and-outbreaks" target="_blank">ECDC</a>')

# ── OUTBREAK MAP ──────────────────────────────────────────────────────────────
elif page == "Outbreak Map":
    st.markdown('<div class="section-title">Live WHO Outbreak Map</div>', unsafe_allow_html=True)
    st.markdown("""<div class="disclaimer">
      <strong>Data source:</strong> Every marker comes from an official
      <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO Disease Outbreak News</a>
      publication. Country extracted from report title, geocoded via
      <a href="https://nominatim.openstreetmap.org" target="_blank">OpenStreetMap Nominatim</a>.
      <strong>No case counts, severity ratings, or coordinates are hardcoded or estimated.</strong>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Fetching WHO reports…"):
        don_items = fetch_who_don(limit=60)

    if don_items:
        with st.spinner("Geocoding locations (cached after first run)…"):
            map_data = build_map_data(don_items)

        if map_data:
            st_folium(build_folium_map(map_data), height=540, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">WHO DON Reference Table</div>', unsafe_allow_html=True)
            sorted_data = sorted(map_data, key=lambda x: -len(x["reports"]))
            rows = "".join([
                f"<tr>"
                f"<td>{e['country']}</td>"
                f"<td style='text-align:center'>{len(e['reports'])}</td>"
                f"<td><a href='{e['reports'][0]['url']}' target='_blank' style='color:#1565c0'>"
                f"{e['reports'][0]['title'][:80]}{'…' if len(e['reports'][0]['title'])>80 else ''}</a></td>"
                f"<td>{e['reports'][0]['date']}</td>"
                f"</tr>"
                for e in sorted_data
            ])
            st.markdown(
                f'<table class="data-table">'
                f'<thead><tr><th>Country / Region</th><th>WHO Reports</th><th>Latest Report</th><th>Date</th></tr></thead>'
                f'<tbody>{rows}</tbody>'
                f'</table>',
                unsafe_allow_html=True
            )
        else:
            st.warning(
                "Geocoding returned no results — Nominatim may be temporarily rate-limiting. "
                "Results are cached for 24 hours once loaded. Try refreshing in 60 seconds."
            )
    else:
        st.error(
            "Could not reach WHO API. "
            "Visit [WHO Disease Outbreak News](https://www.who.int/emergencies/disease-outbreak-news) directly."
        )

# ── VACCINES & TREATMENTS ─────────────────────────────────────────────────────
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
            fallback_links='<a href="https://www.who.int/news-room/vaccines" target="_blank">WHO Vaccines</a> | '
                           '<a href="https://www.fda.gov/vaccines-blood-biologics" target="_blank">FDA</a>')
    with tab2:
        with st.spinner("Loading…"):
            items = fetch_multi(
                RSS_SOURCES["vaccines"],
                keywords=["antiviral","drug","treatment","therapy","approved","FDA","EMA","medication","pill"],
                max_per_source=8
            )
        render_grid(items, cols=2,
            fallback_links='<a href="https://www.fda.gov/drugs/drug-approvals-and-databases/drug-approvals" target="_blank">FDA Drug Approvals</a>')
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
            fallback_links='<a href="https://clinicaltrials.gov" target="_blank">ClinicalTrials.gov</a> | '
                           '<a href="https://ctri.nic.in" target="_blank">CTRI India</a>')

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">'
    'Outbreak data: <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO Disease Outbreak News</a>'
    ' &nbsp;·&nbsp; Geocoding: <a href="https://nominatim.openstreetmap.org" target="_blank">Nominatim / OpenStreetMap</a>'
    ' &nbsp;·&nbsp; News: WHO · Reuters · The Lancet · NEJM · STAT News · The Hindu · Times of India'
    ' &nbsp;·&nbsp; For internal clinical use only'
    '</div>',
    unsafe_allow_html=True
)