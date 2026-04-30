import streamlit as st
import pandas as pd
import plotly.express as px
from database import Database
from ai_analyst import AIAnalyst
from keepa_client import KeepaClient
import threading
import time
from datetime import datetime

st.set_page_config(page_title="Amazon Hub", layout="wide")

if 'is_run' not in st.session_state:
    st.session_state.is_run = False

db = Database()
ai = AIAnalyst()
cl = KeepaClient()

st.title("🏢 Amazon Intelligence Hub")

def start_update():
    asins = db.get_all_tracked_asins()
    if not asins: return "No ASINs."
    c = 0
    for a in asins:
        d = cl.get_product_data(a)
        if d:
            p = cl.extract_current_price(d, "new")
            if p: db.save_price(a, p)
            det = cl.extract_full_details(d)
            if det: db.save_product_details(a, det)
            c += 1
    return f"Updated {c}/{len(asins)} products."

def loop_func():
    while True:
        start_update()
        time.sleep(3600)

if not st.session_state.is_run:
    t = threading.Thread(target=loop_func, daemon=True)
    t.start()
    st.session_state.is_run = True

st.sidebar.header("📁 Projects")
with st.sidebar.expander("➕ New Project"):
    n_p = st.text_input("Name").strip()
    if st.button("Create"):
        if n_p and db.create_project(n_p):
            st.success("Done!")
            st.rerun()

projs = db.get_projects()
if not projs: st.stop()
p_map = {name: pid for pid, name in projs}
s_name = st.sidebar.selectbox("Project", list(p_map.keys()))
s_id = p_map[s_name]

st.sidebar.divider()
n_a = st.sidebar.text_input("Add ASIN").strip().upper()
if st.sidebar.button("Add"):
    if n_a and db.add_asin_to_project(s_id, n_a):
        st.sidebar.success("Done!")
        st.rerun()

st.header(f"Project: {s_name}")
if st.button("🔄 Sync Now"):
    with st.spinner("Syncing..."):
        st.toast(start_update())
        st.rerun()

as_list = db.get_asins_for_project(s_id)
if not as_list:
    st.info("Empty project.")
else:
    st.subheader("📊 Market Overview")
    ov_d = []
    for a in as_list:
        p = db.get_last_price(a)
        dt = db.get_product_details(a) or {}
        with db.get_connection() as conn:
            res = conn.execute(f"SELECT timestamp FROM price_history WHERE asin='{a}' ORDER BY timestamp DESC LIMIT 1").fetchone()
            ts = res[0] if res else "Never"
        ov_d.append({"ASIN": a, "Price": p if p else "N/A", "BSR": dt.get('sales_rank', 'N/A'), 
                    "Rating": dt.get('reviews_rating', 'N/A'), "Reviews": dt.get('reviews_count', 'N/A'), "Updated": ts})
    st.dataframe(pd.DataFrame(ov_d), use_container_width=True)

    st.divider()
    st.subheader("📈 Deep Dive")
    s_asin = st.selectbox("Product", as_list)
    if s_asin:
        dt = db.get_product_details(s_asin)
        if dt:
            with st.expander("📋 Specs", expanded=True):
                st.write(f"**Title:** {dt.get('title')}")
                st.write(f"**BSR:** {dt.get('sales_rank', 'N/A')}")
                st.write(f"**Bullets:** {dt.get('features')}")

        with db.get_connection() as conn:
            q = f"SELECT timestamp, price FROM price_history WHERE asin = '{s_asin}' ORDER BY timestamp ASC"
            df_data = pd.read_sql_query(q, conn)
        if not df_data.empty:
            df_data['timestamp'] = pd.to_datetime(df_data['timestamp'])
            fig = px.line(df_data, x='timestamp', y='price', title=f"Price: {s_asin}", markers=True)
            fig.update_traces(line_color='#ff9900', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Price", f"${df_data['price'].iloc[-1]}")
            col2.metric("Min", f"${df_data['price'].min()}")
            col3.metric("Max", f"${df_data['price'].max()}")
            if st.button(f"🤖 AI Report"):
                with st.spinner("AI thinking..."):
                    ans = ai.analyze_trends(s_asin, df_data) 
                    st.markdown("### 💡 AI Insights:")
                    st.markdown(ans)
        else:
            st.warning("No data. Sync now.")
