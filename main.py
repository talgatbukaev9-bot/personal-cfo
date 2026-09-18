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
# --- КАСТОМНЫЙ CSS ДЛЯ ДИЗАЙНА ---
st.markdown("""
    <style>
    .stApp { background-color: #0c1512; color: #e0e6e3; }
    div[data-testid="stSidebar"] { background-color: #111e1a; border-right: 1px solid #1a2f28; }
    .hero-card {
        background: linear-gradient(135deg, #142a22 0%, #0e1c17 100%);
        border: 1px solid #234739;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #111f1a;
        border: 1px solid #1a332a;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .green-text { color: #8ef552; }
    .muted-text { color: #83998f; font-size: 0.85rem; }
    .stButton>button {
        background-color: #8ef552;
        color: #0c1512;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover { background-color: #72c740; color: #0c1512; }
    </style>
""", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ (ФАЙЛ) ---
DATA_FILE = "data.csv"


def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)

    data = [
        {"Дата": "2026-04-15", "Тип": "Расход", "Категория": "LEAK", "Описание": "Самокаты / Фастфуд", "Сумма": 8602,
         "Месяц": "Апр"},
        {"Дата": "2026-04-20", "Тип": "Расход", "Категория": "WANT", "Описание": "Личные переводы", "Сумма": 39720,
         "Месяц": "Апр"},
        {"Дата": "2026-05-10", "Тип": "Доход", "Категория": "Доход", "Описание": "Выручка Дёнер/Смена", "Сумма": 24596,
         "Месяц": "Май"},
        {"Дата": "2026-05-15", "Тип": "Расход", "Категория": "LIFE", "Описание": "Личные расходы", "Сумма": 22373,
         "Месяц": "Май"},
        {"Дата": "2026-06-10", "Тип": "Доход", "Категория": "Доход", "Описание": "Выручка/Заработки", "Сумма": 51283,
         "Месяц": "Июн"},
        {"Дата": "2026-06-15", "Тип": "Расход", "Категория": "FIXED", "Описание": "Зал/Связь/Обязательные",
         "Сумма": 46938, "Месяц": "Июн"},
        {"Дата": "2026-07-10", "Тип": "Доход", "Категория": "Доход", "Описание": "Выручка магазина FORBIDEEN",
         "Сумма": 85354, "Месяц": "Июл"},
        {"Дата": "2026-07-15", "Тип": "Расход", "Категория": "LEAK", "Описание": "Фастфуд/Переводы/Самокаты",
         "Сумма": 88884, "Месяц": "Июл"},
        {"Дата": "2026-08-10", "Тип": "Доход", "Категория": "Доход", "Описание": "Выручка магазина FORBIDEEN",
         "Сумма": 99130, "Месяц": "Авг"},
        {"Дата": "2026-08-15", "Тип": "Расход", "Категория": "LEAK", "Описание": "Закупки/Личные/Самокаты",
         "Сумма": 98610, "Месяц": "Авг"},
        {"Дата": "2026-09-10", "Тип": "Доход", "Категория": "Доход", "Описание": "Выручка сентябрь", "Сумма": 75712,
         "Месяц": "Сен"},
        {"Дата": "2026-09-15", "Тип": "Расход", "Категория": "WANT", "Описание": "Шопинг/Одежда/Личное", "Сумма": 57915,
         "Месяц": "Сен"}
    ]
    df_init = pd.DataFrame(data)
    df_init.to_csv(DATA_FILE, index=False)
    return df_init


df = load_data()

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.title("💼 Личный CFO")
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Внести операцию")

