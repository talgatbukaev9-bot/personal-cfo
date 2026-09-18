import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="Личный CFO", page_icon="💰", layout="wide")

CSV_PATH = "data.csv"

# Загрузка данных
@st.cache_data(ttl=10)
def load_data():
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Raw"])
        df.to_csv(CSV_PATH, index=False)
        return df
    
    df = pd.read_csv(CSV_PATH)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["YearWeek"] = df["Date"].dt.strftime("%Y-W%U")
        df["YearMonth"] = df["Date"].dt.strftime("%Y-%m")
        df["DayName"] = df["Date"].dt.strftime("%d.%m (%a)")
    return df

df = load_data()

st.title("📊 Личный CFO | Детальная аналитика финансов")

if df.empty:
    st.info("Пока нет записанных транзакций. Все новые покупки и пополнения из Telegram появятся здесь!")
else:
    # ---------------- САЙДБАР: ФИЛЬТРЫ ----------------
    st.sidebar.header("⚙️ Фильтры и Период")
    
    period_type = st.sidebar.radio(
        "Группировка и фильтр:",
        ["Вся история", "По месяцами", "По неделям", "По дням"]
    )

    filtered_df = df.copy()

    if period_type == "По месяцами":
        selected_month = st.sidebar.selectbox("Выберите месяц:", sorted(df["YearMonth"].unique(), reverse=True))
        filtered_df = df[df["YearMonth"] == selected_month]
    elif period_type == "По неделям":
        selected_week = st.sidebar.selectbox("Выберите неделю:", sorted(df["YearWeek"].unique(), reverse=True))
        filtered_df = df[df["YearWeek"] == selected_week]
    elif period_type == "По дням":
        selected_date = st.sidebar.date_input("Выберите день:", value=df["Date"].max())
        filtered_df = df[df["Date"].dt.date == selected_date]

    # ---------------- ГЛАВНЫЕ МЕТРИКИ ----------------
    total_income = filtered_df[filtered_df["Type"] == "Доход"]["Amount"].sum()
    total_expense = filtered_df[filtered_df["Type"] == "Расход"]["Amount"].sum()
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🟢 Доходы", f"{total_income:,.0f} ₽".replace(",", " "))
    col2.metric("🔴 Расходы", f"{total_expense:,.0f} ₽".replace(",", " "))
    col3.metric("💵 Дельта (Чистый поток)", f"{net_savings:,.0f} ₽".replace(",", " "))
    col4.metric("📈 Норма сбережений", f"{savings_rate:.1f}%")

    st.markdown("---")

    # ---------------- ДЕТАЛЬНАЯ АНАЛИТИКА ТРАТ ----------------
    st.subheader("📉 Детализация трат и расходов")

    tab1, tab2, tab3 = st.tabs(["📅 Тренды по времени", "🍕 По категориям (FIXED/LIFE/WANT/LEAK)", "📑 Таблица операций"])

    with tab1:
        st.write("### Динамика расходов")
        
        # Группировка по дням
        daily_expense = filtered_df[filtered_df["Type"] == "Расход"].groupby("Date")["Amount"].sum().reset_index()
        if not daily_expense.empty:
            fig_daily = px.bar(
                daily_expense, 
                x="Date", 
                y="Amount", 
                title="Расходы по дням",
                labels={"Amount": "Сумма (₽)", "Date": "Дата"},
                color_discrete_sequence=["#FF4B4B"]
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        
        # Группировка по неделям
        weekly_expense = df[df["Type"] == "Расход"].groupby("YearWeek")["Amount"].sum().reset_index()
        if not weekly_expense.empty:
            fig_weekly = px.line(
                weekly_expense, 
                x="YearWeek", 
                y="Amount", 
                markers=True,
                title="Сравнение трат по неделям (За весь период)",
                labels={"Amount": "Сумма (₽)", "YearWeek": "Неделя"},
                color_discrete_sequence=["#0068C9"]
            )
            st.plotly_chart(fig_weekly, use_container_width=True)

    with tab2:
        st.write("### Разбор категорий трат")
        cat_expense = filtered_df[filtered_df["Type"] == "Расход"].groupby("Category")["Amount"].sum().reset_index()
        
        if not cat_expense.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                fig_pie = px.pie(
                    cat_expense, 
                    names="Category", 
                    values="Amount", 
                    title="Доли категорий трат",
                    hole=0.4
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_chart2:
                fig_cat_bar = px.bar(
                    cat_expense.sort_values(by="Amount", ascending=False),
                    x="Category",
                    y="Amount",
                    color="Category",
                    title="Сумма трат по категориям"
                )
                st.plotly_chart(fig_cat_bar, use_container_width=True)
        else:
            st.info("За выбранный период нет расходов.")

    with tab3:
        st.write("### Все операции за выбранный период")
        st.dataframe(
            filtered_df[["Date", "Type", "Amount", "Category", "Raw"]].sort_values(by="Date", ascending=False),
            use_container_width=True
        )
