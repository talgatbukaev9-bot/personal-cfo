import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Личный CFO | Талгат", page_icon="💰", layout="wide")

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
    return df

df = load_data()

st.title("📊 Личный CFO | Капитал & Аналитика")

if df.empty or df["Date"].isna().all():
    st.info("Данные пока отсутствуют. Отправь скрины/список операций или новые транзакции в Telegram!")
else:
    # --- МЕТРИКИ ---
    total_inc = df[df["Type"] == "Доход"]["Amount"].sum()
    total_exp = df[df["Type"] == "Расход"]["Amount"].sum()
    net_flow = total_inc - total_exp

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Всего доходов", f"{total_inc:,.0f} ₽".replace(",", " "))
    col2.metric("🔴 Всего расходов", f"{total_exp:,.0f} ₽".replace(",", " "))
    col3.metric("💵 Чистый капитал (Дельта)", f"{net_flow:,.0f} ₽".replace(",", " "))

    st.markdown("---")

    # --- ФИЛЬТРЫ ---
    st.sidebar.header("⚙️ Период аналитики")
    view_mode = st.sidebar.radio("Обзор:", ["Вся история", "По месяцами", "По неделям", "По дням"])

    filtered_df = df.copy()
    if view_mode == "По месяцами" and "YearMonth" in df.columns:
        m = st.sidebar.selectbox("Месяц:", sorted(df["YearMonth"].dropna().unique(), reverse=True))
        filtered_df = df[df["YearMonth"] == m]
    elif view_mode == "По неделям" and "YearWeek" in df.columns:
        w = st.sidebar.selectbox("Неделя:", sorted(df["YearWeek"].dropna().unique(), reverse=True))
        filtered_df = df[df["YearWeek"] == w]
    elif view_mode == "По дням":
        d = st.sidebar.date_input("День:", value=df["Date"].max())
        filtered_df = df[df["Date"].dt.date == d]

    # --- ГРАФИКИ И ТАБЛИЦА ---
    t1, t2, t3 = st.tabs(["📉 Расходы по времени", "🍕 Категории", "📑 Все транзакции"])

    with t1:
        exp_df = filtered_df[filtered_df["Type"] == "Расход"].groupby("Date")["Amount"].sum().reset_index()
        if not exp_df.empty:
            st.plotly_chart(px.bar(exp_df, x="Date", y="Amount", title="Динамика трат"), use_container_width=True)
        else:
            st.write("За выбранный период трат нет.")

    with t2:
        cat_df = filtered_df[filtered_df["Type"] == "Расход"].groupby("Category")["Amount"].sum().reset_index()
        if not cat_df.empty:
            st.plotly_chart(px.pie(cat_df, names="Category", values="Amount", title="Распределение расходов"), use_container_width=True)

    with t3:
        st.dataframe(filtered_df[["Date", "Type", "Amount", "Category", "Raw"]].sort_values("Date", ascending=False), use_container_width=True)
