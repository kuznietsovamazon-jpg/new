with open('app.py', 'w', encoding='utf-8') as f:
    f.write(r'''import streamlit as st
import pandas as pd
import plotly.express as px
from database import Database
from ai_analyst import AIAnalyst
from keepa_client import KeepaClient
import threading
import time
from datetime import datetime

st.set_page_config(page_title="Amazon Intelligence Hub", layout="wide")

if 'monitor_running' not in st.session_state:
    st.session_state.monitor_running = False

db = Database()
ai = AIAnalyst()
client = KeepaClient()

st.title("🏢 Amazon Competitor Intelligence Hub")
st.markdown("Мониторинг цен, продаж (BSR) и контента конкурентов")

def run_monitor_cycle():
    asins = db.get_all_tracked_asins()
    if not asins:
        return "No ASINs found."
    updates_count = 0
    for asin in asins:
        data = client.get_product_data(asin)
        if data:
            price = client.extract_current_price(data, "new")
            if price:
                db.save_price(asin, price)
            details = client.extract_full_details(data)
            if details:
                db.save_product_details(asin, details)
            updates_count += 1
    return f"Updated {updates_count}/{len(asins)} products."

def monitor_thread_loop():
    while True:
        run_monitor_cycle()
        time.sleep(3600)

if not st.session_state.monitor_running:
    thread = threading.Thread(target=monitor_thread_loop, daemon=True)
    thread.start()
    st.session_state.monitor_running = True

st.sidebar.header("📁 Projects")
with st.sidebar.expander("➕ New Project"):
    new_proj_name = st.text_input("Project Name").strip()
    if st.button("Create"):
        if new_proj_name:
            if db.create_project(new_proj_name):
                st.success("Created!")
                st.rerun()

projects = db.get_projects()
if not projects:
    st.stop()

project_options = {name: pid for pid, name in projects}
selected_project_name = st.sidebar.selectbox("Active Project", list(project_options.keys()))
selected_project_id = project_options[selected_project_name]

st.sidebar.divider()
new_asin = st.sidebar.text_input("Add ASIN").strip().upper()
if st.sidebar.button("Add"):
    if new_asin:
        if db.add_asin_to_project(selected_project_id, new_asin):
            st.sidebar.success("Added!")
            st.rerun()

st.header(f"Project: {selected_project_name}")
col_sync_1, _ = st.columns([1, 4])
with col_sync_1:
    if st.button("🔄 Sync All Data"):
        with st.spinner("Fetching from Amazon..."):
            result = run_monitor_cycle()
            st.toast(result)
            st.rerun()

project_asins = db.get_asins_for_project(selected_project_id)
if not project_asins:
    st.info("No products in this project.")
else:
    st.subheader("📊 Market Overview")
    overview_data = []
    for asin in project_asins:
        price = db.get_last_price(asin)
        details = db.get_product_details(asin) or {}
        with db.get_connection() as conn:
            res = conn.execute(f"SELECT timestamp FROM price_history WHERE asin='{asin}' ORDER BY timestamp DESC LIMIT 1").fetchone()
            ts = res[0] if res else "Never"
        overview_data.append({
            "ASIN": asin, 
            "Price": price if price else "N/A",
            "BSR (Rank)": details.get('sales_rank', 'N/A'),
            "Rating": details.get('reviews_rating', 'N/A'),
            "Reviews": details.get('reviews_count', 'N/A'),
            "Images": details.get('images_count', 'N/A'),
            "Last Updated": ts
        })
    st.dataframe(pd.DataFrame(overview_data), use_container_width=True)

    st.divider()
    st.subheader("📈 Product Deep Dive")
    selected_asin = st.selectbox("Analyze Product", project_asins)
    if selected_asin:
        details = db.get_product_details(selected_asin)
        if details:
            with st.expander("📋 Product Specifications", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Title:** {details.get('title')}")
                c2.write(f"**Sales Rank (BSR):** {details.get('sales_rank', 'N/A')}")
                c3.write(f"**Images:** {details.get('images_count')}")
                st.write(f"**Bullet Points:** {details.get('features')}")
                st.write(f"**List Price:** {details.get('list_price')}$")

        with db.get_connection() as conn:
            query = f"SELECT timestamp, price FROM price_history WHERE asin = '{selected_asin}' ORDER BY timestamp ASC"
            df_history = pd.read_sql_query(query, conn)
        if not df_history.empty:
            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
            fig = px.line(df_history, x='timestamp', y='price', title=f"Price Trend: {selected_asin}", markers=True)
            fig.update_traces(line_color='#ff9900', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"${df_history['price'].iloc[-1]}")
            col2.metric("Min Price", f"${df_// l'en_history['price'].min()}")
            col3.metric("Max Price", f"${df_history['price'].max()}")
            if st.button(f"🤖 Get AI Strategic Report"):
                with st.spinner("AI analyzing..."):
                    analysis = ai.analyze_trends(selected_asin, df_history) 
                    st.markdown("### 💡 AI Strategic Insights:")
                    st.markdown(analysis)
        else:
            st.warning("No price history yet. Please Sync Data.")
''')
