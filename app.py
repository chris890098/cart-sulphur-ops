import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os

# ─── Theme & Layout ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CART SULPHUR OPS • 2026",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0f2d 0%, #000814 100%);
        color: #e0f7ff;
    }
    .stMetric,
    [data-testid="stMetric"] {
        background: rgba(10, 25, 60, 0.45);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 200, 0.18);
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
        font-size: 12px !important;
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
    }
    .stMetric [data-testid="stMetricDelta"],
    [data-testid="stMetricDelta"] {
        font-size: 13px;
        font-weight: 600;
        text-align: center;
    }
    .metric-card {
        background: rgba(10, 25, 60, 0.45);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 200, 0.18);
        border-radius: 16px;
        padding: 1rem;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .metric-title {
        font-size: 12px;
        color: #e0f7ff;
        margin: 0;
        text-align: center;
        margin-bottom: 0.6rem;
    }
    .status-value {
        font-size: 18px;
        font-weight: 700;
        margin: 0.6rem 0 0 0;
        text-align: center;
    }
    .status-delta {
        font-size: 12px;
        font-weight: 600;
        color: #bfe8f4;
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
        font-size: 12px;
        color: #bfe8f4;
    }
    .metric-block-value {
        font-size: 20px;
        font-weight: 700;
        color: #e0f7ff;
        line-height: 1.1;
        text-align: center;
        width: 100%;
    }
    .metric-stack {
        background: rgba(10, 25, 60, 0.45);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 200, 0.18);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-top: 0.4rem;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 0.25rem 0;
        border-bottom: 1px solid rgba(0, 255, 234, 0.12);
    }
    .metric-row:last-child {
        border-bottom: none;
    }
    .metric-label {
        font-size: 13px;
        color: #bfe8f4;
    }
    .metric-value {
        font-size: 18px;
        font-weight: 700;
        color: #e0f7ff;
    }
    h1, h2, h3 { color: #00ffea !important; }
    hr { border-color: rgba(0, 255, 234, 0.25) !important; }
    .center-caption {
        text-align: center;
        color: #8fd7e8;
        margin: 0 0 0.5rem 0;
    }
    @media (max-width: 768px) {
        .modebar { display: none !important; }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─── Database Setup ────────────────────────────────────────────────────────
DB_PATH = "cart_sulphur_ops.db"
DEFAULT_MONTHLY_ALLOCATION_MT = 1250
DEFAULT_FINISH_BY_DAY = 25
TRUCK_CAPACITY_MT = 34

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
mkey = month_key_for(today)
ensure_month_plan(mkey)

# ─── Load Data ─────────────────────────────────────────────────────────────
st.sidebar.title("🚀 CART OPS")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()
is_admin = False
if ADMIN_TOKEN:
    admin_param = st.query_params.get("admin", "")
    if isinstance(admin_param, list):
        admin_param = admin_param[0] if admin_param else ""
    if admin_param and admin_param == ADMIN_TOKEN:
        is_admin = True
else:
    is_admin = True

if is_admin:
    page = st.sidebar.radio("Navigate", ["Dashboard", "Daily Planner", "Settings"])
else:
    page = "Dashboard"
    st.sidebar.markdown("🔒 Admin pages hidden")
    st.sidebar.caption("Admin access via URL only")

plan_df = read_df("SELECT allocation_mt, finish_by_day FROM monthly_plan WHERE month_key=?", (mkey,))
allocation_mt = float(plan_df.iloc[0]["allocation_mt"]) if len(plan_df) else DEFAULT_MONTHLY_ALLOCATION_MT
finish_by_day = int(plan_df.iloc[0]["finish_by_day"]) if len(plan_df) else DEFAULT_FINISH_BY_DAY

trans_alloc_df = read_df("SELECT transporter_name, allocation_mt FROM transporter_allocation WHERE month_key=?", (mkey,))
trans_alloc = {row["transporter_name"]: float(row["allocation_mt"]) for _, row in trans_alloc_df.iterrows()}

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
finish_by_date = date(today.year, today.month, min(finish_by_day, 28))
days_left = max(0, (finish_by_date - today).days)

# Calculate days until 24th for transporter performance
days_until_24 = max(1, (date(today.year, today.month, 24) - today).days)

if page == "Dashboard":
    st.title("🌀 CART SULPHUR OPS • CONTROL CENTER")
    st.caption(f"Month: {today.strftime('%Y-%m')} • Supplier: Sasol • Target: {allocation_mt:,.0f} MT")

    # KPI Metrics
    cols = st.columns(4)
    with cols[0]:
        st.markdown(
            f"""
            <div class="metric-card">
                <p class="metric-title">Target (MT)</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{allocation_mt:,.0f}</span>
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
        st.markdown(
            f"""
            <div class="metric-card">
                <p class="metric-title">Days Left</p>
                <div class="metric-blocks single">
                    <div class="metric-block">
                        <span class="metric-block-value">{days_left}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Progress Analysis
    st.subheader("📊 Progress Analysis")
    if len(trans_daily_pickups) > 0:
        daily_agg = trans_daily_pickups.groupby("pickup_date")["trucks_picked"].sum().reset_index()
        daily_agg["daily_mt"] = daily_agg["trucks_picked"] * TRUCK_CAPACITY_MT
        daily_agg["cumulative_mt"] = daily_agg["daily_mt"].cumsum()
        
        month_start = date(today.year, today.month, 1)
        latest_cumulative = daily_agg['cumulative_mt'].iloc[-1]
        target_by_today = (allocation_mt / finish_by_day) * (today - month_start).days
        variance = latest_cumulative - target_by_today
        
        needed_per_day = remaining / max(days_left, 1)
        trucks_needed = needed_per_day / TRUCK_CAPACITY_MT
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_value = f"✅ Ahead by {variance:,.0f} MT" if variance >= 0 else f"⚠️ Behind by {abs(variance):,.0f} MT"
            st.markdown(
                f"""
                <div class="metric-card compact">
                    <p class="metric-title">Status</p>
                    <p class="status-value">{status_value}</p>
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

    st.divider()

    # Main Progress Chart - Plotly with Futuristic Style
    st.subheader("📈 Monthly Progress – Live Trajectory")
    st.markdown(f"<div class='center-caption'>Monthly Progress to Target - {mkey}</div>", unsafe_allow_html=True)
    
    if len(trans_daily_pickups) > 0:
        daily_agg = trans_daily_pickups.groupby("pickup_date")["trucks_picked"].sum().reset_index()
        daily_agg["daily_mt"] = daily_agg["trucks_picked"] * TRUCK_CAPACITY_MT
        daily_agg["cumulative_mt"] = daily_agg["daily_mt"].cumsum()
        daily_agg["pickup_date"] = pd.to_datetime(daily_agg["pickup_date"])
        
        month_start = date(today.year, today.month, 1)
        month_end = date(today.year, today.month, min(finish_by_day, 28))
        
        # Create target trajectory
        target_dates = pd.date_range(month_start, month_end)
        target_values = np.linspace(0, allocation_mt, len(target_dates))
        
        fig = go.Figure()
        
        # Split actual progress into completed and projected
        completed_data = daily_agg[daily_agg['pickup_date'] <= pd.to_datetime(today)]
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
        projected_data = daily_agg[daily_agg['pickup_date'] > pd.to_datetime(today)]
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
        fig.add_shape(
            type="line",
            x0=pd.to_datetime(today), x1=pd.to_datetime(today),
            y0=0, y1=1,
            yref="paper",
            line=dict(color='#ff2e63', width=4, dash='dash'),
        )
        fig.add_annotation(
            x=pd.to_datetime(today),
            y=1,
            yref="paper",
            text="TODAY",
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
    st.subheader("🚛 Transporter Performance")
    
    col_poly, col_tram = st.columns(2)
    
    with col_poly:
        poly_alloc = trans_alloc.get("Polytra", allocation_mt / 2)
        poly_pct = (poly_mt / poly_alloc * 100) if poly_alloc > 0 else 0
        poly_pct = min(poly_pct, 100)  # Cap at 100% for gauge
        
        # Calculate trucks per day needed to complete by 24th
        poly_remaining = poly_alloc - poly_mt
        poly_trucks_per_day = poly_remaining / (TRUCK_CAPACITY_MT * days_until_24) if days_until_24 > 0 else 0
        
        fig_poly = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=poly_pct,
            title=dict(text="Polytra", font=dict(size=20, color='#ffffff')),
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
            height=350,
            margin=dict(l=20, r=20, t=60, b=20),
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
        
        # Calculate trucks per day needed to complete by 24th
        tram_remaining = tram_alloc - tram_mt
        tram_trucks_per_day = tram_remaining / (TRUCK_CAPACITY_MT * days_until_24) if days_until_24 > 0 else 0
        
        fig_tram = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tram_pct,
            title=dict(text="Reload (Trammo)", font=dict(size=20, color='#ffffff')),
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
            height=350,
            margin=dict(l=20, r=20, t=60, b=20),
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

elif page == "Daily Planner":
    st.title("Daily Truck Pickups")
    st.caption("Track daily truck pickups per transporter from Sasol")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚛 Polytra Daily Pickups")
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
        
        poly_pickups = read_df("SELECT pickup_date, trucks_picked FROM transporter_daily_pickups WHERE transporter_name='Polytra' ORDER BY pickup_date DESC LIMIT 7")
        if len(poly_pickups):
            st.metric("Trucks (7 days)", f"{int(poly_pickups['trucks_picked'].sum())}")
            st.dataframe(poly_pickups, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("🚛 Trammo Daily Pickups")
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
        
        tram_pickups = read_df("SELECT pickup_date, trucks_picked FROM transporter_daily_pickups WHERE transporter_name='Reload (Trammo)' ORDER BY pickup_date DESC LIMIT 7")
        if len(tram_pickups):
            st.metric("Trucks (7 days)", f"{int(tram_pickups['trucks_picked'].sum())}")
            st.dataframe(tram_pickups, use_container_width=True, hide_index=True)

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
    st.subheader("⚠️ Danger Zone")
    
    if st.button("🗑️ Clear All Data", key="clear_data"):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            st.success("✅ Database cleared! Refresh the page to start fresh.")
