import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Личный CFO | Система управления капиталом", page_icon="💰", layout="wide")

CSV_PATH = "data.csv"

# Исторические данные из оригинального дашборда (Апр - Авг 2026)
HISTORICAL_DATA = [
    {"Date": "2026-04-15", "Type": "Доход", "Amount": 0, "Category": "FIXED", "Raw": "Базовый доход Апр"},
    {"Date": "2026-04-15", "Type": "Расход", "Amount": 38000, "Category": "LIFE", "Raw": "Базовый расход Апр"},
    {"Date": "2026-05-15", "Type": "Доход", "Amount": 28000, "Category": "FIXED", "Raw": "Базовый доход Май"},
    {"Date": "2026-05-15", "Type": "Расход", "Amount": 25000, "Category": "LIFE", "Raw": "Базовый расход Май"},
    {"Date": "2026-06-15", "Type": "Доход", "Amount": 48000, "Category": "FIXED", "Raw": "Базовый доход Июн"},
    {"Date": "2026-06-15", "Type": "Расход", "Amount": 48000, "Category": "LIFE", "Raw": "Базовый расход Июн"},
    {"Date": "2026-07-15", "Type": "Доход", "Amount": 82000, "Category": "FIXED", "Raw": "Базовый доход Июл"},
    {"Date": "2026-07-15", "Type": "Расход", "Amount": 88000, "Category": "LIFE", "Raw": "Базовый расход Июл"},
    {"Date": "2026-08-15", "Type": "Доход", "Amount": 105000, "Category": "FIXED", "Raw": "Базовый доход Авг"},
    {"Date": "2026-08-15", "Type": "Расход", "Amount": 85000, "Category": "LIFE", "Raw": "Базовый расход Авг"},
    {"Date": "2026-08-20", "Type": "Расход", "Amount": 13500, "Category": "LEAK", "Raw": "Утечки за период"},
]

@st.cache_data(ttl=5)
def load_data():
    cols = ["Date", "Type", "Amount", "Category", "Raw"]
    hist_df = pd.DataFrame(HISTORICAL_DATA)
    
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        new_df = pd.read_csv(CSV_PATH)
        for col in cols:
            if col not in new_df.columns:
                new_df[col] = None
        df = pd.concat([hist_df, new_df], ignore_index=True)
    else:
        df = hist_df
        
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["YearMonth"] = df["Date"].dt.strftime("%Y-%m")
    df["YearWeek"] = df["Date"].dt.strftime("%Y-W%U")
    df["Day"] = df["Date"].dt.strftime("%Y-%m-%d")
    return df

df = load_data()

st.title("Добрый день, Талгат 👋")

# --- ВЕРХНИЕ МЕТРИКИ (ИЗ ОРИГИНАЛЬНОГО ДАШБОРДА) ---
net_capital = -26967
income_total = df[df["Type"] == "Доход"]["Amount"].sum()
expense_total = df[df["Type"] == "Расход"]["Amount"].sum()
net_flow = income_total - expense_total

avg_income = 67200
avg_burn_rate = 72600
savings_rate = -8.0
leaks = df[df["Category"] == "LEAK"]["Amount"].sum()
if leaks == 0:
    leaks = 13500

col_cap, col_stat = st.columns([1, 2])

with col_cap:
    st.markdown("### ЧИСТЫЙ КАПИТАЛ")
    st.markdown(f"# {net_capital:,.0f} ₽".replace(",", " "))
    st.caption("Ликвидный резерв + накопленный результат")
    st.success("+17 797 ₽ за месяц (Деньги — это ресурс для развития)")

with col_stat:
    m1, m2 = st.columns(2)
    m1.metric("СЕДНИЙ ДОХОД", f"{avg_income/1000:.1f} тыс. ₽", "расчет за 5 месяцев")
    m2.metric("СРЕДНИЙ BURN RATE", f"{avg_burn_rate/1000:.1f} тыс. ₽", "расходы за месяц")
    
    m3, m4 = st.columns(2)
    m3.metric("НОРМА СБЕРЕЖЕНИЙ", f"{savings_rate:.1f}%", "цель: не менее 20%", delta_color="inverse")
    m4.metric("НАЙДЕНО УТЕЧЕК ⚡", f"{leaks/1000:.1f} тыс. ₽", "можно вернуть в капитал", delta_color="inverse")

st.markdown("---")

# --- ТАБЫ: ГЛОБАЛЬНЫЙ И ДЕТАЛЬНЫЙ АНАЛИЗ ---
tab_global, tab_detail, tab_table = st.tabs(["📊 Глобальный баланс (Апр-Авг+)", "📅 Анализ по дням и неделям", "📑 Все транзакции"])

with tab_global:
    st.subheader("Доход против расхода")
    
    # Группировка по месяцам
    monthly_df = df.groupby(["YearMonth", "Type"])["Amount"].sum().unstack(fill_value=0).reset_index()
    
    if not monthly_df.empty:
        fig = go.Figure()
        if "Доход" in monthly_df.columns:
            fig.add_trace(go.Bar(x=monthly_df["YearMonth"], y=monthly_df["Доход"], name="Доход", marker_color="#1E4D3B"))
        if "Расход" in monthly_df.columns:
            fig.add_trace(go.Bar(x=monthly_df["YearMonth"], y=monthly_df["Расход"], name="Расход", marker_color="#80FF00"))
            
        fig.update_layout(barmode="group", xaxis_title="Месяц", yaxis_title="Сумма (₽)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

with tab_detail:
    st.sidebar.header("⚙️ Фильтры детализации")
    period = st.sidebar.radio("Период:", ["Все дни", "По неделям", "По дням"])
    
    filtered_df = df.copy()
    if period == "По неделям":
        w = st.sidebar.selectbox("Неделя:", sorted(df["YearWeek"].dropna().unique(), reverse=True))
        filtered_df = df[df["YearWeek"] == w]
    elif period == "По дням":
        d = st.sidebar.date_input("День:", value=df["Date"].max())
        filtered_df = df[df["Date"].dt.date == d]

    st.subheader("Динамика трат")
    exp_df = filtered_df[filtered_df["Type"] == "Расход"]
    if not exp_df.empty:
        daily_exp = exp_df.groupby("Day")["Amount"].sum().reset_index()
        fig_daily = px.bar(daily_exp, x="Day", y="Amount", color_discrete_sequence=["#80FF00"], title="Расходы")
        st.plotly_chart(fig_daily, use_container_width=True)
    else:
        st.info("Нет трат за выбранный период.")

with tab_table:
    st.subheader("Полный реестр операций")
    st.dataframe(df[["Date", "Type", "Amount", "Category", "Raw"]].sort_values("Date", ascending=False), use_container_width=True)
