import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nanavati Hospital | Global Disease Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── All CSS Inline ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: #f4f5f7 !important;
    color: #1a1a2e !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1600px; }
.stRadio > label { display: none; }
div[data-testid="stDecoration"] { display: none; }

[data-testid="stSidebar"] { background: #0d1b2a !important; border-right: 1px solid #1e3a5f !important; }
[data-testid="stSidebar"] * { color: #c8d6e5 !important; }
[data-testid="stSidebar"] .stRadio > div > label {
    display: flex !important; padding: 10px 14px !important;
    border-radius: 6px !important; margin: 2px 0 !important;
    cursor: pointer; font-size: 0.88rem !important; font-weight: 500 !important;
    letter-spacing: 0.01em; transition: background 0.15s;
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
.status-tag { font-size: 0.72rem; font-weight: 600; }
.badge { font-size: 0.68rem; font-weight: 600; color: #fff; padding: 3px 9px; border-radius: 10px; letter-spacing: 0.04em; text-transform: uppercase; }

.who-item { display: block; padding: 11px 14px; border: 1px solid #e0e6ed; border-left: 3px solid #1565c0; background: #ffffff; border-radius: 0 8px 8px 0; margin-bottom: 8px; text-decoration: none !important; transition: border-color 0.15s, box-shadow 0.15s; }
.who-item:hover { border-left-color: #c0392b; box-shadow: 0 3px 10px rgba(0,0,0,0.06); }
.who-title { font-size: 0.85rem; font-weight: 600; color: #0d1b2a; line-height: 1.4; }
.who-meta { font-size: 0.73rem; color: #8a9bb0; margin-top: 4px; }

.article-card { display: block; background: #ffffff; border: 1px solid #e0e6ed; border-radius: 10px; padding: 18px; margin-bottom: 14px; text-decoration: none !important; transition: transform 0.15s, box-shadow 0.15s; min-height: 148px; }
.article-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.09); border-color: #1565c0; }
.article-meta { font-size: 0.72rem; color: #1565c0; font-weight: 600; letter-spacing: 0.03em; margin-bottom: 7px; }
.article-title { font-size: 0.88rem; font-weight: 700; color: #0d1b2a; line-height: 1.45; margin-bottom: 8px; }
.article-desc { font-size: 0.8rem; color: #5a6a7e; line-height: 1.5; }
.article-link { font-size: 0.75rem; font-weight: 600; color: #1565c0; margin-top: 10px; }

.authority-link { display: block; text-align: center; background: #ffffff; border: 1px solid #c5d3e0; border-radius: 8px; padding: 12px; font-size: 0.82rem; font-weight: 600; color: #1565c0 !important; text-decoration: none !important; transition: background 0.15s, box-shadow 0.15s; margin-bottom: 10px; }
.authority-link:hover { background: #e8f0fe; box-shadow: 0 3px 10px rgba(21,101,192,0.12); }

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

.no-data { background: #fff8e1; border: 1px solid #ffe082; border-radius: 8px; padding: 16px 20px; font-size: 0.85rem; color: #6d4c00; line-height: 1.7; }
.no-data a { color: #1565c0; font-weight: 600; }

.footer { text-align: center; font-size: 0.72rem; color: #a0aebe; margin-top: 40px; padding-top: 16px; border-top: 1px solid #e0e6ed; letter-spacing: 0.02em; }

[data-testid="stMultiSelect"] span[data-baseweb="tag"] { background-color: #1565c0 !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "")

SEVERITY_COLOR = {
    "Critical": "#c0392b",
    "High":     "#e67e22",
    "Moderate": "#f1c40f",
    "Low":      "#27ae60",
}

# Update this list regularly with verified outbreak data
OUTBREAK_DATA = [
    {"location": "Mumbai, India",      "lat": 19.076, "lon": 72.877,  "disease": "Leptospirosis",           "cases": 340,   "status": "Active",     "severity": "Moderate"},
    {"location": "Kerala, India",      "lat": 10.850, "lon": 76.271,  "disease": "Nipah (Historical Alert)", "cases": 6,     "status": "Contained",  "severity": "High"},
    {"location": "Delhi, India",       "lat": 28.613, "lon": 77.209,  "disease": "Dengue Surge",            "cases": 2100,  "status": "Active",     "severity": "Moderate"},
    {"location": "West Bengal, India", "lat": 22.572, "lon": 88.363,  "disease": "Cholera",                 "cases": 180,   "status": "Active",     "severity": "Moderate"},
    {"location": "Rajasthan, India",   "lat": 27.023, "lon": 74.217,  "disease": "Anthrax (Animal-linked)", "cases": 14,    "status": "Contained",  "severity": "High"},
    {"location": "Southeast Asia",     "lat": 13.736, "lon": 100.523, "disease": "H5N1 Avian Influenza",   "cases": 12,    "status": "Monitoring", "severity": "High"},
    {"location": "Central Africa",     "lat": -1.291, "lon": 28.859,  "disease": "Mpox Clade Ib",          "cases": 8900,  "status": "Active",     "severity": "Critical"},
    {"location": "South America",      "lat": -3.119, "lon": -60.021, "disease": "Oropouche Fever",        "cases": 7600,  "status": "Active",     "severity": "Moderate"},
    {"location": "Pakistan",           "lat": 30.375, "lon": 69.345,  "disease": "Polio (cVDPV)",          "cases": 27,    "status": "Active",     "severity": "Moderate"},
    {"location": "East Africa",        "lat": 1.285,  "lon": 36.820,  "disease": "Rift Valley Fever",      "cases": 410,   "status": "Monitoring", "severity": "High"},
    {"location": "United States",      "lat": 37.090, "lon": -95.712, "disease": "H5N1 Dairy Workers",     "cases": 67,    "status": "Monitoring", "severity": "Moderate"},
    {"location": "China",              "lat": 35.861, "lon": 104.195, "disease": "HMPV Surge",             "cases": 15000, "status": "Monitoring", "severity": "Low"},
]

# ── Data Fetchers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_news(query: str, page_size: int = 9) -> list:
    if not NEWS_API_KEY:
        return []
    try:
        r = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query, "language": "en", "sortBy": "publishedAt",
                "pageSize": page_size, "apiKey": NEWS_API_KEY,
                "from": (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d"),
            },
            timeout=8,
        )
        return r.json().get("articles", [])
    except Exception:
        return []

@st.cache_data(ttl=7200)
def fetch_who_rss() -> list:
    try:
        r = requests.get("https://www.who.int/rss-feeds/news-english.xml", timeout=10)
        root = ET.fromstring(r.content)
        items = []
        for item in root.iter("item"):
            items.append({
                "title": item.findtext("title", ""),
                "url":   item.findtext("link", ""),
                "publishedAt": item.findtext("pubDate", "")[:16],
                "source": {"name": "WHO"},
            })
            if len(items) >= 8:
                break
        return items
    except Exception:
        return []

# ── UI Helpers ────────────────────────────────────────────────────────────────
def severity_badge(level: str) -> str:
    c = SEVERITY_COLOR.get(level, "#888")
    return f'<span class="badge" style="background:{c}">{level}</span>'

def build_map() -> folium.Map:
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

def article_card(a: dict) -> str:
    title  = (a.get("title") or "Untitled")[:110]
    url    = a.get("url", "#")
    source = (a.get("source") or {}).get("name", "Unknown")
    desc   = (a.get("description") or "")[:160]
    pub    = a.get("publishedAt", "")
    try:
        pub = datetime.fromisoformat(pub.replace("Z", "+00:00")).strftime("%d %b %Y")
    except Exception:
        pub = pub[:10]
    return f"""<a class="article-card" href="{url}" target="_blank" rel="noopener noreferrer">
      <div class="article-meta">{source} &nbsp;·&nbsp; {pub}</div>
      <div class="article-title">{title}</div>
      <div class="article-desc">{desc}</div>
      <div class="article-link">Read full article &rarr;</div>
    </a>"""

def no_key_box(extra: str = "") -> str:
    return f"""<div class="no-data">
      Add your free NewsAPI key in Streamlit Secrets to load live articles.
      Get one at <a href="https://newsapi.org/register" target="_blank">newsapi.org/register</a> (100 requests/day free).
      {extra}
    </div>"""

def render_articles(query: str, cols: int = 2, n: int = 8, extra: str = ""):
    articles = fetch_news(query, n)
    if articles:
        columns = st.columns(cols)
        for i, a in enumerate(articles):
            with columns[i % cols]:
                st.markdown(article_card(a), unsafe_allow_html=True)
    else:
        st.markdown(no_key_box(extra), unsafe_allow_html=True)

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
    st.markdown(f'<p class="sidebar-footer">Data refreshed hourly<br>Last update: {datetime.utcnow().strftime("%d %b %Y, %H:%M")} UTC</p>', unsafe_allow_html=True)

# ── Top Header ────────────────────────────────────────────────────────────────
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
        who = fetch_who_rss()
        if who:
            for a in who[:6]:
                st.markdown(f"""
                <a class="who-item" href="{a['url']}" target="_blank">
                  <div class="who-title">{a['title'][:105]}</div>
                  <div class="who-meta">WHO &nbsp;·&nbsp; {a['publishedAt']}</div>
                </a>""", unsafe_allow_html=True)
        else:
            st.markdown(no_key_box('Or visit <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO Outbreak News</a> directly.'), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Global Outbreak Map</div>', unsafe_allow_html=True)
    st_folium(build_map(), height=360, use_container_width=True)

# ── GLOBAL NEWS ──────────────────────────────────────────────────────────────
elif page == "Global News":
    st.markdown('<div class="section-title">Global Disease and Epidemic News</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Emerging Diseases", "Active Outbreaks", "Pandemic Preparedness"])
    with tab1:
        render_articles("emerging disease outbreak epidemic 2025", cols=3)
    with tab2:
        render_articles("mpox H5N1 avian flu cholera outbreak WHO 2025", cols=3)
    with tab3:
        render_articles("pandemic preparedness vaccine stockpile WHO 2025", cols=3)

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
            ("MoHFW India", "https://www.mohfw.gov.in"),
            ("ICMR",        "https://www.icmr.gov.in"),
            ("NCDC India",  "https://ncdc.mohfw.gov.in"),
            ("IDSP",        "https://idsp.mohfw.gov.in"),
        ]:
            st.markdown(f'<a class="authority-link" href="{url}" target="_blank">{name} &rarr;</a>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-subtitle">India News Feed</div>', unsafe_allow_html=True)
        render_articles("India disease outbreak ICMR epidemic 2025", cols=1, n=6)

# ── EXPERT ADVISORIES ─────────────────────────────────────────────────────────
elif page == "Expert Advisories":
    st.markdown('<div class="section-title">Expert and Government Advisories</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Epidemiologists", "Government Measures", "WHO / CDC"])
    with tab1:
        render_articles("epidemiologist warns disease risk outbreak 2025", cols=2)
    with tab2:
        render_articles("government health measures quarantine disease control 2025", cols=2)
    with tab3:
        who = fetch_who_rss()
        if who:
            cols = st.columns(2)
            for i, a in enumerate(who):
                with cols[i % 2]:
                    st.markdown(article_card(a), unsafe_allow_html=True)
        else:
            st.markdown("""<div class="no-data">
              Official sources:
              <a href="https://www.who.int/emergencies/disease-outbreak-news" target="_blank">WHO Outbreak News</a> &nbsp;|&nbsp;
              <a href="https://www.cdc.gov/outbreaks/index.html" target="_blank">CDC Outbreaks</a> &nbsp;|&nbsp;
              <a href="https://ecdc.europa.eu/en/threats-and-outbreaks" target="_blank">ECDC Threats</a>
            </div>""", unsafe_allow_html=True)

# ── OUTBREAK MAP ──────────────────────────────────────────────────────────────
elif page == "Outbreak Map":
    st.markdown('<div class="section-title">Global Outbreak Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<p class="map-note">Circle size and color indicate severity. Click any marker for detailed information.</p>', unsafe_allow_html=True)
    legend = " &nbsp; ".join([f'<span class="legend-dot" style="background:{c}"></span>{s}' for s, c in SEVERITY_COLOR.items()])
    st.markdown(f'<div class="map-legend">{legend}</div>', unsafe_allow_html=True)
    st_folium(build_map(), height=500, use_container_width=True)

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
    with tab1:
        render_articles(
            "new vaccine approved WHO FDA infectious disease 2025", cols=2,
            extra='Official source: <a href="https://www.who.int/news-room/vaccines" target="_blank">WHO Vaccines</a>',
        )
    with tab2:
        render_articles(
            "antiviral drug approval treatment infectious disease 2025", cols=2,
            extra='Track approvals: <a href="https://www.fda.gov/vaccines-blood-biologics" target="_blank">FDA</a>',
        )
    with tab3:
        render_articles(
            "clinical trial phase 3 vaccine infectious disease 2025", cols=2,
            extra='Track trials: <a href="https://clinicaltrials.gov" target="_blank">ClinicalTrials.gov</a> | <a href="https://ctri.nic.in" target="_blank">CTRI India</a>',
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Nanavati Super Speciality Hospital &nbsp;·&nbsp; Global Disease Intelligence Platform &nbsp;·&nbsp;
  Sources: WHO, NewsAPI, public health agencies &nbsp;·&nbsp; For internal clinical use only
</div>""", unsafe_allow_html=True)
