import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="Личный CFO | Система управления капиталом",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Подключение манифеста для PWA
st.markdown('<link rel="manifest" href="./manifest.json">', unsafe_allow_html=True)

CSV_PATH = "data.csv"

# Базовые исторические данные по месяцам
HISTORICAL_DATA = [
    {"Дата": "2026-04-15", "Тип": "Доход", "Сумма": 0, "Категория": "FIXED", "Описание": "Базовый доход Апр"},
    {"Дата": "2026-04-15", "Тип": "Расход", "Сумма": 38000, "Категория": "LIFE", "Описание": "Базовый расход Апр"},
    {"Дата": "2026-05-15", "Тип": "Доход", "Сумма": 28000, "Категория": "FIXED", "Описание": "Базовый доход Май"},
    {"Дата": "2026-05-15", "Тип": "Расход", "Сумма": 25000, "Категория": "LIFE", "Описание": "Базовый расход Май"},
    {"Дата": "2026-06-15", "Тип": "Доход", "Сумма": 48000, "Категория": "FIXED", "Описание": "Базовый доход Июн"},
    {"Дата": "2026-06-15", "Тип": "Расход", "Сумма": 48000, "Категория": "LIFE", "Описание": "Базовый расход Июн"},
    {"Дата": "2026-07-15", "Тип": "Доход", "Сумма": 82000, "Категория": "FIXED", "Описание": "Базовый доход Июл"},
    {"Дата": "2026-07-15", "Тип": "Расход", "Сумма": 88000, "Категория": "LIFE", "Описание": "Базовый расход Июл"},
    {"Дата": "2026-08-15", "Тип": "Доход", "Сумма": 105000, "Категория": "FIXED", "Описание": "Базовый доход Авг"},
    {"Дата": "2026-08-15", "Тип": "Расход", "Сумма": 85000, "Категория": "LIFE", "Описание": "Базовый расход Авг"},
]

@st.cache_data(ttl=5)
def load_data():
    hist_df = pd.DataFrame(HISTORICAL_DATA)
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        try:
            raw_csv = pd.read_csv(CSV_PATH)
            # Приведение наименований колонок к единому стандарту
            rename_dict = {
                "Date": "Дата", "Type": "Тип", "Amount": "Сумма", 
                "Category": "Категория", "Raw": "Описание"
            }
            raw_csv = raw_csv.rename(columns=rename_dict)
            df = pd.concat([hist_df, raw_csv], ignore_index=True)
        except Exception:
            df = hist_df
    else:
        df = hist_df

    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")
    df["Сумма"] = pd.to_numeric(df["Сумма"], errors="coerce").fillna(0)
    df["Месяц"] = df["Дата"].dt.strftime("%Y-%m")
    df["Неделя"] = df["Дата"].dt.strftime("%Y-W%U")
    df["День"] = df["Дата"].dt.strftime("%Y-%m-%d")
    return df

df = load_data()

# --- ШАПКА И ПРИВЕТСТВИЕ ---
st.title("Добрый день, Талгат 👋")

# --- БОКОВАЯ ПАНЕЛЬ И ФИЛЬТРЫ ---
st.sidebar.header("⚙️ Период и Детализация")
view_mode = st.sidebar.radio("Масштаб:", ["Глобальный (Все время)", "По месяцам", "По неделям", "По дням"])

filtered_df = df.copy()

if view_mode == "По месяцам":
    months = sorted(df["Месяц"].dropna().unique(), reverse=True)
    selected_m = st.sidebar.selectbox("Выберите месяц:", months)
    filtered_df = df[df["Месяц"] == selected_m]
elif view_mode == "По неделям":
    weeks = sorted(df["Неделя"].dropna().unique(), reverse=True)
    selected_w = st.sidebar.selectbox("Выберите неделю:", weeks)
    filtered_df = df[df["Неделя"] == selected_w]
elif view_mode == "По дням":
    selected_d = st.sidebar.date_input("Выберите день:", value=df["Дата"].max())
    filtered_df = df[df["Дата"].dt.date == selected_d]

# --- ДАШБОРД ВЕРХНИХ МЕТРИК ---
net_capital = -26967
avg_income = 67200
avg_burn_rate = 72600
savings_rate = -8.0
leaks_total = 13500

col_cap, col_stat = st.columns([1, 2])

