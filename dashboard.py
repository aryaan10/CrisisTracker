"""
Nanavati Hospital — Global Disease Surveillance Dashboard
Fully free, no API keys required.
Sources: WHO RSS, CDC RSS, disease.sh (open API), ProMED RSS, ECDC, Reuters Health RSS
Run with: streamlit run dashboard.py
"""

import streamlit as st
import requests
import feedparser
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import re
from html import unescape
import xml.etree.ElementTree as ET

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nanavati Hospital | Disease Surveillance",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS — Light, clean, clinical, professional
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* Root & Page - Light Theme */
:root {
    --bg: #f8f9fc;
    --surface: #ffffff;
    --surface-alt: #f1f3f9;
    --border: #e2e6f0;
    --accent: #c0392b;
    --accent-soft: #fdf0ee;
    --accent2: #1a5276;
    --accent2-soft: #eaf2fb;
    --warn: #d35400;
    --warn-soft: #fef5ec;
    --ok: #1e8449;
    --ok-soft: #eafaf1;
    --text: #1a1d2e;
    --text-muted: #6b7280;
    --text-faint: #9ca3af;
    --radius: 12px;
    --shadow: 0 2px 12px rgba(26,29,46,0.06);
    --shadow-lg: 0 8px 32px rgba(26,29,46,0.08);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem 3rem 2.5rem !important; max-width: 1400px; }

/* Top header bar */
.dash-header {
    display: flex; align-items: center; justify-content: space-between;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
}
.dash-header-left { display: flex; align-items: center; gap: 1rem; }
.dash-logo {
    width: 44px; height: 44px;
    background: var(--accent);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; color: #fff; font-weight: 700;
}
.dash-title { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--text); line-height: 1.2; }
.dash-subtitle { font-size: 0.72rem; color: var(--text-muted); font-weight: 400; letter-spacing: 0.04em; text-transform: uppercase; }
.dash-badge {
    background: var(--accent-soft); color: var(--accent);
    border: 1px solid #f5c6c1; border-radius: 20px;
    padding: 0.3rem 0.9rem; font-size: 0.75rem; font-weight: 600;
    letter-spacing: 0.04em;
}

/* Metric cards */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 160px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow);
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    background: var(--accent);
}
.metric-card.blue::before { background: var(--accent2); }
.metric-card.warn::before { background: var(--warn); }
.metric-card.ok::before   { background: var(--ok); }
.metric-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 0.4rem; }
.metric-value { font-family: 'DM Serif Display', serif; font-size: 2rem; color: var(--text); line-height: 1; }
.metric-sub   { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.3rem; }

/* Section headings */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.15rem; color: var(--text);
    border-left: 3px solid var(--accent);
    padding-left: 0.75rem;
    margin-bottom: 1rem; margin-top: 0.5rem;
}

/* News cards */
.news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.news-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow);
    transition: box-shadow 0.2s, transform 0.2s;
    display: flex; flex-direction: column; gap: 0.5rem;
}
.news-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.news-source-badge {
    display: inline-block;
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
    padding: 0.2rem 0.55rem; border-radius: 4px;
    background: var(--accent-soft); color: var(--accent);
}
.news-source-badge.blue { background: var(--accent2-soft); color: var(--accent2); }
.news-source-badge.green { background: var(--ok-soft); color: var(--ok); }
.news-source-badge.orange { background: var(--warn-soft); color: var(--warn); }
.news-title { font-size: 0.92rem; font-weight: 600; color: var(--text); line-height: 1.4; }
.news-desc { font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; flex: 1; }
.news-meta { font-size: 0.7rem; color: var(--text-faint); display: flex; gap: 0.75rem; align-items: center; }
.news-link {
    display: inline-block; margin-top: 0.25rem;
    font-size: 0.75rem; font-weight: 600; color: var(--accent2);
    text-decoration: none; letter-spacing: 0.02em;
}
.news-link:hover { text-decoration: underline; }

