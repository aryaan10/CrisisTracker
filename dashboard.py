import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nanavati Hospital | Global Disease Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Force light theme regardless of system preference
st._config.set_option("theme.base", "light")
st._config.set_option("theme.backgroundColor", "#f4f5f7")
st._config.set_option("theme.secondaryBackgroundColor", "#0d1b2a")
st._config.set_option("theme.textColor", "#1a1a2e")
st._config.set_option("theme.primaryColor", "#1565c0")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* Force light theme regardless of system preference */
:root, html[data-theme="dark"], html[data-theme="light"] {
    color-scheme: light !important;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: #f4f5f7 !important;
    color: #1a1a2e !important;
}
/* Override Streamlit dark mode variables */
[data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #f4f5f7 !important;
    color: #1a1a2e !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar toggle button — shown only when sidebar is collapsed */
.sidebar-toggle-btn {
    position: fixed;
    top: 50%;
    left: 0;
    transform: translateY(-50%);
    z-index: 9999;
    background: #0d1b2a;
    color: #c8d6e5;
    border: none;
    border-radius: 0 8px 8px 0;
    padding: 14px 10px;
    cursor: pointer;
    font-size: 1.1rem;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.18);
    transition: background 0.15s;
    display: none;
}
.sidebar-toggle-btn:hover { background: #1565c0; }

/* Show the button only when sidebar is collapsed */
[data-testid="collapsedControl"] ~ * .sidebar-toggle-btn,
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stAppViewContainer"] .sidebar-toggle-btn {
    display: block;
}
/* Detect collapsed state via the collapse button presence */
section[data-testid="stSidebar"][style*="margin-left"] ~ div .sidebar-toggle-btn,
section[data-testid="stSidebar"].st-emotion-cache-hidden ~ div .sidebar-toggle-btn {
    display: block;
}
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1600px; }
.stRadio > label { display: none; }
div[data-testid="stDecoration"] { display: none; }

