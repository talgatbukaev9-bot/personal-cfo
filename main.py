import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Личный CFO | Капитал & Аналитика", page_icon="💰", layout="wide")

CSV_PATH = "data.csv"

@st.cache_data(ttl=5)
def load_data():
    cols = ["Date", "Type", "Amount", "Category", "Raw"]
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        return pd.DataFrame(columns=cols)
    
    df = pd.read_csv(CSV_PATH)
    for col in cols:
        if col not in df.columns:
            df[col] = None
            
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["YearWeek"] = df["Date"].dt.strftime("%Y-W%U")
        df["YearMonth"] = df["Date"].dt.strftime("%Y-%m")
        df["Day"] = df["Date"].dt.strftime("%Y-%m-%d")
    return df

df = load_data()

st.title("📊 Личный CFO | Глобальный капитал и аналитика")

if df.empty or df["Date"].isna().all():
    st.info("Данные пока отсутствуют. Как только в Telegram придут транзакции — здесь появится вся глобальная и детальная статистика!")
else:
    # --- САЙДБАР: ВЫБОР РЕЖИМА ОБЗОРА ---
    st.sidebar.header("⚙️ Режим отображения")
    mode = st.sidebar.radio("Уровень аналитики:", ["🌐 Глобальный (Все данные)", "📅 По месяцам", "📆 По неделям", "📌 По дням"])

    filtered_df = df.copy()

    if mode == "📅 По месяцам" and "YearMonth" in df.columns:
        m = st.sidebar.selectbox("Выберите месяц:", sorted(df["YearMonth"].dropna().unique(), reverse=True))
        filtered_df = df[df["YearMonth"] == m]
    elif mode == "📆 По неделям" and "YearWeek" in df.columns:
        w = st.sidebar.selectbox("Выберите неделю:", sorted(df["YearWeek"].dropna().unique(), reverse=True))
        filtered_df = df[df["YearWeek"] == w]
    elif mode == "📌 По дням":
        d = st.sidebar.date_input("Выберите день:", value=df["Date"].max())
        filtered_df = df[df["Date"].dt.date == d]

    # --- ГЛОБАЛЬНЫЕ МЕТРИКИ КАПИТАЛА ---
    total_inc = filtered_df[filtered_df["Type"] == "Доход"]["Amount"].sum()
    total_exp = filtered_df[filtered_df["Type"] == "Расход"]["Amount"].sum()
    net_flow = total_inc - total_exp
    savings_rate = (net_flow / total_inc * 100) if total_inc > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🟢 Доходы", f"{total_inc:,.0f} ₽".replace(",", " "))
    c2.metric("🔴 Расходы", f"{total_exp:,.0f} ₽".replace(",", " "))
    c3.metric("💵 Чистый капитал (Дельта)", f"{net_flow:,.0f} ₽".replace(",", " "))
    c4.metric("📈 Сбережения", f"{savings_rate:.1f}%")

    st.markdown("---")

    # --- ВКЛАДКИ С ГРАФИКАМИ ---
    t1, t2, t3 = st.tabs(["📊 Динамика и тренды", "🍕 Категории (FIXED / LIFE / WANT / LEAK)", "📑 Реестр операций"])

    with t1:
        st.subheader("Динамика расходов по времени")
        exp_df = filtered_df[filtered_df["Type"] == "Расход"]
        if not exp_df.empty:
            daily_grp = exp_df.groupby("Day")["Amount"].sum().reset_index()
            fig = px.bar(daily_grp, x="Day", y="Amount", title="Расходы по дням", color_discrete_sequence=["#FF4B4B"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет трат за выбранный период.")

    with t2:
        st.subheader("Структура расходов по категориям")
        cat_df = filtered_df[filtered_df["Type"] == "Расход"].groupby("Category")["Amount"].sum().reset_index()
        if not cat_df.empty:
            fig_pie = px.pie(cat_df, names="Category", values="Amount", title="Доли категорий", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Нет трат за выбранный период.")

    with t3:
        st.subheader("Список всех записанных транзакций")
        st.dataframe(filtered_df[["Date", "Type", "Amount", "Category", "Raw"]].sort_values("Date", ascending=False), use_container_width=True)