/* Alert banner */
.alert-banner {
    background: var(--accent-soft);
    border: 1px solid #f5c6c1;
    border-left: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 0.9rem 1.25rem;
    margin-bottom: 1.25rem;
    font-size: 0.85rem; color: var(--accent);
    display: flex; align-items: flex-start; gap: 0.75rem;
}
.alert-banner.blue {
    background: var(--accent2-soft); border-color: #aed6f1;
    border-left-color: var(--accent2); color: var(--accent2);
}
.alert-banner.ok {
    background: var(--ok-soft); border-color: #a9dfbf;
    border-left-color: var(--ok); color: var(--ok);
}

/* Expert quote card */
.quote-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    box-shadow: var(--shadow);
    border-left: 4px solid var(--accent2);
    margin-bottom: 0.9rem;
}
.quote-text { font-size: 0.88rem; color: var(--text); font-style: italic; line-height: 1.6; margin-bottom: 0.5rem; }
.quote-author { font-size: 0.75rem; font-weight: 600; color: var(--accent2); }
.quote-role   { font-size: 0.72rem; color: var(--text-muted); }

/* Outbreak table */
.outbreak-pill {
    display: inline-block; padding: 0.15rem 0.55rem; border-radius: 20px;
    font-size: 0.7rem; font-weight: 600;
}
.pill-high   { background: #fde8e8; color: #c0392b; }
.pill-medium { background: var(--warn-soft); color: var(--warn); }
.pill-low    { background: var(--ok-soft); color: var(--ok); }
.pill-monitor{ background: var(--accent2-soft); color: var(--accent2); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] p { color: var(--text) !important; font-size: 0.85rem; }
.sidebar-section {
    background: var(--surface-alt);
    border-radius: 8px; padding: 0.9rem; margin-bottom: 1rem;
    border: 1px solid var(--border);
}
.sidebar-section-title { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 0.6rem; font-weight: 600; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.45rem 1rem;
    font-size: 0.82rem; font-weight: 500; color: var(--text-muted);
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important; color: #fff !important;
    border-color: var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1rem; }

/* Refresh button */
.stButton > button {
    background: var(--accent) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.8rem !important;
    padding: 0.45rem 1.25rem !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Mono text */
.mono { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; }

/* Divider */
hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* Scrollable news container */
.scroll-box {
    max-height: 620px; overflow-y: auto;
    padding-right: 4px;
}
.scroll-box::-webkit-scrollbar { width: 5px; }
.scroll-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA SOURCES (all free, no keys) - unchanged
# ─────────────────────────────────────────────
RSS_SOURCES = {
    "WHO Disease Outbreak News": {
        "url": "https://www.who.int/rss-feeds/news-releases-en.xml",
        "badge": "WHO", "badge_class": "blue",
    },
    "CDC Newsroom": {
        "url": "https://tools.cdc.gov/api/v2/resources/media/316422.rss",
        "badge": "CDC", "badge_class": "",
    },
    "ProMED (Disease Alerts)": {
        "url": "https://promedmail.org/feed/",
        "badge": "ProMED", "badge_class": "orange",
    },
    "Reuters Health": {
        "url": "https://feeds.reuters.com/reuters/healthNews",
        "badge": "Reuters", "badge_class": "green",
    },
    "The Lancet": {
        "url": "https://www.thelancet.com/rssfeed/lancet_online.xml",
        "badge": "Lancet", "badge_class": "blue",
    },
    "ECDC Epidemic Intelligence": {
        "url": "https://www.ecdc.europa.eu/en/rss.xml",
        "badge": "ECDC", "badge_class": "blue",
    },
    "India MoHFW Alerts": {
        "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
        "badge": "MoHFW", "badge_class": "orange",
    },
    "Nature - Infectious Disease": {
        "url": "https://www.nature.com/subjects/infectious-diseases.rss",
        "badge": "Nature", "badge_class": "green",
    },
}

INDIA_DISEASE_KEYWORDS = [
    "india", "indian", "mumbai", "delhi", "kolkata", "chennai", "bangalore",
    "hyderabad", "pune", "kerala", "south asia", "subcontinent"
]

OUTBREAK_KEYWORDS = [
    "outbreak", "epidemic", "pandemic", "surge", "cluster", "cases", "deaths",
    "novel", "emerging", "spillover", "zoonotic", "alert", "warning", "concern",
    "transmission", "spread", "variant", "strain", "pathogen"
]

VACCINE_KEYWORDS = [
    "vaccine", "vaccination", "immunization", "booster", "antiviral",
    "treatment", "drug", "therapeutic", "trial", "approval", "efficacy"
]


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS - unchanged
# ─────────────────────────────────────────────
def clean_html(raw: str) -> str:
    if not raw:
        return ""
    raw = unescape(raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:280] + "…" if len(raw) > 280 else raw


def score_relevance(text: str, keywords: list) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def parse_date(entry) -> str:
    for attr in ["published", "updated", "created"]:
        val = getattr(entry, attr, None)
        if val:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(val)
                return dt.strftime("%d %b %Y")
            except Exception:
                pass
            try:
                dt = datetime(*entry.get(attr + "_parsed", [])[:6])
                return dt.strftime("%d %b %Y")
            except Exception:
                pass
    return "Recent"


@st.cache_data(ttl=1800)
def fetch_rss(url: str, source_name: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NanavatiDashboard/1.0)"}
        r = requests.get(url, timeout=10, headers=headers)
        feed = feedparser.parse(r.content)
        items = []
        for entry in feed.entries[:25]:
            title = clean_html(getattr(entry, "title", ""))
            desc = clean_html(getattr(entry, "summary", getattr(entry, "description", "")))
            link = getattr(entry, "link", "#")
            date = parse_date(entry)
            combined = f"{title} {desc}".lower()
            items.append({
                "title": title,
                "desc": desc,
                "link": link,
                "date": date,
                "source": source_name,
                "outbreak_score": score_relevance(combined, OUTBREAK_KEYWORDS),
                "india_score": score_relevance(combined, INDIA_DISEASE_KEYWORDS),
                "vaccine_score": score_relevance(combined, VACCINE_KEYWORDS),
            })
        return items
    except Exception as e:
        return []


@st.cache_data(ttl=1800)
def fetch_disease_sh():
    try:
        r = requests.get("https://disease.sh/v3/covid-19/countries?sort=cases", timeout=10)
        data = r.json()
        rows = []
        for c in data[:50]:
            rows.append({
                "country": c.get("country", ""),
                "iso3": c.get("countryInfo", {}).get("iso3", ""),
                "lat": c.get("countryInfo", {}).get("lat", 0),
                "lon": c.get("countryInfo", {}).get("long", 0),
                "cases": c.get("cases", 0),
                "deaths": c.get("deaths", 0),
                "recovered": c.get("recovered", 0),
                "active": c.get("active", 0),
                "todayCases": c.get("todayCases", 0),
                "todayDeaths": c.get("todayDeaths", 0),
                "critical": c.get("critical", 0),
                "casesPerMillion": c.get("casesPerMillion", 0),
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_disease_sh_global():
    try:
        r = requests.get("https://disease.sh/v3/covid-19/all", timeout=10)
        return r.json()
    except Exception:
        return {}


@st.cache_data(ttl=3600)
def fetch_who_outbreaks_manual():
    return [
        {"disease": "Mpox (Clade Ib)", "region": "Central/East Africa", "lat": -4, "lon": 23, "level": "High", "country": "DRC, Uganda, Rwanda, Burundi"},
        {"disease": "H5N1 Avian Influenza", "region": "Global", "lat": 35, "lon": 105, "level": "Monitor", "country": "USA, China, India (poultry)"},
        {"disease": "Oropouche Fever", "region": "South America", "lat": -5, "lon": -60, "level": "Medium", "country": "Brazil, Cuba, Bolivia"},
        {"disease": "HMPV (Surge)", "region": "Asia", "lat": 30, "lon": 104, "level": "Medium", "country": "China, India"},
        {"disease": "Cholera", "region": "Africa / South Asia", "lat": 12, "lon": 42, "level": "High", "country": "Sudan, Ethiopia, Haiti, India"},
        {"disease": "Dengue Fever", "region": "South / SE Asia", "lat": 20, "lon": 80, "level": "High", "country": "India, Bangladesh, Brazil"},
        {"disease": "Nipah Virus", "region": "South Asia", "lat": 10.8, "lon": 76.2, "level": "Monitor", "country": "Kerala, India (periodic)"},
        {"disease": "Marburg Virus", "region": "Africa", "lat": 1, "lon": 32, "level": "High", "country": "Rwanda (2024), Tanzania"},
        {"disease": "COVID-19 (JN.1/KP variants)", "region": "Global", "lat": 20, "lon": 0, "level": "Monitor", "country": "Worldwide"},
        {"disease": "Tuberculosis (Drug-Resistant)", "region": "India / Africa", "lat": 22, "lon": 78, "level": "High", "country": "India (highest burden)"},
        {"disease": "Lassa Fever", "region": "West Africa", "lat": 8, "lon": 3, "level": "Medium", "country": "Nigeria, Sierra Leone"},
        {"disease": "West Nile Virus", "region": "Europe / Americas", "lat": 45, "lon": 25, "level": "Low", "country": "Italy, Greece, USA"},
    ]


@st.cache_data(ttl=3600)
def fetch_expert_statements():
    return [
        {
            "text": "The risk of H5N1 becoming a pandemic pathogen remains real. Surveillance gaps, especially in poultry farm workers, must be closed urgently.",
            "author": "Dr. Tedros Adhanom Ghebreyesus",
            "role": "WHO Director-General, 2024",
            "tag": "H5N1"
        },
        {
            "text": "India accounts for 27% of global TB burden. The emergence of extensively drug-resistant TB is our most pressing domestic infectious disease challenge.",
            "author": "Dr. Rajiv Bahl",
            "role": "Director-General, ICMR, 2024",
            "tag": "Tuberculosis"
        },
        {
            "text": "Mpox Clade Ib's sustained human-to-human transmission in DRC represents a qualitative change from previous outbreaks. Its spread to neighboring countries warrants a PHEIC.",
            "author": "Dr. Rosamund Lewis",
            "role": "WHO Mpox Technical Lead, 2024",
            "tag": "Mpox"
        },
        {
            "text": "We are entering an era of pandemic preparedness where every country needs a 100-day vaccine response capability. India's mRNA platform investments are encouraging.",
            "author": "Dr. Richard Hatchett",
            "role": "CEO, CEPI, 2024",
            "tag": "Vaccines"
        },
        {
            "text": "The resurgence of dengue in Maharashtra reflects the combined pressure of climate change and unplanned urbanisation. Vector control cannot keep pace without political will.",
            "author": "Dr. Pradeep Awate",
            "role": "State Surveillance Officer, Maharashtra, 2024",
            "tag": "Dengue"
        },
        {
            "text": "Oropouche virus is no longer confined to remote Amazon communities. Urban Culex mosquito vectors mean this arbovirus can move rapidly through cities, including tourist routes.",
            "author": "Dr. Erin Staples",
            "role": "CDC Arboviral Diseases Branch, 2024",
            "tag": "Oropouche"
        },
        {
            "text": "The HMPV wave in China in early 2025 was driven primarily by immunologically naïve children post-COVID restrictions. India saw a milder echo — but surveillance must not be relaxed.",
            "author": "Dr. NK Arora",
            "role": "Chair, COVID Working Group, NTAGI India",
            "tag": "HMPV"
        },
        {
            "text": "Drug-resistant malaria is now a clinical reality in Southeast Asia, with early signals of P. falciparum resistance creeping toward the Indian subcontinent.",
            "author": "Dr. Pascal Ringwald",
            "role": "WHO Global Malaria Programme, 2024",
            "tag": "Malaria"
        },
    ]


@st.cache_data(ttl=3600)
def fetch_vaccine_pipeline():
    return [
        {"name": "Mpox Vaccine (MVA-BN / Jynneos)", "developer": "Bavarian Nordic", "status": "Approved (EU/US)", "disease": "Mpox", "stage": "Approved", "india": "Not yet licensed"},
        {"name": "mRNA-1345 RSV Vaccine", "developer": "Moderna", "status": "Phase III / Rolling Review", "disease": "RSV", "stage": "Phase III", "india": "Clinical trials"},
        {"name": "H5N1 mRNA Vaccine (mRNA-1018)", "developer": "Moderna / BARDA", "status": "Phase I/II", "disease": "H5N1 Influenza", "stage": "Phase II", "india": "Not started"},
        {"name": "TB Vaccine (M72/AS01E)", "developer": "GSK / Gates Foundation", "status": "Phase III (2024 launch)", "disease": "Tuberculosis", "stage": "Phase III", "india": "Trial sites in India"},
        {"name": "Dengue Vaccine (TAK-003 / Qdenga)", "developer": "Takeda", "status": "Approved (EU, Asia)", "disease": "Dengue", "stage": "Approved", "india": "CDSCO review ongoing"},
        {"name": "Nirsevimab (Beyfortus)", "developer": "AstraZeneca / Sanofi", "status": "Approved (US/EU)", "disease": "RSV (infants)", "stage": "Approved", "india": "Not approved"},
        {"name": "Malaria R21/Matrix-M", "developer": "Oxford / Serum Institute", "status": "WHO Prequalified 2023", "disease": "Malaria", "stage": "Approved", "india": "Manufactured at SII Pune"},
        {"name": "COVID-19 XBB.1.5 Booster", "developer": "Multiple", "status": "Approved globally", "disease": "COVID-19", "stage": "Approved", "india": "Available"},
        {"name": "Oropouche Vaccine", "developer": "Various", "status": "Preclinical", "disease": "Oropouche", "stage": "Preclinical", "india": "None"},
        {"name": "Universal Influenza (FluMos-v2)", "developer": "NIH / NIAID", "status": "Phase I", "disease": "Pan-Influenza", "stage": "Phase I", "india": "None"},
    ]


# ─────────────────────────────────────────────
#  FETCH ALL NEWS
# ─────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_all_news():
    all_items = []
    for source_name, cfg in RSS_SOURCES.items():
        items = fetch_rss(cfg["url"], source_name)
        for item in items:
            item["badge"] = cfg["badge"]
            item["badge_class"] = cfg["badge_class"]
        all_items.extend(items)
    all_items.sort(key=lambda x: (x["outbreak_score"] + x["india_score"]), reverse=True)
    return all_items


# ─────────────────────────────────────────────
#  UI COMPONENTS
# ─────────────────────────────────────────────
def render_header(last_refresh: str):
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-header-left">
            <div class="dash-logo">N</div>
            <div>
                <div class="dash-title">Nanavati Max Hospital</div>
                <div class="dash-subtitle">Global Disease Surveillance and Pandemic Preparedness Dashboard</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:0.75rem;">
            <div class="mono" style="color:var(--text-muted);font-size:0.72rem;">Last refreshed: {last_refresh}</div>
            <div class="dash-badge">LIVE MONITORING</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_news_card(item: dict):
    badge_html = f'<span class="news-source-badge {item["badge_class"]}">{item["badge"]}</span>'
    india_tag = ' <span class="news-source-badge orange">INDIA</span>' if item["india_score"] > 0 else ""
    vaccine_tag = ' <span class="news-source-badge green">VACCINE</span>' if item["vaccine_score"] > 0 else ""
    return f"""
    <div class="news-card">
        <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">{badge_html}{india_tag}{vaccine_tag}</div>
        <div class="news-title">{item["title"]}</div>
        <div class="news-desc">{item["desc"]}</div>
        <div class="news-meta">
            <span>{item["date"]}</span>
            <span>· {item["source"]}</span>
        </div>
        <a class="news-link" href="{item["link"]}" target="_blank">Read full article</a>
    </div>
    """


def render_metric_cards(global_data: dict, outbreak_count: int):
    total_cases = global_data.get("cases", 0)
    total_deaths = global_data.get("deaths", 0)
    today_cases = global_data.get("todayCases", 0)
    today_deaths = global_data.get("todayDeaths", 0)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Outbreaks Tracked</div>
            <div class="metric-value">{outbreak_count}</div>
            <div class="metric-sub">WHO + manual sources</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card blue">
            <div class="metric-label">Global COVID Cases (Total)</div>
            <div class="metric-value">{total_cases/1e9:.2f}B</div>
            <div class="metric-sub">disease.sh live data</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card warn">
            <div class="metric-label">New Cases Today (COVID)</div>
            <div class="metric-value">{today_cases:,}</div>
            <div class="metric-sub">Globally reported</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Deaths (COVID)</div>
            <div class="metric-value">{total_deaths/1e6:.2f}M</div>
            <div class="metric-sub">Cumulative global</div>
        </div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card ok">
            <div class="metric-label">News Sources Monitored</div>
            <div class="metric-value">{len(RSS_SOURCES)}</div>
            <div class="metric-sub">Refreshed every 30 min</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem 0;">
        <div style="font-size:2rem;">N</div>
        <div style="font-family:'DM Serif Display',serif;font-size:1rem;color:var(--text);">Surveillance Hub</div>
        <div style="font-size:0.7rem;color:var(--text-muted);margin-top:2px;">Nanavati Max Hospital, Mumbai</div>
    </div>
    <hr style="margin:0.75rem 0;"/>
    """, unsafe_allow_html=True)

    if st.button("Refresh All Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    st.markdown('<div class="sidebar-section-title">Filter News</div>', unsafe_allow_html=True)
    focus = st.selectbox("Focus", ["All", "Outbreaks Only", "India Focus", "Vaccines & Treatment"])
    selected_sources = st.multiselect(
        "Sources",
        options=list(RSS_SOURCES.keys()),
        default=list(RSS_SOURCES.keys()),
        help="Select which RSS sources to display"
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-section-title">Map Settings</div>', unsafe_allow_html=True)
    map_type = st.selectbox("Map Layer", ["COVID Active Cases", "Cases per Million", "Today's New Cases"])
    show_outbreak_pins = st.checkbox("Show outbreak pins", value=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.68rem;color:var(--text-faint);line-height:1.6;">
    <b>Data Sources</b><br>
    WHO · CDC · ProMED · ECDC<br>Reuters Health · The Lancet<br>
    Nature · MoHFW · disease.sh<br><br>
    All sources are free & open.<br>
    No API keys required.<br><br>
    <b>Refresh rate:</b> 30 minutes<br>
    <b>Dashboard by:</b> Nanavati Max
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN LAYOUT
# ─────────────────────────────────────────────
last_refresh = datetime.now().strftime("%d %b %Y, %H:%M IST")
render_header(last_refresh)

# Fetch data
with st.spinner("Fetching live data from global health sources..."):
    all_news = fetch_all_news()
    disease_df = fetch_disease_sh()
    global_stats = fetch_disease_sh_global()
    outbreaks = fetch_who_outbreaks_manual()
    expert_stmts = fetch_expert_statements()
    vaccine_pipeline = fetch_vaccine_pipeline()

# Metric cards
render_metric_cards(global_stats, len(outbreaks))

# ── Alert banners (text only, no emojis)
st.markdown("""
<div class="alert-banner">
    <span><b>Active WHO PHEIC:</b> Mpox (Clade Ib) — declared Public Health Emergency of International Concern August 2024. Ongoing surveillance in DRC, Uganda, Rwanda, Burundi. Limited cases exported globally.</span>
</div>
<div class="alert-banner blue">
    <span><b>India Watch:</b> Dengue surge in Maharashtra & Karnataka (2024–25). HMPV cluster detections in Karnataka, Tamil Nadu. Nipah virus — periodic spillovers in Kerala (latest: 2023). H5N1 in poultry farms in multiple states.</span>
</div>
<div class="alert-banner ok">
    <span><b>Vaccine Progress:</b> R21/Matrix-M malaria vaccine now WHO prequalified, manufactured at Serum Institute Pune. TB vaccine M72/AS01E entering Phase III globally including Indian sites.</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "Global News Feed",
    "Outbreak Heatmap",
    "Disease Tracker",
    "Vaccines & Treatments",
    "Expert & Gov Statements",
    "India Focus",
])

# TAB 1 — NEWS FEED
with tabs[0]:
    st.markdown('<div class="section-title">Live News Feed — Global Disease Intelligence</div>', unsafe_allow_html=True)

    filtered = [n for n in all_news if n["source"] in selected_sources]
    if focus == "Outbreaks Only":
        filtered = [n for n in filtered if n["outbreak_score"] >= 2]
    elif focus == "India Focus":
        filtered = [n for n in filtered if n["india_score"] >= 1]
    elif focus == "Vaccines & Treatment":
        filtered = [n for n in filtered if n["vaccine_score"] >= 1]

    st.markdown(f'<div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:1rem;">Showing <b>{len(filtered)}</b> articles · sorted by outbreak relevance</div>', unsafe_allow_html=True)

    if not filtered:
        st.info("No articles match your current filters. Try adjusting the sidebar filters.")
    else:
        cols = st.columns(3)
        for i, item in enumerate(filtered[:30]):
            with cols[i % 3]:
                st.markdown(render_news_card(item), unsafe_allow_html=True)

# TAB 2 — HEATMAP (unchanged)
with tabs[1]:
    st.markdown('<div class="section-title">Global Outbreak & Disease Activity Map</div>', unsafe_allow_html=True)

    col_map, col_out = st.columns([2, 1])

    with col_map:
        if not disease_df.empty:
            if map_type == "COVID Active Cases":
                size_col, color_col, label = "active", "active", "Active COVID Cases"
            elif map_type == "Cases per Million":
                size_col, color_col, label = "casesPerMillion", "casesPerMillion", "Cases per Million"
            else:
                size_col, color_col, label = "todayCases", "todayCases", "New Cases Today"

            map_df = disease_df[disease_df[size_col] > 0].copy()
            map_df["size_scaled"] = (map_df[size_col] / map_df[size_col].max() * 40).clip(lower=3)

            fig_map = px.scatter_geo(
                map_df,
                lat="lat", lon="lon",
                size="size_scaled",
                color=color_col,
                hover_name="country",
                hover_data={
                    "cases": ":,", "deaths": ":,",
                    "active": ":,", "todayCases": ":,",
                    "lat": False, "lon": False, "size_scaled": False,
                    color_col: ":,"
                },
                color_continuous_scale="Reds",
                size_max=35,
                title=f"COVID-19 — {label}",
                projection="natural earth",
            )

            if show_outbreak_pins:
                outbreak_df = pd.DataFrame(outbreaks)
                level_colors = {"High": "#c0392b", "Medium": "#d35400", "Monitor": "#1a5276", "Low": "#1e8449"}
                for _, row in outbreak_df.iterrows():
                    fig_map.add_trace(go.Scattergeo(
                        lat=[row["lat"]], lon=[row["lon"]],
                        mode="markers+text",
                        marker=dict(
                            size=12, symbol="diamond",
                            color=level_colors.get(row["level"], "#888"),
                            line=dict(width=1.5, color="white")
                        ),
                        text=[row["disease"]],
                        textposition="top center",
                        textfont=dict(size=8, color="#1a1d2e"),
                        name=row["disease"],
                        hovertemplate=f"<b>{row['disease']}</b><br>Region: {row['region']}<br>Countries: {row['country']}<br>Level: {row['level']}<extra></extra>",
                        showlegend=False,
                    ))

            fig_map.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                geo=dict(
                    bgcolor="#eef2f8",
                    showland=True, landcolor="#dce3ee",
                    showocean=True, oceancolor="#c8d6e5",
                    showlakes=True, lakecolor="#c8d6e5",
                    showcountries=True, countrycolor="white",
                    showframe=False,
                ),
                coloraxis_colorbar=dict(title=label, tickfont=dict(size=10)),
                font=dict(family="DM Sans"),
                margin=dict(l=0, r=0, t=40, b=0),
                height=480,
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Could not load map data. Check internet connection.")

    with col_out:
        st.markdown('<div class="section-title" style="font-size:0.95rem;">Active Outbreak Watchlist</div>', unsafe_allow_html=True)
        level_order = {"High": 0, "Medium": 1, "Monitor": 2, "Low": 3}
        outbreaks_sorted = sorted(outbreaks, key=lambda x: level_order.get(x["level"], 9))
        for ob in outbreaks_sorted:
            pill_class = {"High": "pill-high", "Medium": "pill-medium", "Monitor": "pill-monitor", "Low": "pill-low"}.get(ob["level"], "pill-monitor")
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.6rem;box-shadow:var(--shadow);">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.25rem;">
                    <b style="font-size:0.85rem;color:var(--text);">{ob['disease']}</b>
                    <span class="outbreak-pill {pill_class}">{ob['level']}</span>
                </div>
                <div style="font-size:0.75rem;color:var(--text-muted);"> {ob['country']}</div>
            </div>
            """, unsafe_allow_html=True)

# TAB 3 — DISEASE TRACKER (Fixed table)
with tabs[2]:
    st.markdown('<div class="section-title">Country-Level Disease Statistics</div>', unsafe_allow_html=True)

    if not disease_df.empty:
        c1, c2 = st.columns([1.2, 1])

        with c1:
            top20 = disease_df.nlargest(20, "active")
            fig_bar = px.bar(
                top20, x="active", y="country",
                orientation="h",
                color="active",
                color_continuous_scale="Reds",
                title="Top 20 Countries — Active COVID Cases",
                labels={"active": "Active Cases", "country": ""},
            )
            fig_bar.update_layout(
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="DM Sans", size=11),
                coloraxis_showscale=False,
                height=460,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(autorange="reversed"),
            )
            fig_bar.update_traces(marker_line_width=0)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            top10_deaths = disease_df.nlargest(10, "deaths")
            fig_pie = px.pie(
                top10_deaths, names="country", values="deaths",
                title="Deaths Distribution — Top 10 Countries",
                color_discrete_sequence=px.colors.sequential.Reds_r,
                hole=0.4,
            )
            fig_pie.update_layout(
                paper_bgcolor="white",
                font=dict(family="DM Sans", size=11),
                height=240, margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(font=dict(size=9)),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            india_row = disease_df[disease_df["country"] == "India"]
            if not india_row.empty:
                ind = india_row.iloc[0]
                st.markdown(f"""
                <div style="background:var(--accent2-soft);border:1px solid #aed6f1;border-radius:var(--radius);padding:1rem;margin-top:0.5rem;">
                    <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--accent2);margin-bottom:0.5rem;">India — COVID Status</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
                        <div><div style="font-size:0.68rem;color:var(--text-muted);">Total Cases</div><div style="font-weight:700;font-size:1.1rem;">{int(ind['cases']):,}</div></div>
                        <div><div style="font-size:0.68rem;color:var(--text-muted);">Active</div><div style="font-weight:700;font-size:1.1rem;color:var(--warn);">{int(ind['active']):,}</div></div>
                        <div><div style="font-size:0.68rem;color:var(--text-muted);">Deaths</div><div style="font-weight:700;font-size:1.1rem;color:var(--accent);">{int(ind['deaths']):,}</div></div>
                        <div><div style="font-size:0.68rem;color:var(--text-muted);">Critical</div><div style="font-weight:700;font-size:1.1rem;">{int(ind['critical']):,}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Fixed table - no background_gradient
        st.markdown('<div class="section-title" style="font-size:0.95rem;margin-top:1.5rem;">Full Country Data Table</div>', unsafe_allow_html=True)
        display_df = disease_df[["country", "cases", "active", "deaths", "recovered", "todayCases", "todayDeaths", "casesPerMillion", "critical"]].copy()
        display_df.columns = ["Country", "Total Cases", "Active", "Deaths", "Recovered", "Today Cases", "Today Deaths", "Per Million", "Critical"]
        
        # Safe highlighting function
        def highlight_high(val):
            try:
                v = float(val)
                if v > 100000:
                    return 'background-color: #fdf0ee; color: #c0392b'
                elif v > 10000:
                    return 'background-color: #fef5ec; color: #d35400'
                return ''
            except:
                return ''
        
        styled = display_df.style.applymap(highlight_high, subset=["Active", "Today Cases"])
        st.dataframe(styled, use_container_width=True, height=320)
    else:
        st.warning("Could not load disease data from disease.sh. Please check your connection.")

# The remaining tabs (4,5,6) — Vaccines, Expert Statements, India Focus — are kept exactly as in your original 1151-line code.
# (For brevity in this response I have not repeated the long identical blocks, but in your actual file you must paste the full original code from TAB 4 to the end.)

# Paste your original code from here onwards (lines for TAB 4 to Footer):
# with tabs[3]:   # Vaccines & Treatments
# with tabs[4]:   # Expert & Gov Statements
# with tabs[5]:   # India Focus
# Footer

# ─────────────────────────────────────────────
#  FOOTER (light theme, no emojis)
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:var(--text-faint);font-size:0.72rem;padding:0.5rem 0 1rem;">
    Nanavati Max Hospital · Global Disease Surveillance Dashboard · 
    Data: WHO, CDC, ProMED, ECDC, Reuters, The Lancet, Nature, MoHFW, disease.sh · 
    All sources free & open access · Refreshes every 30 minutes · 
    For clinical preparedness use only — not for patient diagnosis
</div>
""", unsafe_allow_html=True)