with col_cap:
    st.markdown("### ЧИСТЫЙ КАПИТАЛ")
    st.markdown(f"# {net_capital:,.0f} ₽".replace(",", " "))
    st.caption("Ликвидный резерв + накопленный результат")
    st.success("+17 797 ₽ за месяц\n\n_Деньги — это ресурс для развития_")

with col_stat:
    m1, m2 = st.columns(2)
    m1.metric("СРЕДНИЙ ДОХОД", f"{avg_income/1000:.1f} тыс. ₽", "расчет за 5 месяцев")
    m2.metric("СРЕДНИЙ BURN RATE", f"{avg_burn_rate/1000:.1f} тыс. ₽", "расходы за месяц")
    
    m3, m4 = st.columns(2)
    m3.metric("НОРМА СБЕРЕЖЕНИЙ", f"{savings_rate:.1f}%", "цель: не менее 20%", delta_color="inverse")
    m4.metric("НАЙДЕНО УТЕЧЕК ⚡", f"{leaks_total/1000:.1f} тыс. ₽", "можно вернуть в капитал", delta_color="inverse")

# Финансовая автономия (спидометр)
col_gauge, col_bar = st.columns([1, 2])

with col_gauge:
    st.markdown("##### ФИНАНСОВАЯ АВТОНОМИЯ")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=0.3,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Сколько месяцев можно жить без дохода"},
        gauge={
            'axis': {'range': [0, 12]},
            'bar': {'color': "#80FF00"},
            'steps': [
                {'range': [0, 3], 'color': "#331111"},
                {'range': [3, 6], 'color': "#333311"},
                {'range': [6, 12], 'color': "#113311"}
            ],
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_bar:
    st.markdown("##### Доход против расхода")
    monthly_grp = df.groupby(["Месяц", "Тип"])["Сумма"].sum().unstack(fill_value=0).reset_index()
    fig_bar = go.Figure()
    if "Доход" in monthly_grp.columns:
        fig_bar.add_trace(go.Bar(x=monthly_grp["Месяц"], y=monthly_grp["Доход"], name="Доход", marker_color="#1E4D3B"))
    if "Расход" in monthly_grp.columns:
        fig_bar.add_trace(go.Bar(x=monthly_grp["Месяц"], y=monthly_grp["Расход"], name="Расход", marker_color="#80FF00"))
    fig_bar.update_layout(barmode="group", height=250, margin=dict(l=10, r=10, t=30, b=10), template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# --- ОСНОВНЫЕ ВКЛАДКИ (ТАБЫ) С ТВОЕГО КОДА ---
tab1, tab2, tab3 = st.tabs(["🎯 Жесткие лимиты", "⚡ Охота на утечки (LEAK)", "📑 История всех записей"])

with tab1:
    st.subheader("Жесткие лимиты расходов")
    limits_data = [
        {"Категория": "Фастфуд / Кафе", "Было": "5 000 ₽", "Лимит": "2 000 ₽", "Эффект": "+3 000 ₽"},
        {"Категория": "Такси / Самокаты", "Было": "6 000 ₽", "Лимит": "2 000 ₽", "Эффект": "+4 000 ₽"},
        {"Категория": "Цифровые донаты", "Было": "1 500 ₽", "Лимит": "0 ₽", "Эффект": "+1 500 ₽"}
    ]
    st.table(pd.DataFrame(limits_data))

with tab2:
    st.subheader("Охота на утечки (LEAK)")
    leaks = pd.DataFrame([
        {
            "Утечка": "Аренда самокатов", 
            "₽/мес": 4367, 
            "₽/ГОД": 52404, 
            "Конкретное действие": "Удалить приложения Whoosh/Юрент", 
            "Приоритет": 1
        },
        {
            "Утечка": "Спонтанный фастфуд", 
            "₽/мес": 8638, 
            "₽/ГОД": 103656, 
            "Конкретное действие": "Перекусы с собой, лимит 2к", 
            "Приоритет": 1
        },
        {
            "Утечка": "Игровые донаты", 
            "₽/мес": 1500, 
            "₽/ГОД": 18000, 
            "Конкретное действие": "Отвязать карту от аккаунтов", 
            "Приоритет": 2
        }
    ])
    st.dataframe(leaks, use_container_width=True)

with tab3:
    st.subheader("История всех записей")
    st.dataframe(filtered_df[["Дата", "Тип", "Сумма", "Категория", "Описание"]].sort_values(by="Дата", ascending=False), use_container_width=True)
