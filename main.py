import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Личный CFO", page_icon="💰", layout="wide")

CSV_PATH = "data.csv"

# Загрузка данных с защитой от отсутствующих колонок
@st.cache_data(ttl=5)
def load_data():
    required_columns = ["Date", "Type", "Amount", "Category", "Raw"]
    
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        df = pd.DataFrame(columns=required_columns)
        df.to_csv(CSV_PATH, index=False)
        return df
    
    df = pd.read_csv(CSV_PATH)
    
    # Проверка наличия всех колонок
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            
    if not df.empty and df["Date"].notna().any():
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["YearWeek"] = df["Date"].dt.strftime("%Y-W%U")
        df["YearMonth"] = df["Date"].dt.strftime("%Y-%m")
        df["DayName"] = df["Date"].dt.strftime("%d.%m (%a)")
        
    return df

df = load_data()

st.title("📊 Личный CFO | Детальная аналитика финансов")

if df.empty or df["Date"].isna().all():
    st.info("Пока нет записанных транзакций. Отправьте тестовое сообщение в Telegram-бота!")
else:
    # ---------------- САЙДБАР: ФИЛЬТРЫ ----------------
    st.sidebar.header("⚙️ Фильтры и Период")
    
    period_type = st.sidebar.radio(
        "Группировка и фильтр:",
        ["Вся история", "По месяцам", "По неделям", "По дням"]
    )

    filtered_df = df.copy()

    if period_type == "По месяцам" and "YearMonth" in df.columns:
        months = sorted(df["YearMonth"].dropna().unique(), reverse=True)
        if months:
            selected_month = st.sidebar.selectbox("Выберите месяц:", months)
            filtered_df = df[df["YearMonth"] == selected_month]
    elif period_type == "По неделям" and "YearWeek" in df.columns:
        weeks = sorted(df["YearWeek"].dropna().unique(), reverse=True)
        if weeks:
            selected_week = st.sidebar.selectbox("Выберите неделю:", weeks)
            filtered_df = df[df["YearWeek"] == selected_week]
    elif period_type == "По дням":
        valid_dates = df["Date"].dropna()
        max_date = valid_dates.max() if not valid_dates.empty else pd.Timestamp.now()
        selected_date = st.sidebar.date_input("Выберите день:", value=max_date)
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

    tab1, tab2, tab3 = st.tabs(["📅 Тренды по времени", "🍕 По категориям", "📑 Таблица операций"])

    with tab1:
        st.write("### Динамика расходов")
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

    with tab2:
        st.write("### Разбор категорий трат")
        cat_expense = filtered_df[filtered_df["Type"] == "Расход"].groupby("Category")["Amount"].sum().reset_index()
        if not cat_expense.empty:
            fig_pie = px.pie(cat_expense, names="Category", values="Amount", title="Доли категорий трат", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("За выбранный период нет расходов.")

    with tab3:
        st.write("### Все операции за выбранный период")
        st.dataframe(
            filtered_df[["Date", "Type", "Amount", "Category", "Raw"]].sort_values(by="Date", ascending=False),
            use_container_width=True
        )
