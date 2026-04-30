import streamlit as st
import pandas as pd
import plotly.express as px
from database import Database
from ai_analyst import AIAnalyst
from keepa_client import KeepaClient
import threading
import time
from datetime import datetime

# Page config
st.set_page_config(page_title="Amazon Project Hub", layout="wide")

# --- GLOBAL STATE ---
if 'monitor_running' not in st.session_state:
    st.session_state.monitor_running = False

db = Database()
ai = AIAnalyst()
client = KeepaClient()

st.title("🏢 Amazon Competitor Project Hub")
st.markdown("Управление проектами и автоматический сбор данных")

# --- BACKGROUND MONITOR LOGIC ---
def run_monitor_cycle():
    """Function that performs one full update cycle for all tracked ASINs"""
    asins = db.get_all_tracked_asins()
    if not asins:
        return "No ASINs found to monitor."
    
    updates_count = 0
    for asin in asins:
        data = client.get_product_data(asin)
        if data:
            price = client.extract_current_price(data, "new")
            if price:
                db.save_price(asin, price)
                updates_count += 1
    return f"Updated {updates_count}/{len(asins)} products."

def monitor_thread_loop():
    """Infinite loop for background monitoring (runs every hour)"""
    while True:
        run_monitor_cycle()
        time.sleep(3600)

# Start background thread if not running
if not st.session_state.monitor_running:
    thread = threading.Thread(target=monitor_thread_loop, daemon=True)
    thread.start()
    st.session_state.monitor_running = True

# --- SIDEBAR: Project Management ---
st.sidebar.header("📁 Управление Проектами")

with st.sidebar.expander("➕ Создать новый проект"):
    new_proj_name = st.text_input("Название проекта").strip()
    if st.button("Создать проект"):
        if new_proj_name:
            if db.create_project(new_proj_name):
                st.success(f"Проект '{new_proj_name}' создан!")
                st.rerun()
            else:
                st.error("Проект с таким именем уже существует")

projects = db.get_projects()
if not projects:
    st.sidebar.warning("Сначала создайте проект")
    st.info("Пожалуйста, создайте ваш первый проект в боковой панели слева.")
    st.stop()

project_options = {name: pid for pid, name in projects}
selected_project_name = st.sidebar.selectbox("Выберите активный проект", list(project_options.keys()))
selected_project_id = project_options[selected_project_name]

st.sidebar.divider()
st.sidebar.subheader(f"📦 Товары в {selected_project_name}")
new_asin = st.sidebar.text_input("Добавить ASIN в этот проект").strip().upper()
if st.sidebar.button("Добавить товар"):
    if new_asin:
        if db.add_asin_to_project(selected_project_id, new_asin):
            st.sidebar.success(f"Товар {new_asin} добавлен!")
            st.rerun()
        else:
            st.sidebar.error("Товар уже в проекте")

# --- MAIN CONTENT ---
st.header(f"Проект: {selected_project_name}")

st.divider()
col_sync_1, col_sync_2 = st.columns([1, 4])
with col_sync_1:
    if st.button("🔄 Обновить данные сейчас"):
        with st.spinner("Синхронизация с Amazon..."):
            result = run_monitor_cycle()
            st.toast(result)
            st.rerun()

project_asins = db.get_asins_for_project(selected_project_id)

if not project_asins:
    st.info("В этом проекте пока нет товаров.")
else:
    st.subheader("📊 Текущий статус товаров проекта")
    overview_data = []
    for asin in project_asins:
        price = db.get_last_price(asin)
        with db.get_connection() as conn:
            res = conn.execute(f"SELECT timestamp FROM price_history WHERE asin='{asin}' ORDER BY timestamp DESC LIMIT 1").fetchone()
            ts = res[0] if res else "Never"
        overview_data.append({"ASIN": asin, "Last Price": price if price else "No data", "Last Updated": ts})
    
    df_overview = pd.DataFrame(overview_data)
    st.dataframe(df_overview, use_container_width=True)

    st.divider()
    st.subheader("📈 Анализ и AI-Стратегия")
    selected_asin = st.selectbox("Выберите товар для детального анализа", project_asins)
    
    if selected_asin:
        with db.get_connection() as conn:
            query = f"SELECT timestamp, price FROM price_history WHERE asin = '{selected_asin}' ORDER BY timestamp ASC"
            df_history = pd.read_sql_query(query, conn)
        
        if not df_history.empty:
            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
            fig = px.line(df_history, x='timestamp', y='price', 
                          title=f"Динамика цены: {selected_asin}", markers=True)
            fig.update_traces(line_color='#ff9900', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Текущая цена", f"${df_history['price'].iloc[-1]}")
            col2.metric("Мин. цена", f"${df_history['price'].min()}")
            col3.metric("Макс. цена", f"${df_history['price'].max()}")
            
            if st.button(f"🤖 Получить AI-анализ для {selected_asin}"):
                with st.spinner("AI анализирует рынок..."):
                    analysis = ai.analyze_trends(selected_asin, df_history)
                    st.markdown("### 💡 Рекомендации AI:")
                    st.markdown(analysis)
        else:
            st.warning("Данные по этому товару еще не собраны. Нажмите 'Обновить данные сейчас' выше.")
