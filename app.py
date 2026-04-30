import streamlit as st
import pandas as pd
import plotly.express as px
from database import Database
from ai_analyst import AIAnalyst

# Page config
st.set_page_config(page_title="Amazon Project Hub", layout="wide")

db = Database()
ai = AIAnalyst()

st.title("🏢 Amazon Competitor Project Hub")
st.markdown("Управление несколькими проектами мониторинга с AI-аналитикой")

# --- Sidebar: Project Management ---
st.sidebar.header("📁 Управление Проектами")

# Create new project
with st.sidebar.expander("➕ Создать новый проект"):
    new_proj_name = st.text_input("Название проекта").strip()
    if st.button("Создать проект"):
        if new_proj_name:
            if db.create_project(new_proj_name):
                st.success(f"Проект '{new_proj_name}' создан!")
                st.rerun()
            else:
                st.error("Проект с таким именем уже существует")
        else:
            st.error("Введите название")

# Project selection
projects = db.get_projects()
if not projects:
    st.sidebar.warning("Сначала создайте проект")
    st.info("Пожалуйста, создайте ваш первый проект в боковой панели слева.")
    st.stop()

project_options = {name: pid for pid, name in projects}
selected_project_name = st.sidebar.selectbox("Выберите активный проект", list(project_options.keys()))
selected_project_id = project_options[selected_project_name]

# Add ASIN to selected project
st.sidebar.divider()
st.sidebar.subheader(f"📦 Товары в {selected_project_name}")
new_asin = st.sidebar.text_input("Добавить ASIN в этот проект").strip().upper()
if st.sidebar.button("Добавить товар"):
    if new_asin:
        if db.add_asin_to_project(selected_project_id, new_asin):
            st.sidebar.success(f"Товар {new_asin} добавлен в {selected_project_name}!")
            st.rerun()
        else:
            st.sidebar.error("Этот товар уже есть в проекте")
    else:
        st.sidebar.error("Введите ASIN")

# --- Main Content ---

st.header(f"Проект: {selected_project_name}")

# Get ASINs for this project
project_asins = db.get_asins_for_project(selected_project_id)

if not project_asins:
    st.info("В этом проекте пока нет товаров. Добавьте их через боковую панель.")
else:
    # 1. Overview Table for current project
    st.subheader("📊 Текущий статус товаров проекта")
    
    # Build a list of current prices for the project ASINs
    overview_data = []
    for asin in project_asins:
        price = db.get_last_price(asin)
        overview_data.append({"ASIN": asin, "Last Price": price if price else "No data"})
    
    df_overview = pd.DataFrame(overview_data)
    st.dataframe(df_overview, use_container_width=True)

    # 2. Detailed Analysis
    st.divider()
    st.subheader("📈 Анализ и AI-Стратегия")
    
    selected_asin = st.selectbox("Выберите товар для детального анализа", project_asins)
    
    if selected_asin:
        # Get history for selected ASIN
        with db.get_connection() as conn:
            query = f"SELECT timestamp, price FROM price_history WHERE asin = '{selected_asin}' ORDER BY timestamp ASC"
            df_history = pd.read_sql_query(query, conn)
        
        if not df_history.empty:
            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
            
            # Chart
            fig = px.line(df_history, x='timestamp', y='price', 
                          title=f"Динамика цены: {selected_asin}",
                          labels={'timestamp': 'Дата', 'price': 'Цена ($)'},
                          markers=True)
            fig.update_traces(line_color='#ff9900', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Текущая цена", f"${df_history['price'].iloc[-1]}")
            col2.metric("Мин. цена", f"${df_history['price'].min()}")
            col3.metric("Макс. цена", f"${df_history['price'].max()}")
            
            # AI Button
            if st.button(f"🤖 Получить AI-анализ для {selected_asin}"):
                with st.spinner("AI анализирует рынок и ищет возможности..."):
                    analysis = ai.analyze_trends(selected_asin, df_history)
                    st.markdown("### 💡 Рекомендации AI:")
                    st.markdown(analysis)
        else:
            st.warning("История цен еще не собрана. Запустите monitor.py и подождите обновления.")
