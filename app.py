import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os
import math
import io
import base64
import calendar
from PIL import Image, ImageFilter, ImageChops

# ─── Theme & Layout ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CART SULPHUR OPS • 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif !important;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(1200px 600px at 15% 10%, rgba(120, 70, 190, 0.18), transparent 60%),
                    linear-gradient(135deg, #120f1b 0%, #171225 45%, #0f0c18 100%);
        color: #efe6ff;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(22, 18, 32, 0.98) 0%, rgba(16, 13, 24, 0.98) 100%);
        border-right: 1px solid rgba(214, 170, 255, 0.18);
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        width: 14rem;
        min-width: 14rem;
        max-width: 14rem;
        z-index: 1000;
        box-shadow: 0 18px 40px rgba(13, 10, 22, 0.6);
        overflow: hidden;
        will-change: transform;
        transition: none;
        transform: translateX(0) !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 14rem !important;
        min-width: 14rem !important;
        max-width: 14rem !important;
        transform: translateX(0) !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 0;
        margin-top: -0.55cm;
    }
    [data-testid="stAppViewContainer"] .block-container {
        padding-top: 0;
        margin-top: -0.3cm;
    }
    header[data-testid="stHeader"] {
        background: transparent;
        box-shadow: none;
        height: 0;
        padding: 0;
    }
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
        position: fixed;
        top: 0.8rem;
        left: 0.85rem;
        z-index: 1001;
        background: linear-gradient(135deg, rgba(255, 94, 197, 0.85), rgba(188, 92, 255, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px;
        padding: 0.35rem 0.8rem;
        box-shadow: 0 8px 20px rgba(188, 92, 255, 0.25);
        align-items: center;
        justify-content: center;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 0;
            min-width: 0;
            max-width: 0;
            transform: translateX(-110%) !important;
            box-shadow: none;
            visibility: hidden !important;
            pointer-events: none !important;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            width: 0 !important;
            min-width: 0 !important;
            max-width: 0 !important;
            transform: translateX(-110%) !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
        [data-testid="stSidebar"][aria-expanded="true"] {
            width: 14rem !important;
            min-width: 14rem !important;
            max-width: 14rem !important;
            transform: translateX(0) !important;
            box-shadow: 0 18px 40px rgba(13, 10, 22, 0.6);
            visibility: visible !important;
            pointer-events: auto !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: flex !important;
        }
    }
    [data-testid="stSidebarCollapseButton"] button {
        color: #ffffff;
        font-weight: 700;
        letter-spacing: 0.08em;
    }
    .stMetric,
    [data-testid="stMetric"] {
        background: rgba(34, 26, 48, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(214, 170, 255, 0.28);
        border-radius: 16px;
        padding: 1rem;
        min-height: 120px;
        text-align: center;
    }
    .stMetric > div:first-child,
    [data-testid="stMetric"] > div:first-child,
    [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    .stMetric label {
        font-size: 10px !important;
        text-align: center;
        width: 100%;
    }
    [data-testid="stMetric"] > div {
        align-items: center !important;
        justify-content: center !important;
    }
    .stMetric [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        color: #f2eafb;
        text-shadow: 0 0 10px rgba(255, 210, 255, 0.22);
    }
    .stMetric [data-testid="stMetricDelta"],
    [data-testid="stMetricDelta"] {
        font-size: 13px;
        font-weight: 600;
        text-align: center;
    }
    .metric-card {
        background: rgba(34, 26, 48, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(214, 170, 255, 0.28);
        border-radius: 16px;
        padding: 1rem;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        position: relative;
    }
    .metric-title {
        font-size: 10px;
        color: #f2e7ff;
        margin: 0;
        text-align: center;
        margin-bottom: 0.6rem;
    }
    .status-value {
        font-size: 18px;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    .status-delta {
        font-size: 12px;
        font-weight: 600;
        color: #c5a4ff;
        margin: 0.35rem 0 0 0;
        text-align: center;
    }
    .metric-blocks {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.35rem 0.6rem;
        margin-top: 0;
        justify-items: center;
    }
    .metric-blocks.single {
        grid-template-columns: 1fr;
        place-items: center;
    }
    .metric-card.compact {
        min-height: 100px;
        padding-bottom: 0.7rem;
    }
    .metric-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.1rem;
        text-align: center;
    }
    .metric-block-label {
        font-size: 11px;
        color: #cdb8ff;
    }
    .metric-block-value {
        font-size: 20px;
        font-weight: 700;
        color: #f2eafb;
        line-height: 1.1;
        text-align: center;
        width: 100%;
        text-shadow: 0 0 8px rgba(255, 210, 255, 0.22);
    }
    .metric-stack {
        background: rgba(34, 26, 48, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(214, 170, 255, 0.28);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-top: 0.4rem;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 0.25rem 0;
        border-bottom: 1px solid rgba(214, 170, 255, 0.16);
    }
    .metric-row:last-child {
        border-bottom: none;
    }
    .metric-label {
        font-size: 13px;
        color: #cdb8ff;
    }
    .metric-value {
        font-size: 18px;
        font-weight: 700;
        color: #f2eafb;
        text-shadow: 0 0 8px rgba(255, 210, 255, 0.22);
    }
    h1, h2, h3 { color: #e7c6ff !important; }
    hr { border-color: rgba(190, 120, 255, 0.35) !important; }
    .center-caption {
        text-align: center;
        color: #d6b9ff;
        margin: 1.8rem 0 0.5rem 0;
    }
    .section-gap {
        height: 0.8rem;
    }
    .section-gap-tight {
        height: 0.2rem;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e7c6ff;
        margin: 0;
    }
    .section-block {
        margin: 0;
    }
    .section-block .section-content {
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
    }
    .section-divider {
        border: 0;
        height: 1px;
        background: rgba(190, 120, 255, 0.35);
        margin: 0.2rem 0 0.3rem 0;
    }
    .card-row-gap {
        height: 0.35rem;
    }
    .dashboard-header {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0.2rem;
        margin-bottom: 1.2rem;
        width: 100%;
    }
    .dashboard-title {
        text-align: center;
        margin: 0;
        font-size: 2.4rem;
        font-weight: 800;
        color: #f2d9ff;
        letter-spacing: 0.02em;
        width: 100%;
        display: inline-block;
        padding: 0;
        position: relative;
        line-height: 1.05;
    }
    .dashboard-title::after {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: -6px;
        width: 97%;
        height: 2px;
        background: rgba(208, 140, 255, 0.55);
        border-radius: 999px;
    }
    .title-icon {
        color: #ffffff;
        margin-right: 0.5rem;
        font-size: 1.2rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.2rem;
        height: 1.2rem;
        vertical-align: middle;
        transform: translateY(-1px);
    }
    .stRadio [role="radiogroup"] {
        margin-top: 0.6rem;
        gap: 0.25rem;
    }
    .stRadio [role="radiogroup"] label {
        margin: 0;
    }
    .stRadio [role="radiogroup"] input {
        display: none;
    }
    .stRadio [role="radiogroup"] label > div {
        padding: 0.6rem 0.9rem 0.6rem 1.1rem;
        border-radius: 10px;
        border: 1px solid transparent;
        background: transparent;
        color: #cdb8ff;
        font-weight: 600;
        letter-spacing: 0.01em;
        position: relative;
        transition: all 0.2s ease;
    }
    .stRadio [role="radiogroup"] label > div::before {
        content: "";
        position: absolute;
        left: 0.5rem;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 62%;
        border-radius: 3px;
        background: rgba(214, 170, 255, 0.25);
        transition: all 0.2s ease;
    }
    .stRadio [data-baseweb="radio"] > div:first-child,
    .stRadio [data-baseweb="radio"] > div:first-child > div {
        display: none !important;
    }
    .stRadio [role="radiogroup"] label > div:hover {
        background: rgba(44, 34, 60, 0.6);
        color: #efe6ff;
    }
    .stRadio [role="radiogroup"] input:checked + div {
        background: transparent;
        border-color: transparent;
        color: #ffffff;
        box-shadow: none;
    }
    .stRadio [role="radiogroup"] input:checked + div::before {
        background: linear-gradient(180deg, rgba(255, 94, 197, 0.9), rgba(188, 92, 255, 0.9));
        height: 72%;
    }
    .sidebar-nav-group {
        margin-top: 1cm;
    }
    .sidebar-logo {
        display: block;
        width: 180px;
        max-width: 100%;
        margin: -1.7cm auto 0 auto;
    }
    .sim-footer-card {
        margin-bottom: 0.6rem;
    }
    .mini-info {
        position: absolute;
        top: -4.6rem;
        right: 0.6rem;
        display: flex;
        gap: 0.6rem;
        justify-content: center;
        align-items: center;
        padding: 0.4rem 0.6rem;
        border-radius: 999px;
        background: rgba(36, 26, 52, 0.5);
        border: 1px solid rgba(214, 170, 255, 0.2);
        font-size: 0.72rem;
        color: #d7c3ff;
        text-align: center;
        width: fit-content;
        z-index: 2;
    }
    .mini-info-top {
        top: -7.4rem;
    }
    .mini-info strong {
        color: #f2eafb;
        font-weight: 600;
    }
    [data-testid="stExpander"] .streamlit-expanderContent {
        padding-bottom: 0.8rem;
    }
    @media (max-width: 768px) {
        .modebar { display: none !important; }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─── Database Setup ────────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "cart_sulphur_ops.db")
DEFAULT_MONTHLY_ALLOCATION_MT = 1250
DEFAULT_FINISH_BY_DAY = 25
TRUCK_CAPACITY_MT = 34
LOADING_ORDERS_TARGET_TRUCKS = 37

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def migrate_db():
    """Apply schema migrations"""
    conn = get_conn()
    cur = conn.cursor()
    def table_exists(name: str) -> bool:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cur.fetchone() is not None
    
    cur.execute("PRAGMA table_info(monthly_plan)")
    columns = [col[1] for col in cur.fetchall()]
    
    if "finish_by_day" not in columns:
        cur.execute("ALTER TABLE monthly_plan ADD COLUMN finish_by_day INTEGER NOT NULL DEFAULT 25")
        conn.commit()
    
    if not table_exists("transporter_daily_pickups"):
        cur.execute("""
        CREATE TABLE transporter_daily_pickups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pickup_date TEXT NOT NULL,
            transporter_name TEXT NOT NULL,
            trucks_picked INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(pickup_date, transporter_name)
        )
        """)
        conn.commit()

    if not table_exists("loading_orders"):
        cur.execute("""
        CREATE TABLE loading_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_key TEXT UNIQUE NOT NULL,
            orders_paid INTEGER NOT NULL,
            orders_open INTEGER NOT NULL,
            orders_paid_polytra INTEGER NOT NULL DEFAULT 0,
            orders_paid_trammo INTEGER NOT NULL DEFAULT 0,
            orders_paid_polytra_base INTEGER NOT NULL DEFAULT 0,
            orders_paid_trammo_base INTEGER NOT NULL DEFAULT 0
        )
        """)
        conn.commit()
    else:
        cur.execute("PRAGMA table_info(loading_orders)")
        loading_cols = [col[1] for col in cur.fetchall()]
        if "orders_paid_polytra" not in loading_cols:
            cur.execute("ALTER TABLE loading_orders ADD COLUMN orders_paid_polytra INTEGER NOT NULL DEFAULT 0")
            conn.commit()
        if "orders_paid_trammo" not in loading_cols:
            cur.execute("ALTER TABLE loading_orders ADD COLUMN orders_paid_trammo INTEGER NOT NULL DEFAULT 0")
            conn.commit()
        if "orders_paid_polytra_base" not in loading_cols:
            cur.execute("ALTER TABLE loading_orders ADD COLUMN orders_paid_polytra_base INTEGER NOT NULL DEFAULT 0")
            conn.commit()
        if "orders_paid_trammo_base" not in loading_cols:
            cur.execute("ALTER TABLE loading_orders ADD COLUMN orders_paid_trammo_base INTEGER NOT NULL DEFAULT 0")
            conn.commit()
    
    if table_exists("transporters"):
        cur.execute("""
            UPDATE transporters
            SET name=?
            WHERE name=? AND NOT EXISTS (
                SELECT 1 FROM transporters WHERE name=?
            )
        """, ("Polytra", "Poly Self Transport", "Polytra"))
        cur.execute("""
            UPDATE transporters
            SET name=?
            WHERE name=? AND NOT EXISTS (
                SELECT 1 FROM transporters WHERE name=?
            )
        """, ("Reload (Trammo)", "Reload (Tram)", "Reload (Trammo)"))
        cur.execute("DELETE FROM transporters WHERE name=?", ("Poly Self Transport",))
        cur.execute("DELETE FROM transporters WHERE name=?", ("Reload (Tram)",))
        conn.commit()
    if table_exists("transporter_allocation"):
        cur.execute("UPDATE transporter_allocation SET transporter_name=? WHERE transporter_name=?", ("Polytra", "Poly Self Transport"))
        cur.execute("UPDATE transporter_allocation SET transporter_name=? WHERE transporter_name=?", ("Reload (Trammo)", "Reload (Tram)"))
        conn.commit()
    if table_exists("transporter_daily_pickups"):
        cur.execute("UPDATE transporter_daily_pickups SET transporter_name=? WHERE transporter_name=?", ("Polytra", "Poly Self Transport"))
        cur.execute("UPDATE transporter_daily_pickups SET transporter_name=? WHERE transporter_name=?", ("Reload (Trammo)", "Reload (Tram)"))
        conn.commit()
    
    conn.close()

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS transporters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        contact_name TEXT,
        contact_phone TEXT,
        contact_email TEXT,
        notes TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS monthly_plan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month_key TEXT UNIQUE NOT NULL,
        allocation_mt REAL NOT NULL,
        finish_by_day INTEGER NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS transporter_allocation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month_key TEXT NOT NULL,
        transporter_name TEXT NOT NULL,
        allocation_mt REAL NOT NULL,
        UNIQUE(month_key, transporter_name)
    )""")

    conn.commit()

    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", ("supplier_name", "Sasol"))
    cur.execute("INSERT OR IGNORE INTO transporters(name) VALUES(?)", ("Polytra",))
    cur.execute("INSERT OR IGNORE INTO transporters(name) VALUES(?)", ("Reload (Trammo)",))

    conn.commit()
    conn.close()

def month_key_for(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"

def ensure_month_plan(mkey: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT allocation_mt FROM monthly_plan WHERE month_key=?", (mkey,))
    if not cur.fetchone():
        cur.execute("INSERT INTO monthly_plan(month_key, allocation_mt, finish_by_day) VALUES(?,?,?)",
                    (mkey, DEFAULT_MONTHLY_ALLOCATION_MT, DEFAULT_FINISH_BY_DAY))
        conn.commit()
        
        default_per_transporter = DEFAULT_MONTHLY_ALLOCATION_MT / 2
        cur.execute("INSERT OR IGNORE INTO transporter_allocation(month_key, transporter_name, allocation_mt) VALUES(?,?,?)",
                    (mkey, "Polytra", default_per_transporter))
        cur.execute("INSERT OR IGNORE INTO transporter_allocation(month_key, transporter_name, allocation_mt) VALUES(?,?,?)",
                    (mkey, "Reload (Trammo)", default_per_transporter))
        conn.commit()
    conn.close()

def ensure_loading_orders(mkey: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM loading_orders WHERE month_key=?", (mkey,))
    if not cur.fetchone():
        cur.execute(
            """
            INSERT INTO loading_orders(
                month_key,
                orders_paid,
                orders_open,
                orders_paid_polytra,
                orders_paid_trammo,
                orders_paid_polytra_base,
                orders_paid_trammo_base
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (mkey, 0, 0, 0, 0, 0, 0),
        )
        conn.commit()
    conn.close()

def read_df(query, params=()):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def exec_sql(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

init_db()
migrate_db()

today = date.today()
current_mkey = month_key_for(today)
SIDEBAR_LOGO_PATH = "assets/cart-full-logo-white.png"

def load_logo_image(path: str, width: int | None = None):
    try:
        img = Image.open(path).convert("RGBA")
    except (OSError, FileNotFoundError):
        return None
    if width:
        scale = width / img.size[0]
        height = max(1, int(img.size[1] * scale))
        img = img.resize((width, height), Image.LANCZOS)
    return img

def enhance_sidebar_logo(img: Image.Image) -> Image.Image:
    alpha = img.split()[-1]
    glow = Image.new("RGBA", img.size, (255, 120, 230, 0))
    glow.putalpha(alpha)
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    r, g, b, a = glow.split()
    a = a.point(lambda p: int(p * 0.35))
    glow = Image.merge("RGBA", (r, g, b, a))
    combined = Image.alpha_composite(glow, img)
    return combined.filter(ImageFilter.UnsharpMask(radius=1.6, percent=180, threshold=2))

def image_to_base64_png(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def list_month_keys():
    months = set()
    plan_months = read_df("SELECT month_key FROM monthly_plan")
    if len(plan_months):
        months.update(plan_months["month_key"].tolist())
    pickup_months = read_df("SELECT DISTINCT substr(pickup_date, 1, 7) AS month_key FROM transporter_daily_pickups")
    if len(pickup_months):
        months.update(pickup_months["month_key"].tolist())
    months.add(current_mkey)
    return sorted(months, reverse=True)

# ─── Load Data ─────────────────────────────────────────────────────────────
SIDEBAR_LOGO_RENDER_WIDTH = 180
sidebar_logo = load_logo_image(SIDEBAR_LOGO_PATH, width=SIDEBAR_LOGO_RENDER_WIDTH * 2)
if sidebar_logo:
    sidebar_logo = enhance_sidebar_logo(sidebar_logo)
    logo_b64 = image_to_base64_png(sidebar_logo)
    st.sidebar.markdown(
        f"<img class='sidebar-logo' src='data:image/png;base64,{logo_b64}' alt='CART logo' />",
        unsafe_allow_html=True,
    )

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()
is_admin = False
admin_param = ""
if ADMIN_TOKEN:
    admin_param = st.query_params.get("admin", "")
    if isinstance(admin_param, list):
        admin_param = admin_param[0] if admin_param else ""
    if admin_param and admin_param == ADMIN_TOKEN:
        is_admin = True

st.sidebar.markdown("<div class='sidebar-nav-group'>", unsafe_allow_html=True)
if is_admin:
    page = st.sidebar.radio("Navigate", ["Dashboard", "Monthly Data", "Daily Planner", "Settings"])
else:
    page = st.sidebar.radio("Navigate", ["Dashboard", "Monthly Data"])
    # Admin hints hidden for public view
st.sidebar.markdown("</div>", unsafe_allow_html=True)

available_months = list_month_keys()
default_index = available_months.index(current_mkey) if current_mkey in available_months else 0
mkey = current_mkey
if page == "Monthly Data":
    mkey = st.selectbox("Month", available_months, index=default_index)
ensure_month_plan(mkey)
ensure_loading_orders(mkey)

plan_df = read_df("SELECT allocation_mt, finish_by_day FROM monthly_plan WHERE month_key=?", (mkey,))
allocation_mt = float(plan_df.iloc[0]["allocation_mt"]) if len(plan_df) else DEFAULT_MONTHLY_ALLOCATION_MT
finish_by_day = int(plan_df.iloc[0]["finish_by_day"]) if len(plan_df) else DEFAULT_FINISH_BY_DAY

selected_year, selected_month = [int(part) for part in mkey.split("-")]
month_start = date(selected_year, selected_month, 1)
last_day = calendar.monthrange(selected_year, selected_month)[1]
finish_by_date = date(selected_year, selected_month, min(finish_by_day, last_day))
as_of_date = today if mkey == current_mkey else finish_by_date

trans_alloc_df = read_df("SELECT transporter_name, allocation_mt FROM transporter_allocation WHERE month_key=?", (mkey,))
trans_alloc = {row["transporter_name"]: float(row["allocation_mt"]) for _, row in trans_alloc_df.iterrows()}

loading_orders_df = read_df(
    """
    SELECT
        orders_paid,
        orders_open,
        orders_paid_polytra,
        orders_paid_trammo,
        orders_paid_polytra_base,
        orders_paid_trammo_base
    FROM loading_orders
    WHERE month_key=?
    """,
    (mkey,),
)
orders_paid = int(loading_orders_df.iloc[0]["orders_paid"]) if len(loading_orders_df) else 0
orders_paid_polytra = int(loading_orders_df.iloc[0]["orders_paid_polytra"]) if len(loading_orders_df) else 0
orders_paid_trammo = int(loading_orders_df.iloc[0]["orders_paid_trammo"]) if len(loading_orders_df) else 0
orders_paid_polytra_base = int(loading_orders_df.iloc[0]["orders_paid_polytra_base"]) if len(loading_orders_df) else 0
orders_paid_trammo_base = int(loading_orders_df.iloc[0]["orders_paid_trammo_base"]) if len(loading_orders_df) else 0

trans_daily_pickups = read_df(
    "SELECT pickup_date, transporter_name, trucks_picked FROM transporter_daily_pickups WHERE pickup_date LIKE ? ORDER BY pickup_date",
    (f"{mkey}%",)
)

total_trucks_picked = int(trans_daily_pickups["trucks_picked"].sum()) if len(trans_daily_pickups) else 0
total_mt_picked = float(total_trucks_picked * TRUCK_CAPACITY_MT)

poly_trucks = int(trans_daily_pickups[trans_daily_pickups["transporter_name"] == "Polytra"]["trucks_picked"].sum()) if len(trans_daily_pickups) else 0
poly_mt = float(poly_trucks * TRUCK_CAPACITY_MT)

tram_trucks = int(trans_daily_pickups[trans_daily_pickups["transporter_name"] == "Reload (Trammo)"]["trucks_picked"].sum()) if len(trans_daily_pickups) else 0
tram_mt = float(tram_trucks * TRUCK_CAPACITY_MT)

remaining = allocation_mt - total_mt_picked
days_left = max(0, (finish_by_date - as_of_date).days)

# Calculate days until finish-by for transporter performance
days_until_finish = max(1, (finish_by_date - as_of_date).days)

if page == "Dashboard":
    st.markdown(
        """
        <div class="dashboard-header">
            <h1 class="dashboard-title">Sasol Sulphur • Control Centre</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='section-title'><span class='title-icon'>✦</span>Summary — {month_start.strftime('%B %Y')}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='section-content'>", unsafe_allow_html=True)

    # KPI Metrics
    cols = st.columns(4)
    with cols[0]:
        target_trucks = allocation_mt / TRUCK_CAPACITY_MT
        st.markdown(
            f"""
            <div class="metric-card">
                <p class="metric-title">Target (MT)</p>
                <div class="metric-blocks">
                    <div class="metric-block">
                        <span class="metric-block-label">MT</span>
                        <span class="metric-block-value">{allocation_mt:,.0f}</span>
                    </div>
                    <div class="metric-block">
                        <span class="metric-block-label">Trucks</span>
                        <span class="metric-block-value">{target_trucks:,.1f}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            f"""
            <div class="metric-card">
                <p class="metric-title">Picked up</p>
                <div class="metric-blocks">
                    <div class="metric-block">
                        <span class="metric-block-label">MT</span>
                        <span class="metric-block-value">{total_mt_picked:,.0f}</span>
                    </div>
                    <div class="metric-block">
                        <span class="metric-block-label">Trucks</span>
                        <span class="metric-block-value">{total_trucks_picked:,}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[2]:
        remaining_trucks = remaining / TRUCK_CAPACITY_MT
        st.markdown(
            f"""
            <div class="metric-card">
                <p class="metric-title">Remaining</p>
                <div class="metric-blocks">
                    <div class="metric-block">
                        <span class="metric-block-label">MT</span>
                        <span class="metric-block-value">{remaining:,.0f}</span>
                    </div>
                    <div class="metric-block">
                        <span class="metric-block-label">Trucks</span>
                        <span class="metric-block-value">{remaining_trucks:,.1f}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[3]:
        last_poly_date = "—"
        last_tram_date = "—"
        last_poly_trucks = 0
        last_tram_trucks = 0
        if len(trans_daily_pickups):
            poly_dates = trans_daily_pickups[trans_daily_pickups["transporter_name"] == "Polytra"]["pickup_date"]
            tram_dates = trans_daily_pickups[trans_daily_pickups["transporter_name"] == "Reload (Trammo)"]["pickup_date"]
            if len(poly_dates):
                poly_last_date = pd.to_datetime(poly_dates).max().date()
                last_poly_date = poly_last_date.strftime("%b %d")
                last_poly_trucks = int(
                    trans_daily_pickups[
                        (trans_daily_pickups["transporter_name"] == "Polytra")
                        & (pd.to_datetime(trans_daily_pickups["pickup_date"]).dt.date == poly_last_date)
                    ]["trucks_picked"].sum()
                )
            if len(tram_dates):
                tram_last_date = pd.to_datetime(tram_dates).max().date()
                last_tram_date = tram_last_date.strftime("%b %d")
                last_tram_trucks = int(
                    trans_daily_pickups[
                        (trans_daily_pickups["transporter_name"] == "Reload (Trammo)")
                        & (pd.to_datetime(trans_daily_pickups["pickup_date"]).dt.date == tram_last_date)
                    ]["trucks_picked"].sum()
                )
        last_update_date = "—"
        if len(trans_daily_pickups):
            last_update_date = pd.to_datetime(trans_daily_pickups["pickup_date"]).max().strftime("%b %d")
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="mini-info mini-info-top">
                    <span>Last updated <strong>{last_update_date}</strong></span>
                </div>
                <div class="mini-info">
                    <span>Polytra <strong>{last_poly_date}</strong><br>{last_poly_trucks} trucks</span>
                    <span>Reload <strong>{last_tram_date}</strong><br>{last_tram_trucks} trucks</span>
                </div>
                <p class="metric-title">Days Left</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{days_left}</span>
                        <span class="metric-block-label">{finish_by_date.strftime('%b %d')}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    over_target_mt = max(0, total_mt_picked - allocation_mt)
    if over_target_mt > 0:
        over_target_trucks = over_target_mt / TRUCK_CAPACITY_MT
        st.success(f"Over target by {over_target_mt:,.0f} MT ({over_target_trucks:.1f} trucks)")

    st.markdown("<hr class='section-divider' />", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Loading Orders Tracker
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'><span class='title-icon'>✦</span>Loading Orders</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-content'>", unsafe_allow_html=True)
    paid_trucks_covered = orders_paid
    paid_mt_covered = paid_trucks_covered * TRUCK_CAPACITY_MT
    paid_remaining = max(0, orders_paid - total_trucks_picked)
    poly_paid_remaining = max(0, orders_paid_polytra - poly_trucks)
    tram_paid_remaining = max(0, orders_paid_trammo - tram_trucks)
    orders_paid_capped = min(orders_paid, LOADING_ORDERS_TARGET_TRUCKS)
    remaining_orders = max(0, LOADING_ORDERS_TARGET_TRUCKS - orders_paid_capped)

    lo_cols = st.columns(3)
    with lo_cols[0]:
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Paid Orders Remaining</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{paid_remaining}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with lo_cols[1]:
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Paid Coverage (MT)</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{paid_mt_covered:,.0f}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with lo_cols[2]:
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Orders To Pay</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{remaining_orders}</span>
                        <span class="metric-block-label">{LOADING_ORDERS_TARGET_TRUCKS} trucks</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if orders_paid >= LOADING_ORDERS_TARGET_TRUCKS:
        st.success(f"Loading orders complete ({LOADING_ORDERS_TARGET_TRUCKS}/{LOADING_ORDERS_TARGET_TRUCKS}).")
    st.markdown("<div class='card-row-gap'></div>", unsafe_allow_html=True)
    lo_alloc_cols = st.columns(2)
    with lo_alloc_cols[0]:
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Polytra Paid Remaining</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{poly_paid_remaining}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with lo_alloc_cols[1]:
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Reload (Trammo) Paid Remaining</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{tram_paid_remaining}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr class='section-divider' />", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Progress Analysis
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'><span class='title-icon'>✦</span>Progress Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-content'>", unsafe_allow_html=True)
    if len(trans_daily_pickups) > 0:
        daily_agg = trans_daily_pickups.groupby("pickup_date")["trucks_picked"].sum().reset_index()
        daily_agg["daily_mt"] = daily_agg["trucks_picked"] * TRUCK_CAPACITY_MT
        daily_agg["cumulative_mt"] = daily_agg["daily_mt"].cumsum()
        
        latest_cumulative = daily_agg['cumulative_mt'].iloc[-1]
        target_by_asof = (allocation_mt / finish_by_day) * (as_of_date - month_start).days
        variance = latest_cumulative - target_by_asof
        
        needed_per_day = remaining / max(days_left, 1)
        trucks_needed = needed_per_day / TRUCK_CAPACITY_MT
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_value = f"✅ Ahead by {variance:,.0f} MT" if variance >= 0 else f"⚠️ Behind by {abs(variance):,.0f} MT"
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Status</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="status-value">{status_value}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Needed/Day (MT)</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{needed_per_day:.1f}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Needed/Day (Trucks)</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{trucks_needed:.1f}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr class='section-divider' />", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Main Progress Chart - Plotly with Futuristic Style
    st.markdown("<div class='section-title'><span class='title-icon'>✦</span>Monthly Progress – Live Trajectory</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='center-caption'>Monthly Progress to Target - {mkey}</div>", unsafe_allow_html=True)
    
    if len(trans_daily_pickups) > 0:
        daily_agg = trans_daily_pickups.groupby("pickup_date")["trucks_picked"].sum().reset_index()
        daily_agg["daily_mt"] = daily_agg["trucks_picked"] * TRUCK_CAPACITY_MT
        daily_agg["cumulative_mt"] = daily_agg["daily_mt"].cumsum()
        daily_agg["pickup_date"] = pd.to_datetime(daily_agg["pickup_date"])
        
        month_end = date(selected_year, selected_month, min(finish_by_day, 28))
        
        # Create target trajectory
        target_dates = pd.date_range(month_start, month_end)
        target_values = np.linspace(0, allocation_mt, len(target_dates))
        
        fig = go.Figure()
        
        # Split actual progress into completed and projected
        completed_data = daily_agg[daily_agg['pickup_date'] <= pd.to_datetime(as_of_date)]
        if len(completed_data) > 0:
            # Completed portion - bright cyan
            fig.add_trace(go.Scatter(
                x=completed_data['pickup_date'], y=completed_data['cumulative_mt'],
                mode='lines+markers',
                name='Completed Progress',
                line=dict(color='#00d4ff', width=5),
                marker=dict(size=10, color='#00d4ff', line=dict(width=3, color='white')),
                hovertemplate='%{y:,.0f} MT'
            ))
        
        # Projected portion - dimmer cyan
        projected_data = daily_agg[daily_agg['pickup_date'] > pd.to_datetime(as_of_date)]
        if len(projected_data) > 0 and len(completed_data) > 0:
            fig.add_trace(go.Scatter(
                x=projected_data['pickup_date'], y=projected_data['cumulative_mt'],
                mode='lines+markers',
                name='Projected Progress',
                line=dict(color='rgba(0, 212, 255, 0.4)', width=5, dash='dash'),
                marker=dict(size=8, color='rgba(0, 212, 255, 0.4)', line=dict(width=2, color='rgba(255,255,255,0.3)')),
                hovertemplate='%{y:,.0f} MT'
            ))
        
        # Target line - green dotted
        fig.add_trace(go.Scatter(
            x=target_dates, y=target_values,
            mode='lines',
            name='Target Trajectory',
            line=dict(color='#00ff9d', width=4, dash='dot'),
            hovertemplate='%{y:,.0f} MT'
        ))
        
        # Today marker - red dashed
        marker_label = "TODAY" if mkey == current_mkey else "AS OF"
        fig.add_shape(
            type="line",
            x0=pd.to_datetime(as_of_date), x1=pd.to_datetime(as_of_date),
            y0=0, y1=1,
            yref="paper",
            line=dict(color='#ff2e63', width=4, dash='dash'),
        )
        fig.add_annotation(
            x=pd.to_datetime(as_of_date),
            y=1,
            yref="paper",
            text=marker_label,
            showarrow=False,
            font=dict(size=14, color='#ff2e63'),
            yshift=10
        )
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            margin=dict(l=30, r=20, b=100, t=40),
            height=440,
            hovermode='x unified',
            dragmode=False,
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.08)',
                title='Date',
                automargin=True
            ),
            yaxis=dict(
                title=dict(text='Cumulative MT', font=dict(size=13)),
                gridcolor='rgba(255,255,255,0.08)',
                automargin=True
            ),
            title_text="",
            legend_title_text="",
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.25, yanchor="top", font=dict(size=11))
        )
        
        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displayModeBar": False,
                "responsive": True,
                "scrollZoom": False,
                "doubleClick": False,
            },
        )
    else:
        st.info("No pickup data logged yet. Start logging daily pickups to see the progress chart.")

    st.divider()

    # Transporter Performance - Gauge Charts
    st.markdown("<div class='section-title'><span class='title-icon'>✦</span>Transporter Performance</div>", unsafe_allow_html=True)
    
    col_poly, col_tram = st.columns(2)
    
    with col_poly:
        poly_alloc = trans_alloc.get("Polytra", allocation_mt / 2)
        poly_pct = (poly_mt / poly_alloc * 100) if poly_alloc > 0 else 0
        poly_pct = min(poly_pct, 100)  # Cap at 100% for gauge
        
        # Calculate trucks per day needed to complete by finish-by
        poly_remaining = poly_alloc - poly_mt
        poly_trucks_per_day = poly_remaining / (TRUCK_CAPACITY_MT * days_until_finish) if days_until_finish > 0 else 0
        
        fig_poly = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=poly_pct,
            title=dict(text="Polytra", font=dict(size=20, color='#9fb1ca')),
            delta=dict(reference=100, suffix="% to target"),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor='#2f80ff'),
                bar=dict(color='#2f80ff', thickness=0.75),
                bgcolor='rgba(255,255,255,0.1)',
                borderwidth=2,
                bordercolor='#2f80ff',
                steps=[
                    dict(range=[0, 50], color='rgba(255,46,99,0.2)'),
                    dict(range=[50, 80], color='rgba(0,255,157,0.2)'),
                    dict(range=[80, 100], color='rgba(0,212,255,0.2)')
                ],
                threshold=dict(
                    line=dict(color='#ff2e63', width=4),
                    thickness=0.75,
                    value=100
                )
            ),
            domain=dict(x=[0, 1], y=[0, 1]),
            number=dict(suffix='%', font=dict(size=24, color='#2f80ff'))
        ))
        fig_poly.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            height=320,
            margin=dict(l=20, r=28, t=70, b=14),
            font=dict(color='#e0f7ff')
        )
        st.plotly_chart(fig_poly, use_container_width=True)
        
        st.markdown(f"""
        <div class="metric-stack">
            <div class="metric-row">
                <span class="metric-label">Target (MT)</span>
                <span class="metric-value">{poly_alloc:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Completed (MT)</span>
                <span class="metric-value">{poly_mt:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Completed (Trucks)</span>
                <span class="metric-value">{poly_trucks:,}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Remaining (MT)</span>
                <span class="metric-value">{poly_alloc - poly_mt:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Remaining (Trucks)</span>
                <span class="metric-value">{(poly_alloc - poly_mt) / TRUCK_CAPACITY_MT:,.1f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Trucks Needed to Target (/day)</span>
                <span class="metric-value">{poly_trucks_per_day:.1f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_tram:
        tram_alloc = trans_alloc.get("Reload (Trammo)", allocation_mt / 2)
        tram_pct = (tram_mt / tram_alloc * 100) if tram_alloc > 0 else 0
        tram_pct = min(tram_pct, 100)  # Cap at 100% for gauge
        
        # Calculate trucks per day needed to complete by finish-by
        tram_remaining = tram_alloc - tram_mt
        tram_trucks_per_day = tram_remaining / (TRUCK_CAPACITY_MT * days_until_finish) if days_until_finish > 0 else 0
        
        fig_tram = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tram_pct,
            title=dict(text="Reload (Trammo)", font=dict(size=20, color='#9fb1ca')),
            delta=dict(reference=100, suffix="% to target"),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor='#ff9f1a'),
                bar=dict(color='#ff9f1a', thickness=0.75),
                bgcolor='rgba(255,255,255,0.1)',
                borderwidth=2,
                bordercolor='#ff9f1a',
                steps=[
                    dict(range=[0, 50], color='rgba(255,46,99,0.2)'),
                    dict(range=[50, 80], color='rgba(0,255,157,0.2)'),
                    dict(range=[80, 100], color='rgba(0,212,255,0.2)')
                ],
                threshold=dict(
                    line=dict(color='#ff2e63', width=4),
                    thickness=0.75,
                    value=100
                )
            ),
            domain=dict(x=[0, 1], y=[0, 1]),
            number=dict(suffix='%', font=dict(size=24, color='#ff9f1a'))
        ))
        fig_tram.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            height=320,
            margin=dict(l=20, r=28, t=70, b=14),
            font=dict(color='#e0f7ff')
        )
        st.plotly_chart(fig_tram, use_container_width=True)
        
        st.markdown(f"""
        <div class="metric-stack">
            <div class="metric-row">
                <span class="metric-label">Target (MT)</span>
                <span class="metric-value">{tram_alloc:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Completed (MT)</span>
                <span class="metric-value">{tram_mt:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Completed (Trucks)</span>
                <span class="metric-value">{tram_trucks:,}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Remaining (MT)</span>
                <span class="metric-value">{tram_alloc - tram_mt:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Remaining (Trucks)</span>
                <span class="metric-value">{(tram_alloc - tram_mt) / TRUCK_CAPACITY_MT:,.1f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Trucks Needed to Target (/day)</span>
                <span class="metric-value">{tram_trucks_per_day:.1f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Real-time Simulation
    st.markdown("<div class='section-title'><span class='title-icon'>✦</span>Real-time Simulator</div>", unsafe_allow_html=True)
    with st.expander("Run simulation", expanded=False):
        sim_days = st.number_input("Days", min_value=1, step=1, value=5)
        sim_trucks_per_day = st.number_input("Trucks per day", min_value=0.0, step=0.5, value=1.0)
        daily_mt = sim_trucks_per_day * TRUCK_CAPACITY_MT
        sim_mt = sim_days * daily_mt
        projected_total = total_mt_picked + sim_mt
        projected_pct = (projected_total / allocation_mt * 100) if allocation_mt > 0 else 0

        predicted_end_date = as_of_date + timedelta(days=int(sim_days))
        days_to_target = None
        if daily_mt > 0:
            days_to_target = math.ceil(max(0, remaining) / daily_mt)
        predicted_target_date = as_of_date + timedelta(days=days_to_target) if days_to_target else None
        finish_delta_days = (predicted_end_date - finish_by_date).days

        sim_cols = st.columns(3)
        with sim_cols[0]:
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Simulated MT</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{sim_mt:,.0f}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sim_cols[1]:
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Projected Total MT</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{projected_total:,.0f}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sim_cols[2]:
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Projected % of Target</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{projected_pct:.1f}%</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div class='card-row-gap'></div>", unsafe_allow_html=True)
        sim_cols_2 = st.columns(3)
        with sim_cols_2[0]:
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Projected End Date</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{predicted_end_date.strftime('%b %d, %Y')}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sim_cols_2[1]:
            target_date_text = predicted_target_date.strftime('%b %d, %Y') if predicted_target_date else "N/A"
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Target Hit Date</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{target_date_text}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sim_cols_2[2]:
            finish_status = "On time"
            if finish_delta_days < 0:
                finish_status = f"Ahead by {abs(finish_delta_days)}d"
            elif finish_delta_days > 0:
                finish_status = f"Behind by {finish_delta_days}d"
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Finish-by Delta</p>
                    <div class="metric-blocks single">
                        <div class="metric-block">
                            <span class="metric-block-value">{finish_status}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div class='card-row-gap'></div>", unsafe_allow_html=True)
        extra_mt = max(0, projected_total - allocation_mt)
        short_mt = max(0, allocation_mt - projected_total)
        variance_label = "Extra Over Target" if extra_mt > 0 else "Short to Target"
        variance_mt = extra_mt if extra_mt > 0 else short_mt
        variance_trucks = variance_mt / TRUCK_CAPACITY_MT if variance_mt > 0 else 0
        st.markdown(
            f"""
            <div class="sim-footer-card">
                <div class="metric-card compact">
                    <p class="metric-title">{variance_label}</p>
                    <div class="metric-blocks">
                        <div class="metric-block">
                            <span class="metric-block-label">MT</span>
                            <span class="metric-block-value">{variance_mt:,.0f}</span>
                        </div>
                        <div class="metric-block">
                            <span class="metric-block-label">Trucks</span>
                            <span class="metric-block-value">{variance_trucks:.1f}</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif page == "Daily Planner":
    st.title("Daily Truck Pickups")
    st.caption("Track daily truck pickups per transporter from Sasol")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='section-title'><span class='title-icon'>✦</span>Polytra Daily Pickups</div>", unsafe_allow_html=True)
        with st.expander("Log Polytra Pickups", expanded=True):
            pickup_date_poly = st.date_input("Pickup date", value=today, key="poly_date")
            trucks_poly = st.number_input("Trucks picked", min_value=0, step=1, value=1, key="poly_trucks")
            st.metric(f"Total MT ({TRUCK_CAPACITY_MT} MT/truck)", f"{trucks_poly * TRUCK_CAPACITY_MT:,.0f}")
            notes_poly = st.text_area("Notes", key="poly_notes")
            
            if st.button("Save Polytra Pickups"):
                exec_sql(
                    "INSERT OR REPLACE INTO transporter_daily_pickups(pickup_date, transporter_name, trucks_picked, notes, created_at) VALUES(?,?,?,?,?)",
                    (pickup_date_poly.isoformat(), "Polytra", trucks_poly, notes_poly, datetime.now().isoformat(timespec="seconds"))
                )
                st.success("✅ Polytra pickups logged!")
        
        poly_pickups = read_df("SELECT id, pickup_date, trucks_picked, notes FROM transporter_daily_pickups WHERE transporter_name='Polytra' ORDER BY pickup_date DESC LIMIT 7")
        if len(poly_pickups):
            st.metric("Trucks (7 days)", f"{int(poly_pickups['trucks_picked'].sum())}")
            st.dataframe(poly_pickups.drop(columns=["id"]), use_container_width=True, hide_index=True)

            with st.expander("Edit/Delete Polytra Entry", expanded=False):
                poly_options = {
                    f"{row['pickup_date']} • {int(row['trucks_picked'])} trucks": int(row["id"])
                    for _, row in poly_pickups.iterrows()
                }
                selected_poly_label = st.selectbox(
                    "Select entry",
                    list(poly_options.keys()),
                    key="poly_edit_select",
                )
                selected_poly_id = poly_options[selected_poly_label]
                poly_row = poly_pickups[poly_pickups["id"] == selected_poly_id].iloc[0]

                edit_poly_date = st.date_input(
                    "Pickup date",
                    value=date.fromisoformat(poly_row["pickup_date"]),
                    key="poly_edit_date",
                )
                edit_poly_trucks = st.number_input(
                    "Trucks picked",
                    min_value=0,
                    step=1,
                    value=int(poly_row["trucks_picked"]),
                    key="poly_edit_trucks",
                )
                edit_poly_notes = st.text_area(
                    "Notes",
                    value=poly_row["notes"] if poly_row["notes"] else "",
                    key="poly_edit_notes",
                )

                col_update, col_delete = st.columns(2)
                with col_update:
                    if st.button("Update Entry", key="poly_update_btn"):
                        try:
                            exec_sql(
                                "UPDATE transporter_daily_pickups SET pickup_date=?, trucks_picked=?, notes=? WHERE id=?",
                                (edit_poly_date.isoformat(), edit_poly_trucks, edit_poly_notes, selected_poly_id),
                            )
                            st.success("✅ Polytra entry updated.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("⚠️ Update failed. Duplicate pickup date for Polytra.")
                with col_delete:
                    if st.button("Delete Entry", key="poly_delete_btn"):
                        exec_sql("DELETE FROM transporter_daily_pickups WHERE id=?", (selected_poly_id,))
                        st.success("🗑️ Polytra entry deleted.")
                        st.rerun()
    
    with col2:
        st.markdown("<div class='section-title'><span class='title-icon'>✦</span>Trammo Daily Pickups</div>", unsafe_allow_html=True)
        with st.expander("Log Trammo Pickups", expanded=True):
            pickup_date_tram = st.date_input("Pickup date", value=today, key="tram_date")
            trucks_tram = st.number_input("Trucks picked", min_value=0, step=1, value=1, key="tram_trucks")
            st.metric(f"Total MT ({TRUCK_CAPACITY_MT} MT/truck)", f"{trucks_tram * TRUCK_CAPACITY_MT:,.0f}")
            notes_tram = st.text_area("Notes", key="tram_notes")
            
            if st.button("Save Trammo Pickups"):
                exec_sql(
                    "INSERT OR REPLACE INTO transporter_daily_pickups(pickup_date, transporter_name, trucks_picked, notes, created_at) VALUES(?,?,?,?,?)",
                    (pickup_date_tram.isoformat(), "Reload (Trammo)", trucks_tram, notes_tram, datetime.now().isoformat(timespec="seconds"))
                )
                st.success("✅ Trammo pickups logged!")
        
        tram_pickups = read_df("SELECT id, pickup_date, trucks_picked, notes FROM transporter_daily_pickups WHERE transporter_name='Reload (Trammo)' ORDER BY pickup_date DESC LIMIT 7")
        if len(tram_pickups):
            st.metric("Trucks (7 days)", f"{int(tram_pickups['trucks_picked'].sum())}")
            st.dataframe(tram_pickups.drop(columns=["id"]), use_container_width=True, hide_index=True)

            with st.expander("Edit/Delete Trammo Entry", expanded=False):
                tram_options = {
                    f"{row['pickup_date']} • {int(row['trucks_picked'])} trucks": int(row["id"])
                    for _, row in tram_pickups.iterrows()
                }
                selected_tram_label = st.selectbox(
                    "Select entry",
                    list(tram_options.keys()),
                    key="tram_edit_select",
                )
                selected_tram_id = tram_options[selected_tram_label]
                tram_row = tram_pickups[tram_pickups["id"] == selected_tram_id].iloc[0]

                edit_tram_date = st.date_input(
                    "Pickup date",
                    value=date.fromisoformat(tram_row["pickup_date"]),
                    key="tram_edit_date",
                )
                edit_tram_trucks = st.number_input(
                    "Trucks picked",
                    min_value=0,
                    step=1,
                    value=int(tram_row["trucks_picked"]),
                    key="tram_edit_trucks",
                )
                edit_tram_notes = st.text_area(
                    "Notes",
                    value=tram_row["notes"] if tram_row["notes"] else "",
                    key="tram_edit_notes",
                )

                col_update, col_delete = st.columns(2)
                with col_update:
                    if st.button("Update Entry", key="tram_update_btn"):
                        try:
                            exec_sql(
                                "UPDATE transporter_daily_pickups SET pickup_date=?, trucks_picked=?, notes=? WHERE id=?",
                                (edit_tram_date.isoformat(), edit_tram_trucks, edit_tram_notes, selected_tram_id),
                            )
                            st.success("✅ Trammo entry updated.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("⚠️ Update failed. Duplicate pickup date for Trammo.")
                with col_delete:
                    if st.button("Delete Entry", key="tram_delete_btn"):
                        exec_sql("DELETE FROM transporter_daily_pickups WHERE id=?", (selected_tram_id,))
                        st.success("🗑️ Trammo entry deleted.")
                        st.rerun()

elif page == "Monthly Data":
    st.title("Monthly Data")
    month_opts_df = read_df(
        """
        SELECT DISTINCT month_key FROM monthly_plan
        UNION
        SELECT DISTINCT substr(pickup_date, 1, 7) AS month_key
        FROM transporter_daily_pickups
        ORDER BY month_key DESC
        """
    )
    month_options = month_opts_df["month_key"].tolist() if len(month_opts_df) else [mkey]
    month_options = month_options or [mkey]

    md_cols = st.columns(2)
    with md_cols[0]:
        md_mkey = st.selectbox("Month", month_options, index=0, key="md_month")
    with md_cols[1]:
        transporter_options = ["All", "Polytra", "Reload (Trammo)"]
        md_transporter = st.selectbox("Transporter", transporter_options, index=0, key="md_transporter")

    md_plan_df = read_df("SELECT allocation_mt FROM monthly_plan WHERE month_key=?", (md_mkey,))
    md_allocation_mt = float(md_plan_df.iloc[0]["allocation_mt"]) if len(md_plan_df) else DEFAULT_MONTHLY_ALLOCATION_MT

    md_year, md_month = [int(part) for part in md_mkey.split("-")]
    md_month_label = date(md_year, md_month, 1).strftime("%B %Y")
    st.caption(f"Summary — {md_month_label} • Target: {md_allocation_mt:,.0f} MT")

    md_pickups = read_df(
        "SELECT pickup_date, transporter_name, trucks_picked FROM transporter_daily_pickups WHERE pickup_date LIKE ? ORDER BY pickup_date",
        (f"{md_mkey}%",),
    )
    if md_transporter != "All":
        md_pickups = md_pickups[md_pickups["transporter_name"] == md_transporter].copy()

    md_total_trucks = int(md_pickups["trucks_picked"].sum()) if len(md_pickups) else 0
    md_total_mt = float(md_total_trucks * TRUCK_CAPACITY_MT)

    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Total Picked (MT)</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{md_total_mt:,.0f}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[1]:
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Total Trucks</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{md_total_trucks:,}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[2]:
        over_target_mt = max(0, md_total_mt - md_allocation_mt)
        st.markdown(
            f"""
            <div class="metric-card compact">
                <p class="metric-title">Over Target (MT)</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{over_target_mt:,.0f}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("Daily Pickups")
    if len(md_pickups):
        daily_view = md_pickups.copy()
        daily_view["mt"] = daily_view["trucks_picked"] * TRUCK_CAPACITY_MT
        st.dataframe(daily_view, use_container_width=True, hide_index=True)
    else:
        st.info("No pickup data logged for this selection.")

elif page == "Settings":
    st.title("Settings")
    
    st.subheader("Production Targets")
    col1, col2 = st.columns(2)
    
    with col1:
        new_alloc = st.number_input("Monthly target (MT)", min_value=0.0, step=50.0, value=float(allocation_mt))
    with col2:
        new_finish_day = st.number_input("Finish-by day", min_value=1, max_value=31, step=1, value=int(finish_by_day))
    
    if st.button("Save Targets"):
        exec_sql("UPDATE monthly_plan SET allocation_mt=?, finish_by_day=? WHERE month_key=?", (new_alloc, new_finish_day, mkey))
        st.success("✅ Targets saved!")
    
    st.divider()
    st.subheader("Transporter Allocations")
    
    col_poly, col_tram = st.columns(2)
    poly_alloc = trans_alloc.get("Polytra", allocation_mt / 2)
    tram_alloc = trans_alloc.get("Reload (Trammo)", allocation_mt / 2)
    
    with col_poly:
        new_poly = st.number_input("Polytra allocation (MT)", min_value=0.0, step=50.0, value=float(poly_alloc), key="poly_alloc")
    with col_tram:
        new_tram = st.number_input("Trammo allocation (MT)", min_value=0.0, step=50.0, value=float(tram_alloc), key="tram_alloc")
    
    if st.button("Save Allocations"):
        exec_sql("UPDATE transporter_allocation SET allocation_mt=? WHERE month_key=? AND transporter_name=?", (new_poly, mkey, "Polytra"))
        exec_sql("UPDATE transporter_allocation SET allocation_mt=? WHERE month_key=? AND transporter_name=?", (new_tram, mkey, "Reload (Trammo)"))
        st.success("✅ Allocations saved!")

    st.divider()
    st.subheader("Loading Orders")
    lo_col1, lo_col2, lo_col3 = st.columns(3)
    with lo_col1:
        new_orders_paid = st.number_input("Orders paid", min_value=0, step=1, value=int(orders_paid))
    with lo_col2:
        new_orders_paid_poly = st.number_input(
            "Polytra paid orders",
            min_value=0,
            step=1,
            value=int(orders_paid_polytra),
        )
    with lo_col3:
        new_orders_paid_tram = st.number_input(
            "Reload (Trammo) paid orders",
            min_value=0,
            step=1,
            value=int(orders_paid_trammo),
        )

    if st.button("Save Loading Orders"):
        total_allocated = new_orders_paid_poly + new_orders_paid_tram
        if total_allocated != new_orders_paid:
            st.error(
                f"Allocate all paid orders to a transporter. Assigned {total_allocated} of {new_orders_paid}."
            )
        else:
            exec_sql(
                """
                UPDATE loading_orders
                SET
                    orders_paid=?,
                    orders_open=?,
                    orders_paid_polytra=?,
                    orders_paid_trammo=?,
                    orders_paid_polytra_base=?,
                    orders_paid_trammo_base=?
                WHERE month_key=?
                """,
                (
                    new_orders_paid,
                    0,
                    new_orders_paid_poly,
                    new_orders_paid_tram,
                    poly_trucks,
                    tram_trucks,
                    mkey,
                ),
            )
            st.success("✅ Loading orders saved!")
            st.rerun()

    st.divider()
    st.subheader("⚠️ Danger Zone")
    
    if st.button("🗑️ Clear All Data", key="clear_data"):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            st.success("✅ Database cleared! Refresh the page to start fresh.")
