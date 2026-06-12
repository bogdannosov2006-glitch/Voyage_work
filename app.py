import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# ---------- Конфигурация Supabase ----------
SUPABASE_URL = "https://pidvreatfpmwqtuapthy.supabase.co"
SUPABASE_KEY = "sb_publishable_sPvLakingoiqo7y9d11R0Q_0aKDn5r0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_EMAIL = "tokt2918@gmail.com"   # ← теперь твоя почта

# ---------- Настройка страницы ----------
st.set_page_config(page_title="Трейдерский воркспейс", layout="wide")

# ---------- Функции работы с облаком ----------
def sign_up(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

def sign_in(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def load_trades(user_id):
    data = supabase.table("trades").select("*").eq("user_id", user_id).order("datetime", desc=True).execute()
    return data.data if data.data else []

def add_trade(trade, user_id):
    trade["user_id"] = user_id
    supabase.table("trades").insert(trade).execute()

def delete_trades(user_id):
    supabase.table("trades").delete().eq("user_id", user_id).execute()

def load_notes(user_id):
    data = supabase.table("notes").select("content").eq("user_id", user_id).execute()
    return data.data[0]["content"] if data.data else ""

def save_notes(content, user_id):
    existing = supabase.table("notes").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("notes").update({"content": content}).eq("user_id", user_id).execute()
    else:
        supabase.table("notes").insert({"user_id": user_id, "content": content}).execute()

def load_news():
    data = supabase.table("news").select("*").order("time").execute()
    return data.data if data.data else []

def add_news(news_item):
    supabase.table("news").insert(news_item).execute()

def delete_news(news_id):
    supabase.table("news").delete().eq("id", news_id).execute()

# ---------- Состояние сессии ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "trades" not in st.session_state:
    st.session_state.trades = []
if "notes" not in st.session_state:
    st.session_state.notes = ""

# ---------- Экран входа / регистрации ----------
if st.session_state.user is None:
    st.title("🔐 Вход в Трейдерский воркспейс")
    auth_mode = st.radio("Режим", ["Вход", "Регистрация"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")
    
    if auth_mode == "Вход":
        if st.button("Войти"):
            try:
                res = sign_in(email, password)
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка входа: {e}")
    else:
        if st.button("Зарегистрироваться"):
            try:
                res = sign_up(email, password)
                st.session_state.user = res.user
                st.success("Регистрация успешна! Добро пожаловать.")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка регистрации: {e}")
    st.stop()

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================
user = st.session_state.user
user_id = user.id
is_admin = (user.email == ADMIN_EMAIL)

# Загрузка данных
if not st.session_state.trades:
    st.session_state.trades = load_trades(user_id)
if not st.session_state.notes:
    st.session_state.notes = load_notes(user_id)

# ---------- Боковое меню ----------
st.sidebar.title(f"👤 {user.email}")
pages = ["📒 Журнал", "📊 Аналитика", "📝 Заметки", "📅 Календарь"]
if is_admin:
    pages.append("⚙️ Админка новостей")
page = st.sidebar.radio("📂 Разделы", pages)
if st.sidebar.button("🚪 Выйти"):
    st.session_state.user = None
    st.session_state.trades = []
    st.session_state.notes = []
    st.rerun()

st.title("📊 Трейдерский воркспейс")

# ==================== ЖУРНАЛ ====================
if page == "📒 Журнал":
    st.header("📒 Журнал сделок")
    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_date = st.date_input("Дата", datetime.now().date())
            trade_time = st.time_input("Время", datetime.now().time())
            instrument = st.text_input("Инструмент", "EURUSD")
            direction = st.selectbox("Направление", ["Long", "Short"])
        with col2:
            entry = st.number_input("Цена входа", step=0.00001, format="%.5f")
            exit_price = st.number_input("Цена выхода", step=0.00001, format="%.5f")
            volume = st.number_input("Объём (лоты)", step=0.01, format="%.2f", value=1.0)
        with col3:
            pnl = st.number_input("P/L", step=0.01, format="%.2f")
            comment = st.text_area("Комментарий")
        submitted = st.form_submit_button("➕ Добавить сделку")
        if submitted:
            trade = {
                "datetime": datetime.combine(trade_date, trade_time).isoformat(),
                "instrument": instrument,
                "direction": direction,
                "entry": entry,
                "exit": exit_price,
                "volume": volume,
                "pnl": pnl,
                "comment": comment
            }
            add_trade(trade, user_id)
            st.session_state.trades = load_trades(user_id)
            st.success("Сделка добавлена!")

    if st.session_state.trades:
        st.subheader("📋 Все сделки")
        df = pd.DataFrame(st.session_state.trades)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values("datetime", ascending=False)
        st.dataframe(df, use_container_width=True)
        if st.button("🗑️ Очистить журнал"):
            delete_trades(user_id)
            st.session_state.trades = []
            st.rerun()
    else:
        st.info("Сделок пока нет.")

# ==================== АНАЛИТИКА ====================
elif page == "📊 Аналитика":
    st.header("📊 Аналитика сделок")
    if not st.session_state.trades:
        st.info("Добавьте сделки в журнале, чтобы увидеть аналитику.")
    else:
        df = pd.DataFrame(st.session_state.trades)
        df['datetime'] = pd.to_datetime(df['datetime'])
        total_pnl = df['pnl'].sum()
        win_rate = (df['pnl'] > 0).mean() * 100
        avg_pnl = df['pnl'].mean()
        max_pnl = df['pnl'].max()
        min_pnl = df['pnl'].min()
        count = len(df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Всего сделок", count)
        col2.metric("Общий P/L", f"{total_pnl:.2f}")
        col3.metric("Винрейт", f"{win_rate:.1f}%")
        col4.metric("Средний P/L", f"{avg_pnl:.2f}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Макс. P/L", f"{max_pnl:.2f}")
        col2.metric("Мин. P/L", f"{min_pnl:.2f}")
        col3.metric("Прибыльные", f"{(df['pnl'] > 0).sum()} / {count}")

        st.subheader("📈 Кривая доходности (Equity)")
        df_sorted = df.sort_values("datetime")
        df_sorted['equity'] = df_sorted['pnl'].cumsum()
        fig = px.line(df_sorted, x='datetime', y='equity', title='Рост баланса', markers='o')
        fig.update_layout(xaxis_title='Дата', yaxis_title='Накопленный P/L')
        st.plotly_chart(fig, use_container_width=True)

# ==================== ЗАМЕТКИ ====================
elif page == "📝 Заметки":
    st.header("📝 Заметки")
    notes = st.text_area("Редактор (Markdown)", value=st.session_state.notes, height=300)
    st.session_state.notes = notes
    if st.button("💾 Сохранить заметки"):
        save_notes(notes, user_id)
        st.success("Сохранено!")
    st.subheader("👁️ Предпросмотр")
    if notes:
        st.markdown(notes)
    else:
        st.info("Начните писать. Markdown поддерживается.")

# ==================== КАЛЕНДАРЬ (для всех) ====================
elif page == "📅 Календарь":
    st.header("📅 Экономический календарь")
    news_items = load_news()
    if not news_items:
        st.info("Пока нет новостей.")
    else:
        now = datetime.now()
        future = [n for n in news_items if pd.to_datetime(n['time']) > now]
        future.sort(key=lambda x: x['time'])
        if future:
            next_event = future[0]
            delta = pd.to_datetime(next_event['time']) - now
            mins, secs = divmod(int(delta.total_seconds()), 60)
            hours, mins = divmod(mins, 60)
            timer_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            st.markdown("### ⏳ Ближайшая новость")
            c1, c2 = st.columns([2, 1])
            c1.markdown(f"""
            **{next_event['event']}** ({next_event['currency']})  
            🕒 {pd.to_datetime(next_event['time']).strftime('%Y-%m-%d %H:%M')}  
            🔴 Важность: {next_event['importance']}
            """)
            if delta.total_seconds() < 900:
                c2.warning(f"⚠️ Осталось: {timer_str}")
            else:
                c2.info(f"До события: {timer_str}")
        else:
            st.info("Все новости уже прошли.")

        st.subheader("📆 Все новости")
        df = pd.DataFrame(news_items)
        df['time'] = pd.to_datetime(df['time'])
        st.dataframe(df.sort_values("time"), use_container_width=True)

# ==================== АДМИНКА НОВОСТЕЙ (только админ) ====================
elif page == "⚙️ Админка новостей" and is_admin:
    st.header("⚙️ Администрирование новостей")
    with st.form("news_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            news_time = st.datetime_input("Дата и время")
            currency = st.text_input("Валюта", "USD")
        with col2:
            event = st.text_input("Событие", "Non-Farm Payrolls")
            importance = st.selectbox("Важность", ["High", "Medium", "Low"])
        if st.form_submit_button("➕ Добавить новость"):
            add_news({
                "time": news_time.isoformat(),
                "currency": currency,
                "event": event,
                "importance": importance
            })
            st.success("Новость добавлена!")
            st.rerun()

    news_items = load_news()
    if news_items:
        st.subheader("Существующие новости")
        for n in news_items:
            cols = st.columns([4, 1])
            cols[0].write(f"🕒 {n['time']} — {n['event']} ({n['currency']}) [{n['importance']}]")
            if cols[1].button("🗑️", key=f"del_{n['id']}"):
                delete_news(n['id'])
                st.rerun()