[data-testid="stSidebar"] { background: #0d1b2a !important; border-right: 1px solid #1e3a5f !important; }
[data-testid="stSidebar"] * { color: #c8d6e5 !important; }
[data-testid="stSidebar"] .stRadio > div > label {
    display: flex !important; padding: 10px 14px !important; border-radius: 6px !important;
    margin: 2px 0 !important; cursor: pointer; font-size: 0.88rem !important;
    font-weight: 500 !important; letter-spacing: 0.01em; transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio > div > label:hover { background: #1e3a5f !important; }
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] { background: #1565c0 !important; color: #fff !important; }

.sidebar-logo { font-size: 1.1rem; font-weight: 700; letter-spacing: 0.1em; color: #ffffff !important; padding: 8px 4px 4px 4px; line-height: 1.4; }
.sidebar-logo span { font-size: 0.7rem; font-weight: 400; letter-spacing: 0.04em; color: #7a9cc4 !important; display: block; }
.sidebar-label { font-size: 0.68rem !important; font-weight: 600 !important; letter-spacing: 0.14em !important; color: #4a6f8a !important; margin: 0 0 6px 4px !important; }
.sidebar-footer { font-size: 0.72rem !important; color: #4a6f8a !important; line-height: 1.6; }

.top-header { display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #e0e6ed; border-radius: 10px; padding: 18px 28px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.header-title { font-size: 1.4rem; font-weight: 700; color: #0d1b2a; letter-spacing: -0.01em; }
.header-sub { font-size: 0.82rem; color: #6b7c93; margin-top: 3px; }
.header-status { display: flex; align-items: center; gap: 8px; font-size: 0.82rem; font-weight: 600; color: #27ae60; background: #eafaf1; border: 1px solid #a9dfbf; border-radius: 20px; padding: 7px 16px; }
.pulse-dot { width: 8px; height: 8px; background: #27ae60; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.3)} }

.kpi-card { background: #ffffff; border: 1px solid #e0e6ed; border-radius: 10px; padding: 20px 24px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
.kpi-num { font-size: 2.4rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.kpi-label { font-size: 0.78rem; font-weight: 500; color: #6b7c93; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }

.section-title { font-size: 1.05rem; font-weight: 700; color: #0d1b2a; letter-spacing: -0.01em; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #1565c0; display: inline-block; }
.section-subtitle { font-size: 0.9rem; font-weight: 600; color: #1a3a5c; margin-bottom: 10px; }

.outbreak-row { display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #e0e6ed; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; transition: box-shadow 0.15s; }
.outbreak-row:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.07); }
.outbreak-disease { font-size: 0.9rem; font-weight: 600; color: #0d1b2a; }
.outbreak-loc { font-size: 0.78rem; color: #6b7c93; margin-top: 2px; }
.outbreak-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.outbreak-cases { font-size: 0.8rem; font-weight: 600; font-family: 'IBM Plex Mono', monospace; color: #34495e; }
.badge { font-size: 0.68rem; font-weight: 600; color: #fff; padding: 3px 9px; border-radius: 10px; letter-spacing: 0.04em; text-transform: uppercase; }
.status-tag { font-size: 0.72rem; font-weight: 600; }

.article-card { display: block; background: #ffffff; border: 1px solid #e0e6ed; border-radius: 10px; padding: 18px; margin-bottom: 14px; text-decoration: none !important; transition: transform 0.15s, box-shadow 0.15s; }
.article-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.09); border-color: #1565c0; }
.article-meta { font-size: 0.72rem; color: #1565c0; font-weight: 600; letter-spacing: 0.03em; margin-bottom: 7px; }
.article-title { font-size: 0.88rem; font-weight: 700; color: #0d1b2a; line-height: 1.45; margin-bottom: 8px; }
.article-desc { font-size: 0.8rem; color: #5a6a7e; line-height: 1.5; }
.article-link { font-size: 0.75rem; font-weight: 600; color: #1565c0; margin-top: 10px; }

.authority-link { display: block; text-align: center; background: #ffffff; border: 1px solid #c5d3e0; border-radius: 8px; padding: 12px; font-size: 0.82rem; font-weight: 600; color: #1565c0 !important; text-decoration: none !important; transition: background 0.15s; margin-bottom: 10px; }
.authority-link:hover { background: #e8f0fe; }

.source-badge { display: inline-block; font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-right: 6px; letter-spacing: 0.04em; text-transform: uppercase; }

.map-note { font-size: 0.8rem; color: #6b7c93; margin-bottom: 8px; }
.map-legend { display: flex; align-items: center; gap: 6px; font-size: 0.78rem; color: #34495e; font-weight: 600; margin-bottom: 12px; flex-wrap: wrap; }
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }

.data-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); font-size: 0.85rem; }
.data-table th { background: #0d1b2a; color: #c8d6e5; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; padding: 12px 16px; text-align: left; }
.data-table td { padding: 11px 16px; border-bottom: 1px solid #edf0f4; color: #2c3e50; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #f7f9fc; }

.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 2px solid #e0e6ed !important; background: transparent !important; }
.stTabs [data-baseweb="tab"] { font-size: 0.85rem !important; font-weight: 600 !important; color: #6b7c93 !important; padding: 10px 20px !important; border-radius: 0 !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: #1565c0 !important; border-bottom: 2px solid #1565c0 !important; }

.feed-error { background: #fff8e1; border: 1px solid #ffe082; border-radius: 8px; padding: 14px 18px; font-size: 0.83rem; color: #6d4c00; }
.feed-error a { color: #1565c0; font-weight: 600; }

.footer { text-align: center; font-size: 0.72rem; color: #a0aebe; margin-top: 40px; padding-top: 16px; border-top: 1px solid #e0e6ed; }
[data-testid="stMultiSelect"] span[data-baseweb="tag"] { background-color: #1565c0 !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Toggle Button (shown when sidebar is collapsed) ───────────────────
st.markdown("""
<script>
(function() {
    function addToggleBtn() {
        if (document.getElementById('sidebar-toggle-fab')) return;
        var btn = document.createElement('button');
        btn.id = 'sidebar-toggle-fab';
        btn.innerHTML = '&#9776;';
        btn.title = 'Show sidebar';
        btn.style.cssText = [
            'position:fixed', 'top:50%', 'left:0',
            'transform:translateY(-50%)', 'z-index:9999',
            'background:#0d1b2a', 'color:#c8d6e5',
            'border:none', 'border-radius:0 8px 8px 0',
            'padding:14px 10px', 'cursor:pointer',
            'font-size:1.2rem', 'box-shadow:2px 2px 8px rgba(0,0,0,0.25)',
            'transition:background 0.15s', 'display:none'
        ].join(';');
        btn.onmouseenter = function(){ btn.style.background = '#1565c0'; };
        btn.onmouseleave = function(){ btn.style.background = '#0d1b2a'; };
        btn.onclick = function() {
            var collapseBtn = document.querySelector('[data-testid="collapsedControl"]');
            if (collapseBtn) { collapseBtn.click(); }
        };
        document.body.appendChild(btn);

        function updateBtn() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            var expanded = sidebar.getAttribute('aria-expanded');
            var style = window.getComputedStyle(sidebar);
            var ml = parseInt(style.marginLeft || '0');
            var isHidden = (expanded === 'false') || ml < -50;
            btn.style.display = isHidden ? 'block' : 'none';
        }

        var observer = new MutationObserver(updateBtn);
        function observeSidebar() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                observer.observe(sidebar, { attributes: true, attributeFilter: ['aria-expanded', 'style'] });
                updateBtn();
            } else {
                setTimeout(observeSidebar, 300);
            }
        }
        observeSidebar();
        setInterval(updateBtn, 800);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addToggleBtn);
    } else {
        setTimeout(addToggleBtn, 500);
    }
})();
</script>
""", unsafe_allow_html=True)

# ── Outbreak Data ─────────────────────────────────────────────────────────────
# Update this list regularly with verified data from WHO / NCDC / ECDC
SEVERITY_COLOR = {"Critical": "#c0392b", "High": "#e67e22", "Moderate": "#e2b800", "Low": "#27ae60"}

OUTBREAK_DATA = [
    {"location": "Mumbai, India",      "lat": 19.076, "lon": 72.877,  "disease": "Leptospirosis",            "cases": 340,   "status": "Active",     "severity": "Moderate"},
    {"location": "Kerala, India",      "lat": 10.850, "lon": 76.271,  "disease": "Nipah (Historical Alert)", "cases": 6,     "status": "Contained",  "severity": "High"},
    {"location": "Delhi, India",       "lat": 28.613, "lon": 77.209,  "disease": "Dengue Surge",             "cases": 2100,  "status": "Active",     "severity": "Moderate"},
    {"location": "West Bengal, India", "lat": 22.572, "lon": 88.363,  "disease": "Cholera",                  "cases": 180,   "status": "Active",     "severity": "Moderate"},
    {"location": "Rajasthan, India",   "lat": 27.023, "lon": 74.217,  "disease": "Anthrax (Animal-linked)",  "cases": 14,    "status": "Contained",  "severity": "High"},
    {"location": "Southeast Asia",     "lat": 13.736, "lon": 100.523, "disease": "H5N1 Avian Influenza",    "cases": 12,    "status": "Monitoring", "severity": "High"},
    {"location": "Central Africa",     "lat": -1.291, "lon": 28.859,  "disease": "Mpox Clade Ib",           "cases": 8900,  "status": "Active",     "severity": "Critical"},
    {"location": "South America",      "lat": -3.119, "lon": -60.021, "disease": "Oropouche Fever",         "cases": 7600,  "status": "Active",     "severity": "Moderate"},
    {"location": "Pakistan",           "lat": 30.375, "lon": 69.345,  "disease": "Polio (cVDPV)",           "cases": 27,    "status": "Active",     "severity": "Moderate"},
    {"location": "East Africa",        "lat": 1.285,  "lon": 36.820,  "disease": "Rift Valley Fever",       "cases": 410,   "status": "Monitoring", "severity": "High"},
    {"location": "United States",      "lat": 37.090, "lon": -95.712, "disease": "H5N1 Dairy Workers",      "cases": 67,    "status": "Monitoring", "severity": "Moderate"},
    {"location": "China",              "lat": 35.861, "lon": 104.195, "disease": "HMPV Surge",              "cases": 15000, "status": "Monitoring", "severity": "Low"},
]

# ── RSS Feed Sources (all free, no API key needed) ────────────────────────────
# Each entry: (label, color, rss_url)
RSS_SOURCES = {
    "who": [
        ("WHO",     "#1565c0", "https://www.who.int/rss-feeds/news-english.xml"),
    ],
    "global": [
        ("WHO",     "#1565c0", "https://www.who.int/rss-feeds/news-english.xml"),
        ("Reuters", "#c0392b", "https://feeds.reuters.com/reuters/healthNews"),
        ("CDC",     "#27ae60", "https://tools.cdc.gov/api/v2/resources/media/132608.rss"),
    ],
    "india": [
        ("The Hindu",    "#b71c1c", "https://www.thehindu.com/sci-tech/health/feeder/default.rss"),
        ("Times of India", "#e65100", "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms"),
        ("NDTV Health",  "#1a237e", "https://feeds.feedburner.com/ndtvnews-health"),
    ],
    "expert": [
        ("WHO",        "#1565c0", "https://www.who.int/rss-feeds/news-english.xml"),
        ("The Lancet", "#6a1b9a", "https://www.thelancet.com/rssfeed/lancet_online.xml"),
        ("NEJM",       "#004d40", "https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm"),
    ],
    "vaccines": [
        ("WHO",     "#1565c0", "https://www.who.int/rss-feeds/news-english.xml"),
        ("Reuters", "#c0392b", "https://feeds.reuters.com/reuters/healthNews"),
        ("STAT",    "#f57f17", "https://www.statnews.com/feed/"),
    ],
}

DISEASE_KEYWORDS = [
    "disease", "virus", "outbreak", "epidemic", "pandemic", "infection",
    "pathogen", "vaccine", "flu", "dengue", "cholera", "mpox", "H5N1",
    "WHO", "CDC", "ICMR", "health alert", "antimicrobial", "resistant",
    "fever", "zoonotic", "emerging", "surveillance", "quarantine", "clinical trial",
    "antiviral", "mortality", "morbidity", "contagious", "immunization",
]

INDIA_KEYWORDS = ["india", "indian", "icmr", "mohfw", "delhi", "mumbai", "kerala",
                  "bengal", "rajasthan", "chennai", "hyderabad", "pune", "kolkata"]

VACCINE_KEYWORDS = ["vaccine", "vaccination", "immunization", "antiviral", "drug",
                    "treatment", "therapy", "clinical trial", "approved", "phase 3",
                    "efficacy", "booster", "mRNA"]

EXPERT_KEYWORDS = ["expert", "scientist", "researcher", "epidemiologist", "virologist",
                   "government", "ministry", "advisory", "warning", "alert", "WHO",
                   "CDC", "lancet", "nejm", "study", "research", "policy"]

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()

def parse_date(raw: str) -> str:
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%d %b %Y")
        except Exception:
            pass
    return raw[:10] if raw else ""

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rss(url: str) -> list:
    """Fetch and parse a single RSS feed. Returns list of article dicts."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NanavatiDashboard/1.0)"}
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        # Support both RSS <item> and Atom <entry>
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for item in list(root.iter("item")) + list(root.iter("{http://www.w3.org/2005/Atom}entry")):
            title = strip_html(item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "")
            link  = (item.findtext("link") or item.findtext("{http://www.w3.org/2005/Atom}link") or "").strip()
            # Atom links are attributes
            if not link:
                link_el = item.find("{http://www.w3.org/2005/Atom}link")
                link = (link_el.get("href", "") if link_el is not None else "")
            desc  = strip_html(
                item.findtext("description") or
                item.findtext("{http://www.w3.org/2005/Atom}summary") or
                item.findtext("{http://www.w3.org/2005/Atom}content") or ""
            )[:200]
            pub   = parse_date(
                item.findtext("pubDate") or
                item.findtext("{http://www.w3.org/2005/Atom}published") or
                item.findtext("{http://www.w3.org/2005/Atom}updated") or ""
            )
            if title and link:
                items.append({"title": title, "url": link, "description": desc, "date": pub})
        return items
    except Exception:
        return []

def fetch_multi(sources: list, keywords: list = None, max_per_source: int = 6) -> list:
    """Fetch from multiple RSS sources, optionally filter by keywords, deduplicate."""
    results = []
    seen = set()
    for label, color, url in sources:
        items = fetch_rss(url)
        count = 0
        for item in items:
            if count >= max_per_source:
                break
            text = (item["title"] + " " + item["description"]).lower()
            if keywords and not any(k.lower() in text for k in keywords):
                continue
            key = item["title"][:60]
            if key in seen:
                continue
            seen.add(key)
            item["source_label"] = label
            item["source_color"] = color
            results.append(item)
            count += 1
    return results

def article_card(a: dict) -> str:
    title  = a.get("title", "Untitled")[:115]
    url    = a.get("url", "#")
    label  = a.get("source_label", "Source")
    color  = a.get("source_color", "#1565c0")
    desc   = a.get("description", "")[:170]
    date   = a.get("date", "")
    return f"""<a class="article-card" href="{url}" target="_blank" rel="noopener noreferrer">
      <div class="article-meta">
        <span class="source-badge" style="background:{color};color:#fff">{label}</span>{date}
      </div>
      <div class="article-title">{title}</div>
      <div class="article-desc">{desc}</div>
      <div class="article-link">Read full article &rarr;</div>
    </a>"""

def render_grid(articles: list, cols: int = 2, fallback_links: str = ""):
    if not articles:
        st.markdown(f'<div class="feed-error">Could not load feed at this moment. Try refreshing, or visit these sources directly:<br>{fallback_links}</div>', unsafe_allow_html=True)
        return
    columns = st.columns(cols)
    for i, a in enumerate(articles):
        with columns[i % cols]:
            st.markdown(article_card(a), unsafe_allow_html=True)

def severity_badge(level):
    c = SEVERITY_COLOR.get(level, "#888")
    return f'<span class="badge" style="background:{c}">{level}</span>'

def build_map():
    m = folium.Map(location=[20, 30], zoom_start=2, tiles="CartoDB positron", prefer_canvas=True)
    for o in OUTBREAK_DATA:
        color  = SEVERITY_COLOR.get(o["severity"], "#888")
        radius = {"Critical": 22, "High": 17, "Moderate": 13, "Low": 9}.get(o["severity"], 10)
        popup  = f"""<div style="font-family:'IBM Plex Sans',sans-serif;min-width:200px">
          <b style="font-size:14px">{o['disease']}</b><br>
          <span style="color:#555">{o['location']}</span>
          <hr style="margin:6px 0">
          <b>Cases:</b> {o['cases']:,}<br>
          <b>Status:</b> <span style="color:{color};font-weight:600">{o['status']}</span><br>
          <b>Severity:</b> {o['severity']}
        </div>"""
        folium.CircleMarker(
            location=[o["lat"], o["lon"]], radius=radius, color=color,
            fill=True, fill_color=color, fill_opacity=0.55,
            popup=folium.Popup(popup, max_width=250),
            tooltip=f"{o['disease']} — {o['location']}",
        ).add_to(m)
    return m

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">NANAVATI<span>Super Speciality Hospital</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p class="sidebar-label">NAVIGATION</p>', unsafe_allow_html=True)
    page = st.radio("", [
        "Overview", "Global News", "India Focus",
        "Expert Advisories", "Outbreak Map", "Vaccines & Treatments"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<p class="sidebar-label">SEVERITY FILTER</p>', unsafe_allow_html=True)
    severity_filter = st.multiselect(
        "", ["Critical", "High", "Moderate", "Low"],
        default=["Critical", "High", "Moderate", "Low"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(f'<p class="sidebar-footer">Feeds refresh every hour<br>Last update: {datetime.utcnow().strftime("%d %b %Y, %H:%M")} UTC</p>', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-header">
  <div>
    <div class="header-title">Global Disease Intelligence Dashboard</div>
    <div class="header-sub">Pandemic and Epidemic Preparedness &nbsp;·&nbsp; {datetime.utcnow().strftime("%A, %d %B %Y")}</div>
  </div>
  <div class="header-status"><div class="pulse-dot"></div>Live Monitoring</div>
</div>""", unsafe_allow_html=True)

# ── KPI Strip ─────────────────────────────────────────────────────────────────
active    = [o for o in OUTBREAK_DATA if o["status"] == "Active"     and o["severity"] in severity_filter]
critical  = [o for o in OUTBREAK_DATA if o["severity"] == "Critical" and o["severity"] in severity_filter]
monitored = [o for o in OUTBREAK_DATA if o["status"] == "Monitoring" and o["severity"] in severity_filter]
contained = [o for o in OUTBREAK_DATA if o["status"] == "Contained"]

for col, num, label, color in zip(
    st.columns(4),
    [len(active), len(critical), len(monitored), len(contained)],
    ["Active Outbreaks", "Critical Alerts", "Under Monitoring", "Contained"],
    ["#c0392b", "#e67e22", "#2980b9", "#27ae60"],
):
    with col:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:{color}">{num}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═════════════════════════════ PAGES ═════════════════════════════════════════

# ── OVERVIEW ─────────────────────────────────────────────────────────────────
if page == "Overview":
    col_left, col_right = st.columns([1.4, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-title">Active Outbreak Monitor</div>', unsafe_allow_html=True)
        filtered = sorted(
            [o for o in OUTBREAK_DATA if o["severity"] in severity_filter],
            key=lambda x: ["Critical", "High", "Moderate", "Low"].index(x["severity"])
        )
        for o in filtered:
            color = SEVERITY_COLOR[o["severity"]]
            st.markdown(f"""
            <div class="outbreak-row">
              <div>
                <div class="outbreak-disease">{o['disease']}</div>
                <div class="outbreak-loc">{o['location']}</div>
              </div>
              <div class="outbreak-right">
                <div class="outbreak-cases">{o['cases']:,} cases</div>
                {severity_badge(o['severity'])}
                <span class="status-tag" style="color:{color}">{o['status']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">WHO Latest Alerts</div>', unsafe_allow_html=True)
        with st.spinner("Loading WHO feed..."):
            who_items = fetch_rss("https://www.who.int/rss-feeds/news-english.xml")
        if who_items:
            for a in who_items[:7]:
                st.markdown(f"""<a class="article-card" href="{a['url']}" target="_blank">
                  <div class="article-meta"><span class="source-badge" style="background:#1565c0;color:#fff">WHO</span>{a['date']}</div>
                  <div class="article-title">{a['title'][:105]}</div>
                  <div class="article-link">Read full article &rarr;</div>
                </a>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="feed-error">WHO feed unavailable. Visit <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">who.int</a> directly.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Global Outbreak Map</div>', unsafe_allow_html=True)
    st_folium(build_map(), height=360, use_container_width=True)

# ── GLOBAL NEWS ──────────────────────────────────────────────────────────────
elif page == "Global News":
    st.markdown('<div class="section-title">Global Disease and Epidemic News</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["All Sources", "WHO Bulletins", "Reuters Health"])

    with tab1:
        with st.spinner("Loading feeds..."):
            articles = fetch_multi(RSS_SOURCES["global"], keywords=DISEASE_KEYWORDS, max_per_source=8)
        render_grid(articles, cols=3, fallback_links='<a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO</a> | <a href="https://www.reuters.com/business/healthcare-pharmaceuticals/" target="_blank">Reuters Health</a>')

    with tab2:
        with st.spinner("Loading WHO feed..."):
            who_articles = fetch_multi(RSS_SOURCES["who"], keywords=DISEASE_KEYWORDS, max_per_source=12)
        render_grid(who_articles, cols=3, fallback_links='<a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO Disease Outbreak News</a>')

    with tab3:
        with st.spinner("Loading Reuters feed..."):
            reuters = fetch_multi([("Reuters", "#c0392b", "https://feeds.reuters.com/reuters/healthNews")], keywords=DISEASE_KEYWORDS, max_per_source=12)
        render_grid(reuters, cols=3, fallback_links='<a href="https://www.reuters.com/business/healthcare-pharmaceuticals/" target="_blank">Reuters Health</a>')

# ── INDIA FOCUS ───────────────────────────────────────────────────────────────
elif page == "India Focus":
    st.markdown('<div class="section-title">India Disease Intelligence</div>', unsafe_allow_html=True)
    india_keys = ["India", "Mumbai", "Delhi", "Kerala", "Bengal", "Rajasthan", "Chennai", "Kolkata", "Hyderabad", "Pune"]
    india_outbreaks = sorted(
        [o for o in OUTBREAK_DATA if any(s in o["location"] for s in india_keys) and o["severity"] in severity_filter],
        key=lambda x: ["Critical", "High", "Moderate", "Low"].index(x["severity"])
    )

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown('<div class="section-subtitle">Active India Alerts</div>', unsafe_allow_html=True)
        for o in india_outbreaks:
            color = SEVERITY_COLOR[o["severity"]]
            st.markdown(f"""
            <div class="outbreak-row">
              <div>
                <div class="outbreak-disease">{o['disease']}</div>
                <div class="outbreak-loc">{o['location']}</div>
              </div>
              <div class="outbreak-right">
                <div class="outbreak-cases">{o['cases']:,} cases</div>
                {severity_badge(o['severity'])}
              </div>
            </div>""", unsafe_allow_html=True)

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
        with st.spinner("Loading India feeds..."):
            india_articles = fetch_multi(RSS_SOURCES["india"], keywords=DISEASE_KEYWORDS + INDIA_KEYWORDS, max_per_source=5)
        render_grid(
            india_articles, cols=1,
            fallback_links='<a href="https://www.thehindu.com/sci-tech/health/" target="_blank">The Hindu Health</a> | <a href="https://timesofindia.indiatimes.com/life-style/health-fitness" target="_blank">TOI Health</a>'
        )

# ── EXPERT ADVISORIES ─────────────────────────────────────────────────────────
elif page == "Expert Advisories":
    st.markdown('<div class="section-title">Expert and Government Advisories</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["WHO / CDC", "Medical Journals", "Government Measures"])

    with tab1:
        with st.spinner("Loading advisories..."):
            items = fetch_multi(RSS_SOURCES["who"], keywords=DISEASE_KEYWORDS, max_per_source=10)
        render_grid(items, cols=2, fallback_links='<a href="https://www.who.int/news" target="_blank">WHO News</a> | <a href="https://www.cdc.gov/media/dpk/diseases-and-conditions/index.html" target="_blank">CDC</a>')

    with tab2:
        with st.spinner("Loading journal feeds..."):
            journal_sources = [
                ("The Lancet", "#6a1b9a", "https://www.thelancet.com/rssfeed/lancet_online.xml"),
                ("NEJM",       "#004d40", "https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm"),
                ("STAT News",  "#f57f17", "https://www.statnews.com/feed/"),
            ]
            items = fetch_multi(journal_sources, keywords=DISEASE_KEYWORDS + EXPERT_KEYWORDS, max_per_source=6)
        render_grid(
            items, cols=2,
            fallback_links='<a href="https://www.thelancet.com" target="_blank">The Lancet</a> | <a href="https://www.nejm.org" target="_blank">NEJM</a> | <a href="https://www.statnews.com" target="_blank">STAT News</a>'
        )

    with tab3:
        with st.spinner("Loading government feeds..."):
            gov_sources = [
                ("WHO",     "#1565c0", "https://www.who.int/rss-feeds/news-english.xml"),
                ("Reuters", "#c0392b", "https://feeds.reuters.com/reuters/healthNews"),
            ]
            items = fetch_multi(gov_sources, keywords=EXPERT_KEYWORDS + ["government", "ministry", "policy", "regulation", "ban", "mandate"], max_per_source=8)
        render_grid(items, cols=2, fallback_links='<a href="https://www.who.int/news" target="_blank">WHO</a> | <a href="https://ecdc.europa.eu/en/threats-and-outbreaks" target="_blank">ECDC</a>')

# ── OUTBREAK MAP ──────────────────────────────────────────────────────────────
elif page == "Outbreak Map":
    st.markdown('<div class="section-title">Global Outbreak Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<p class="map-note">Circle size and color indicate severity. Click any marker for details.</p>', unsafe_allow_html=True)
    legend = " &nbsp; ".join([f'<span class="legend-dot" style="background:{c}"></span>{s}' for s, c in SEVERITY_COLOR.items()])
    st.markdown(f'<div class="map-legend">{legend}</div>', unsafe_allow_html=True)
    st_folium(build_map(), height=520, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Outbreak Reference Table</div>', unsafe_allow_html=True)
    filtered = sorted(
        [o for o in OUTBREAK_DATA if o["severity"] in severity_filter],
        key=lambda x: ["Critical", "High", "Moderate", "Low"].index(x["severity"])
    )
    rows = "".join([f"""<tr>
      <td>{o['disease']}</td><td>{o['location']}</td><td>{o['cases']:,}</td>
      <td><span class="badge" style="background:{SEVERITY_COLOR[o['severity']]}">{o['severity']}</span></td>
      <td>{o['status']}</td>
    </tr>""" for o in filtered])
    st.markdown(f"""<table class="data-table">
      <thead><tr><th>Disease</th><th>Location</th><th>Cases</th><th>Severity</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)

# ── VACCINES & TREATMENTS ─────────────────────────────────────────────────────
elif page == "Vaccines & Treatments":
    st.markdown('<div class="section-title">Vaccines and New Treatments</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["New Vaccines", "Antiviral Drugs", "Clinical Trials"])

    vax_sources = [
        ("WHO",       "#1565c0", "https://www.who.int/rss-feeds/news-english.xml"),
        ("Reuters",   "#c0392b", "https://feeds.reuters.com/reuters/healthNews"),
        ("STAT News", "#f57f17", "https://www.statnews.com/feed/"),
    ]

    with tab1:
        with st.spinner("Loading vaccine news..."):
            items = fetch_multi(vax_sources, keywords=["vaccine", "vaccination", "immunization", "approved", "rollout", "efficacy", "booster", "mRNA"], max_per_source=6)
        render_grid(items, cols=2, fallback_links='<a href="https://www.who.int/news-room/vaccines" target="_blank">WHO Vaccines</a> | <a href="https://www.fda.gov/vaccines-blood-biologics" target="_blank">FDA</a>')

    with tab2:
        with st.spinner("Loading drug news..."):
            items = fetch_multi(vax_sources, keywords=["antiviral", "drug", "treatment", "therapy", "approved", "FDA", "EMA", "medication", "pill"], max_per_source=6)
        render_grid(items, cols=2, fallback_links='<a href="https://www.fda.gov/drugs/drug-approvals-and-databases/drug-approvals" target="_blank">FDA Drug Approvals</a>')

    with tab3:
        with st.spinner("Loading trial news..."):
            trial_sources = [
                ("STAT News", "#f57f17", "https://www.statnews.com/feed/"),
                ("The Lancet","#6a1b9a", "https://www.thelancet.com/rssfeed/lancet_online.xml"),
                ("NEJM",      "#004d40", "https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm"),
            ]
            items = fetch_multi(trial_sources, keywords=["clinical trial", "phase 2", "phase 3", "trial results", "randomized", "placebo", "study"], max_per_source=6)
        render_grid(
            items, cols=2,
            fallback_links='<a href="https://clinicaltrials.gov" target="_blank">ClinicalTrials.gov</a> | <a href="https://ctri.nic.in" target="_blank">CTRI India</a>'
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Nanavati Super Speciality Hospital &nbsp;·&nbsp; Global Disease Intelligence Platform &nbsp;·&nbsp;
  Sources: WHO, Reuters, The Lancet, NEJM, STAT News, The Hindu, Times of India &nbsp;·&nbsp; For internal clinical use only
</div>""", unsafe_allow_html=True)