with st.sidebar.form("new_transaction", clear_on_submit=True):
    tx_date = st.date_input("Дата операции")
    tx_type = st.selectbox("Тип", ["Расход", "Доход"])
    tx_cat = st.selectbox("Категория",
                          ["FIXED (Обязательные)", "LIFE (Базовые)", "WANT (Хотелки)", "LEAK (Утечки)", "Доход",
                           "Перевод/Бизнес"])
    tx_desc = st.text_input("Описание (на что / откуда)")
    tx_amount = st.number_input("Сумма (₽)", min_value=0.0, step=100.0)
    btn_submit = st.form_submit_button("Сохранить в базу")

    if btn_submit and tx_amount > 0:
        cat_code = tx_cat.split()[0]
        month_str = pd.to_datetime(tx_date).strftime('%b')
        new_row = pd.DataFrame([{
            "Дата": str(tx_date), "Тип": tx_type, "Категория": cat_code,
            "Описание": tx_desc, "Сумма": tx_amount, "Месяц": month_str
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("Успешно сохранено!")

# --- ШАПКА ---
st.caption("СРЕДА УПРАВЛЕНИЯ — СЕНТЯБРЬ 2026")
st.title("Добрый день, Талгат 👋")

inc_df = df[df['Тип'] == 'Доход']
exp_df = df[df['Тип'] == 'Расход']

total_inc = inc_df['Сумма'].sum()
total_exp = exp_df['Сумма'].sum()
net_capital = total_inc - total_exp
avg_inc = total_inc / 5 if len(inc_df) > 0 else 67195
avg_exp = total_exp / 5 if len(exp_df) > 0 else 63245
savings_rate = round(((avg_inc - avg_exp) / avg_inc) * 100, 1) if avg_inc > 0 else 0.0

st.markdown(f"""
<div class="hero-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="muted-text">ЧИСТЫЙ КАПИТАЛ</div>
            <div style="font-size: 2.5rem; font-weight: bold; margin: 8px 0;">{net_capital:,.0f} ₽</div>
            <div class="muted-text">ликвидный резерв + накопленный результат</div>
        </div>
        <div style="text-align: right;">
            <div class="green-text" style="font-size: 1.1rem; font-weight: bold;">+17 797 ₽ за месяц</div>
            <div class="muted-text" style="margin-top: 15px;">Деньги — это ресурс для развития</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_autonomy, col_m1, col_m2 = st.columns([1.2, 1, 1])

with col_autonomy:
    st.markdown("""
    <div class="metric-card">
        <div class="muted-text">ФИНАНСОВАЯ АВТОНОМИЯ</div>
        <div style="font-size: 0.85rem; margin-bottom: 10px;">Сколько месяцев можно жить без нового дохода</div>
    """, unsafe_allow_html=True)
    months_autonomy = round((net_capital / avg_exp), 1) if avg_exp > 0 and net_capital > 0 else 0.3
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=months_autonomy,
        number={'suffix': " мес", 'font': {'color': '#8ef552', 'size': 24}},
        gauge={
            'axis': {'range': [0, 12], 'tickwidth': 1, 'tickcolor': "#1a332a"},
            'bar': {'color': "#8ef552"},
            'bgcolor': "#0c1512",
            'bordercolor': "#1a332a"
        }
    ))
    fig_gauge.update_layout(height=120, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown("<div class='muted-text'>Цель до конца года — 3.0 месяца</div></div>", unsafe_allow_html=True)

with col_m1:
    st.markdown(f"""
    <div class="metric-card" style="height: 100%;">
        <div class="muted-text">СРЕДНИЙ ДОХОД ↗</div>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 10px 0;">{avg_inc / 1000:.1f} тыс. ₽</div>
        <div class="muted-text">расчет за 5 месяцев</div>
        <hr style="border-color: #1a332a; margin: 15px 0;">
        <div class="muted-text">НОРМА СБЕРЕЖЕНИЙ ⚡</div>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 10px 0;" class="green-text">{savings_rate}%</div>
        <div class="muted-text">цель: не менее 20%</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card" style="height: 100%;">
        <div class="muted-text">СРЕДНИЙ BURN RATE ↘</div>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 10px 0;">{avg_exp / 1000:.1f} тыс. ₽</div>
        <div class="muted-text">расходы за месяц</div>
        <hr style="border-color: #1a332a; margin: 15px 0;">
        <div class="muted-text">НАЙДЕНО УТЕЧЕК ⚡</div>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 10px 0; color: #ff5555;">13.5 тыс. ₽</div>
        <div class="muted-text">можно вернуть в капитал</div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("Доход против расхода")
monthly_summary = df.groupby(['Месяц', 'Тип'])['Сумма'].sum().unstack(fill_value=0).reset_index()
months_order = ['Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен']
monthly_summary['Месяц'] = pd.Categorical(monthly_summary['Месяц'], categories=months_order, ordered=True)
monthly_summary = monthly_summary.sort_values('Месяц')

fig_bar = go.Figure()
if 'Доход' in monthly_summary.columns:
    fig_bar.add_trace(
        go.Bar(x=monthly_summary['Месяц'], y=monthly_summary['Доход'], name='Доход', marker_color='#1d382e'))
if 'Расход' in monthly_summary.columns:
    fig_bar.add_trace(
        go.Bar(x=monthly_summary['Месяц'], y=monthly_summary['Расход'], name='Расход', marker_color='#8ef552'))

fig_bar.update_layout(
    barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#83998f'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=30, b=0), height=280
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["🏛️ Архитектура и Лимиты", "🎯 Охота на утечки", "📋 Журнал операций"])

with tab1:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Структура трат по уровням")
        cat_df = exp_df.groupby('Категория')['Сумма'].sum().reset_index()
        st.dataframe(cat_df, use_container_width=True)
    with col_t2:
        st.subheader("Бюджет-конституция (Лимиты)")
        st.write("**Недельный лимит 'на руки':** `2 250 ₽` в неделю.")
        limits_data = [
            {"Категория": "Фастфуд / Кафе", "Было": "5 000 ₽", "Лимит": "2 000 ₽", "Эффект": "+3 000 ₽"},
            {"Категория": "Такси / Самокаты", "Было": "6 000 ₽", "Лимит": "2 000 ₽", "Эффект": "+4 000 ₽"},
            {"Категория": "Цифровые донаты", "Было": "1 500 ₽", "Лимит": "0 ₽", "Эффект": "+1 500 ₽"}
        ]
        st.table(pd.DataFrame(limits_data))

with tab2:
    st.subheader("Охота на утечки (LEAK)")
    leaks = pd.DataFrame([
        {"Утечка": "Аренда самокатов", "₽/мес": 4367, "₽/ГОД": 52404,
         "Конкретное действие": "Удалить приложения Whoosh/Юрент", "Приоритет": 1},
        {"Утечка": "Спонтанный фастфуд", "₽/мес": 8638, "₽/ГОД": 103656,
         "Конкретное действие": "Перекусы с собой, лимит 2к", "Приоритет": 1},
        {"Утечка": "Игровые донаты", "₽/мес": 1500, "₽/ГОД": 18000,
         "Конкретное действие": "Отвязать карту от аккаунтов", "Приоритет": 2}
    ])
    st.dataframe(leaks, use_container_width=True)

with tab3:
    st.subheader("История всех записей")
    st.dataframe(df.sort_values(by="Дата", ascending=False), use_container_width=True)
