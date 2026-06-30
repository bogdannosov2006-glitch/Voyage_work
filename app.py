"""
Voyage Mind – полная версия.
Тёмный экран входа, лимит фонов 5 МБ, прямоугольники непрозрачные.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, time as dt_time
from supabase import create_client, Client
import os
import base64
import calendar
import json
from io import BytesIO
from typing import Optional

# ---------- Конфигурация Supabase ----------
SUPABASE_URL = "https://pidvreatfpmwqtuapthy.supabase.co"
SUPABASE_KEY = "sb_publishable_sPvLakingoiqo7y9d11R0Q_0aKDn5r0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_EMAIL = "tokt2918@gmail.com"

# ---------- Настройка страницы ----------
st.set_page_config(page_title="Voyage Mind", layout="wide")

# ---------- Локализация ----------
LOCALES = {
    "ru": {
        "title": "Voyage Mind", "dashboard": "📊 Статистика", "login": "Вход", "register": "Регистрация",
        "email": "Email", "password": "Пароль", "remember": "Запомнить меня", "login_btn": "Войти",
        "register_btn": "Зарегистрироваться", "nickname": "Никнейм", "trade_journal": "📒 Журнал сделок",
        "accounts": "💼 Аккаунты", "calc": "🧮 Калькулятор", "notes": "📝 Заметки",
        "news": "📅 Новости", "knowledge_base": "📚 База знаний", "settings": "⚙️ Настройки",
        "admin_news": "🔧 Админка", "logout": "🚪 Выйти", "add_trade": "➕ Добавить сделку",
        "clear_journal": "🗑️ Очистить журнал", "no_trades": "Сделок пока нет.",
        "export_csv": "📥 CSV", "screenshots": "Скриншоты", "emotion": "Эмоция",
        "confidence": "Уверенность", "stress": "Стресс", "add_psychology": "Психология",
        "time_entry": "Время входа (ЧЧ:ММ)", "time_exit": "Время выхода (ЧЧ:ММ)",
        "take_profit": "Тейк-профит", "stop_loss": "Стоп-лосс",
        "profile_tab": "👤 Профиль", "backgrounds_tab": "🎨 Фоны",
    },
    "en": {
        "title": "Voyage Mind", "dashboard": "📊 Statistics", "login": "Login", "register": "Register",
        "email": "Email", "password": "Password", "login_btn": "Log in", "register_btn": "Sign up",
        "nickname": "Nickname", "trade_journal": "📒 Trade Journal", "accounts": "💼 Accounts",
        "calc": "🧮 Calculator", "notes": "📝 Notes", "news": "📅 News",
        "knowledge_base": "📚 Knowledge Base", "settings": "⚙️ Settings", "admin_news": "🔧 Admin",
        "logout": "🚪 Log out", "add_trade": "➕ Add Trade", "clear_journal": "🗑️ Clear Journal",
        "no_trades": "No trades yet.", "export_csv": "📥 CSV", "screenshots": "Screenshots",
        "emotion": "Emotion", "confidence": "Confidence", "stress": "Stress",
        "add_psychology": "Psychology", "time_entry": "Entry time", "time_exit": "Exit time",
        "take_profit": "Take Profit", "stop_loss": "Stop Loss",
        "profile_tab": "👤 Profile", "backgrounds_tab": "🎨 Backgrounds",
    }
}

def t(key):
    return LOCALES.get(st.session_state.get("lang", "ru"), LOCALES["ru"]).get(key, key)

# ---------- Состояние сессии ----------
for k, v in {
    "user": None, "trades": [], "note_cards": [], "accounts": [],
    "current_page": "📊 Статистика", "auth_screen": "login", "remembered_email": "",
    "lang": "ru", "active_account_id": None,
    "sidebar_bg": None, "main_bg": None, "login_bg": None, "public_login_bg": None,
    "profile_loaded": False, "app_setting_loaded": False, "trades_loaded": False,
}.items():
    if k not in st.session_state: st.session_state[k] = v

# ---------- Функции ----------
def sign_up(email, password): return supabase.auth.sign_up({"email": email, "password": password})
def sign_in(email, password): return supabase.auth.sign_in_with_password({"email": email, "password": password})

def safe_call(func, default=[]):
    try: return func()
    except: return default

def load_trades_once(user_id):
    if not st.session_state.trades_loaded:
        st.session_state.trades = safe_call(lambda: supabase.table("trades").select("*").eq("user_id", user_id).order("entry_datetime", desc=True).execute().data, [])
        st.session_state.trades_loaded = True

def add_trade(trade, user_id):
    trade["user_id"] = user_id
    if "take_profit" in trade: trade["take_profit"] = 1 if trade["take_profit"] else 0
    if "stop_loss" in trade: trade["stop_loss"] = 1 if trade["stop_loss"] else 0
    try: supabase.table("trades").insert(trade).execute()
    except: pass
    st.session_state.trades.insert(0, trade)

def delete_trades(user_id):
    supabase.table("trades").delete().eq("user_id", user_id).execute()
    st.session_state.trades = []

@st.cache_data(ttl=30)
def load_note_cards(user_id): return safe_call(lambda: supabase.table("note_cards").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data, [])

def save_note_card(title, content, user_id):
    supabase.table("note_cards").insert({"user_id": user_id, "title": title, "content": content, "created_at": datetime.now().isoformat()}).execute()
    load_note_cards.clear()

def delete_note_card(note_id): supabase.table("note_cards").delete().eq("id", note_id).execute(); load_note_cards.clear()

@st.cache_data(ttl=30)
def load_news(): return safe_call(lambda: supabase.table("news").select("*").order("time").execute().data, [])

def add_news(news_item): supabase.table("news").insert(news_item).execute(); load_news.clear()
def delete_news(news_id): supabase.table("news").delete().eq("id", news_id).execute(); load_news.clear()

@st.cache_data(ttl=30)
def load_accounts(user_id): return safe_call(lambda: supabase.table("accounts").select("*").eq("user_id", user_id).order("created_at").execute().data, [])

def create_account(user_id, name, acc_type, initial_balance, daily_loss_limit=None):
    data = {"user_id": user_id, "name": name, "type": acc_type, "initial_balance": initial_balance}
    if daily_loss_limit: data["daily_loss_limit"] = daily_loss_limit
    supabase.table("accounts").insert(data).execute(); load_accounts.clear()

def parse_time_input(txt: str) -> Optional[dt_time]:
    txt = txt.strip()
    if not txt: return None
    digits = ''.join(filter(str.isdigit, txt))
    if not digits: raise ValueError("Нет цифр")
    if len(digits) == 4: h, m = int(digits[:2]), int(digits[2:])
    elif len(digits) == 3: h, m = int(digits[0]), int(digits[1:])
    elif len(digits) <= 2: h, m = int(digits), 0
    else: raise ValueError("Слишком много цифр")
    if not (0 <= h <= 23 and 0 <= m <= 59): raise ValueError(f"Некорректное время: {h:02d}:{m:02d}")
    return dt_time(h, m)

def safe_parse_date(val):
    if val is None or pd.isna(val): return pd.NaT
    try: return pd.to_datetime(val, errors='coerce')
    except: return pd.NaT

def load_profile_once():
    if not st.session_state.profile_loaded and st.session_state.user:
        data = safe_call(lambda: supabase.table("profiles").select("*").eq("user_id", st.session_state.user.id).execute().data, None)
        if isinstance(data, list) and data:
            p = data[0]
            st.session_state.sidebar_bg = p.get("sidebar_bg_base64"); st.session_state.main_bg = p.get("main_bg_base64")
            st.session_state.login_bg = p.get("login_bg_base64"); st.session_state.avatar_base64 = p.get("avatar_base64")
            st.session_state.nickname = p.get("nickname")
        else: st.session_state.avatar_base64 = None; st.session_state.nickname = None
        st.session_state.profile_loaded = True

def load_app_setting_once():
    if not st.session_state.app_setting_loaded:
        data = safe_call(lambda: supabase.table("app_settings").select("*").eq("id", 1).execute().data, None)
        if isinstance(data, list) and data: st.session_state.public_login_bg = data[0].get("login_bg_base64")
        st.session_state.app_setting_loaded = True

# ---------- Экран входа (ТЁМНЫЙ) ----------
if st.session_state.user is None:
    load_app_setting_once()
    
    login_bg = f".stApp{{background-image:url(data:image/png;base64,{st.session_state.public_login_bg})!important;background-size:cover!important;background-position:center!important;}}" if st.session_state.public_login_bg else ""
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Roboto', sans-serif !important; color: #FFFFFF !important; }}
        .voyage-title {{ font-family: 'Playfair Display', serif; font-size: 3.2rem; font-weight: 700; color: #FFFFFF; text-align: center; margin: 0.5rem 0; text-shadow: 0 0 20px rgba(56,189,248,0.5); }}
        .stApp {{ background-color: #0D1117 !important; }}
        {login_bg}
        .stApp::before {{ content:""; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:0; pointer-events:none; }}
        .stApp > * {{ position:relative; z-index:1; }}
        input, button {{ border-radius: 8px !important; }}
        input {{ background-color: #161B22 !important; color: #FFFFFF !important; border: 1px solid #30363D !important; }}
        label, p, div {{ color: #FFFFFF !important; }}
    </style>
    """, unsafe_allow_html=True)
    
    _, c, _ = st.columns([1,2,1])
    with c:
        st.markdown("<br><br><div class='voyage-title'>VOYAGE MIND</div><br>", unsafe_allow_html=True)
        if st.session_state.auth_screen == "login":
            with st.form("lf"):
                e = st.text_input("Email", st.session_state.remembered_email); p = st.text_input("Пароль", type="password")
                if st.form_submit_button("Войти"):
                    try:
                        r = sign_in(e, p); st.session_state.user = r.user
                        st.session_state.profile_loaded = False; st.session_state.trades_loaded = False
                        st.session_state.current_page = "📊 Статистика"; st.rerun()
                    except Exception as ex: st.error(str(ex))
            if st.button("Регистрация", key="tr"): st.session_state.auth_screen = "register"; st.rerun()
        else:
            with st.form("rf"):
                e = st.text_input("Email"); n = st.text_input("Никнейм"); p = st.text_input("Пароль", type="password")
                if st.form_submit_button("Зарегистрироваться"):
                    if not n.strip(): st.error("Никнейм обязателен!")
                    else:
                        try:
                            r = sign_up(e, p); supabase.table("profiles").upsert({"user_id": r.user.id, "nickname": n}).execute()
                            st.session_state.user = r.user; st.session_state.profile_loaded = False
                            st.session_state.trades_loaded = False; st.session_state.current_page = "📊 Статистика"; st.rerun()
                        except Exception as ex: st.error(str(ex))
            if st.button("Вход", key="tl"): st.session_state.auth_screen = "login"; st.rerun()
    st.stop()

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================
user = st.session_state.user; user_id = user.id; is_admin = (user.email == ADMIN_EMAIL)
load_profile_once(); load_trades_once(user_id)
if not st.session_state.note_cards: st.session_state.note_cards = load_note_cards(user_id)
if not st.session_state.accounts: st.session_state.accounts = load_accounts(user_id)
avatar_base64 = st.session_state.get("avatar_base64"); nickname = st.session_state.get("nickname")

# ---------- CSS ----------
main_bg = f".stApp{{background-image:url(data:image/png;base64,{st.session_state.main_bg})!important;background-size:cover!important;background-position:center!important;background-attachment:fixed!important;}}" if st.session_state.main_bg else ""
sb_bg = f"section[data-testid=\"stSidebar\"]{{background-image:url(data:image/png;base64,{st.session_state.sidebar_bg})!important;background-size:cover!important;background-position:center!important;}}" if st.session_state.sidebar_bg else ""

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Roboto', sans-serif !important; color: #FFFFFF !important; }}
    .voyage-title {{ font-family: 'Playfair Display', serif; font-size: 3.2rem; font-weight: 700; color: #FFFFFF; text-align: center; margin: 0.5rem 0; text-shadow: 0 0 20px rgba(56,189,248,0.5); }}
    .stApp {{ background-color: #0D1117; }}
    {main_bg}
    .stApp::before {{ content:""; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(13,17,23,0.85); z-index:0; pointer-events:none; }}
    .stApp > * {{ position:relative; z-index:1; }}
    {sb_bg}
    section[data-testid="stSidebar"]::before {{ content:""; position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(13,17,23,0.7); z-index:0; pointer-events:none; }}
    section[data-testid="stSidebar"] > * {{ position:relative; z-index:1; }}
    [data-testid="stMetric"] {{ background-color: #161B22 !important; border-radius: 16px !important; padding: 18px 16px !important; border: 1px solid #2A3441 !important; box-shadow: 0 6px 16px rgba(0,0,0,0.4); color: #FFFFFF !important; }}
    .note-card, .trade-card, .account-card {{ background-color: #161B22 !important; border-radius: 16px; padding: 20px; border: 1px solid #2A3441; margin-bottom: 12px; color: #FFFFFF; box-shadow: 0 6px 16px rgba(0,0,0,0.4); }}
    [data-testid="stSidebar"] .stButton > button {{ width: 100%; border-radius: 10px; margin-bottom: 8px; padding: 12px 16px; background: rgba(22,27,34,0.8); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.1); }}
    [data-testid="stSidebar"] .stButton > button[type="primary"] {{ background: linear-gradient(135deg, #38BDF8, #2D8CF0) !important; color: #0D1117 !important; }}
    input, textarea, select {{ background-color: #161B22 !important; color: #FFFFFF !important; border: 1px solid #30363D !important; border-radius: 8px !important; }}
    .calendar-day {{ text-align: center; padding: 8px; border-radius: 6px; min-height: 60px; }}
    .calendar-day.green {{ background-color: rgba(0,200,150,0.2); }} .calendar-day.red {{ background-color: rgba(255,100,100,0.2); }} .calendar-day.today {{ border: 1px solid #38BDF8; }}
</style>
""", unsafe_allow_html=True)

# ---------- Боковое меню ----------
with st.sidebar:
    if avatar_base64: st.markdown(f'<img src="data:image/png;base64,{avatar_base64}" style="width:80px;height:80px;border-radius:50%;">', unsafe_allow_html=True)
    else:
        ni = (nickname or user.email.split("@")[0]); ini = "".join([p[0].upper() for p in ni.split(".") if p])[:2]
        st.markdown(f'<div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#38BDF8,#2D8CF0);color:#0D1117;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;">{ini}</div>', unsafe_allow_html=True)
    st.markdown(f"**{nickname or user.email}**"); st.markdown("---")
    an = {None: "Без аккаунта"}
    for a in st.session_state.accounts: an[a["id"]] = a["name"]
    sa = st.selectbox("Активный счёт", list(an.keys()), format_func=lambda x: an[x], index=list(an.keys()).index(st.session_state.active_account_id))
    if sa != st.session_state.active_account_id: st.session_state.active_account_id = sa; st.rerun()
    st.markdown("---")
    pages = ["📊 Статистика", "📒 Журнал сделок", "💼 Аккаунты", "🧮 Калькулятор", "📝 Заметки", "📅 Новости", "📚 База знаний", "⚙️ Настройки"]
    if is_admin: pages.append("🔧 Админка")
    for name in pages:
        if st.button(name, key=name, use_container_width=True, type="primary" if st.session_state.current_page == name else "secondary"):
            st.session_state.current_page = name; st.rerun()
    if st.button("🚪 Выйти", type="secondary"):
        for k in list(st.session_state.keys()): del st.session_state[k]; st.rerun()

st.markdown('<div class="voyage-title">VOYAGE MIND</div>', unsafe_allow_html=True)

# ==================== СТАТИСТИКА ====================
if st.session_state.current_page == "📊 Статистика":
    st.header("📊 Статистика")
    if not st.session_state.trades: st.info(t("no_trades"))
    else:
        stat_names = {None: "Все счета"}
        for a in st.session_state.accounts: stat_names[a["id"]] = a["name"]
        sel = st.selectbox("Счёт", list(stat_names.keys()), format_func=lambda x: stat_names[x],
                           index=list(stat_names.keys()).index(st.session_state.active_account_id) if st.session_state.active_account_id in stat_names else 0)
        df = pd.DataFrame([t for t in st.session_state.trades if not sel or t.get("account_id") == sel])
        acc = next((a for a in st.session_state.accounts if a["id"] == sel), None) if sel else None
        init_bal = float(acc["initial_balance"]) if acc and acc.get("initial_balance") else 0.0
        
        if df.empty: st.info("Нет сделок")
        else:
            df['entry_datetime'] = df['entry_datetime'].apply(safe_parse_date)
            df = df.dropna(subset=['entry_datetime']).sort_values('entry_datetime')
            df['equity'] = init_bal + df['pnl'].cumsum()
            tp = df['pnl'].sum(); wr = (df['pnl'] > 0).mean()*100
            pr = df[df['pnl'] > 0]['pnl']; lo = df[df['pnl'] < 0]['pnl']
            ap = pr.mean() if not pr.empty else 0; al = lo.mean() if not lo.empty else 0
            
            for cols, vals in [
                (st.columns(4), [("Общий P/L", f"{tp:.2f}"), ("Винрейт", f"{wr:.1f}%"), ("Сделок", len(df)), ("Баланс", f"{init_bal+tp:.2f}")]),
                (st.columns(4), [("Средний тейк", f"{ap:.2f}"), ("Средний лосс", f"{al:.2f}"), ("Прибыльных", f"{len(pr)}"), ("Убыточных", f"{len(lo)}")]),
            ]:
                for c, (l, v) in zip(cols, vals): c.metric(l, v)
            
            st.subheader("📈 График депозита")
            fig = px.line(df, x='entry_datetime', y='equity', template="plotly_dark")
            fig.add_hline(y=init_bal, line_dash="dash", line_color="gray"); st.plotly_chart(fig, use_container_width=True)
            st.download_button(t("export_csv"), df.to_csv(index=False).encode('utf-8'), 'trades.csv', 'text/csv')

# ==================== ЖУРНАЛ СДЕЛОК ====================
elif st.session_state.current_page == "📒 Журнал сделок":
    st.header("📒 Журнал сделок")
    with st.expander("➕ Добавить сделку", expanded=True):
        with st.form("tf", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            with c1: td = st.date_input("Дата", datetime.now().date()); et = st.text_input(t("time_entry"), datetime.now().strftime("%H:%M")); xt = st.text_input(t("time_exit"), ""); ins = st.text_input("Инструмент", "EURUSD")
            with c2: dr = st.selectbox("Направление", ["Long","Short"]); ta = st.selectbox("Аккаунт", [a["id"] for a in st.session_state.accounts], format_func=lambda x: next(a["name"] for a in st.session_state.accounts if a["id"]==x)) if st.session_state.accounts else None; en = st.number_input("Цена входа", step=0.00001, format="%.5f"); ex = st.number_input("Цена выхода", step=0.00001, format="%.5f")
            with c3: vo = st.number_input("Объём", step=0.01, format="%.2f", value=1.0); pn = st.number_input("P/L", step=0.01, format="%.2f"); cm = st.text_area("Комментарий"); tg = st.text_input("Теги")
            st.markdown("**Результат:**"); tp_ch = st.checkbox("✅ Тейк-профит"); sl_ch = st.checkbox("🛑 Стоп-лосс")
            sf = st.file_uploader(t("screenshots"), type=["jpg","jpeg","png"], accept_multiple_files=True)
            if st.checkbox(t("add_psychology")):
                pc1,pc2 = st.columns(2)
                with pc1: em = st.selectbox(t("emotion"), ["😊","😐","😟","😡","😴"]); cf = st.slider(t("confidence"),1,10,5)
                with pc2: sts = st.slider(t("stress"),1,10,5); pn2 = st.text_area("Заметка", height=68)
            else: em=cf=sts=pn2=None
            if st.form_submit_button("➕ Добавить"):
                try:
                    fet = parse_time_input(et)
                    if fet is None: st.error("Введите время входа"); st.stop()
                except ValueError as ve: st.error(str(ve)); st.stop()
                fex = parse_time_input(xt) if xt.strip() else None
                sc = [base64.b64encode(f.read()).decode() for f in sf] if sf else []
                trade = {"entry_datetime": datetime.combine(td, fet).isoformat(), "exit_datetime": datetime.combine(td, fex).isoformat() if fex else None,
                         "instrument": ins, "direction": dr, "entry": en, "exit": ex, "volume": vo, "pnl": pn,
                         "comment": cm, "tags": [t.strip() for t in tg.split(',') if t.strip()][:10],
                         "account_id": ta, "screenshots": sc, "emotion": em, "confidence": cf, "stress": sts, "psych_note": pn2,
                         "take_profit": 1 if tp_ch else 0, "stop_loss": 1 if sl_ch else 0}
                add_trade(trade, user_id); st.success("Сделка добавлена!"); st.rerun()

    if st.session_state.trades:
        df = pd.DataFrame(st.session_state.trades)
        df['entry_datetime'] = df['entry_datetime'].apply(safe_parse_date)
        df['exit_datetime'] = df['exit_datetime'].apply(safe_parse_date) if 'exit_datetime' in df.columns else pd.NaT
        if st.session_state.active_account_id: df = df[df['account_id'] == st.session_state.active_account_id]
        df = df.sort_values("entry_datetime", ascending=False)
        for _, tr in df.iterrows():
            di = "🟢" if tr['direction']=="Long" else "🔴"
            ts = ' '.join(tr.get('tags',[]))
            tps = ' '.join(['TP✅' if tr.get('take_profit') in [1,True] else '', 'SL🛑' if tr.get('stop_loss') in [1,True] else '']).strip()
            es = tr['entry_datetime'].strftime('%d.%m.%Y %H:%M') if pd.notna(tr['entry_datetime']) else '—'
            xs = tr['exit_datetime'].strftime('%d.%m.%Y %H:%M') if pd.notna(tr.get('exit_datetime')) else '—'
            with st.expander(f"{di} {es} | {tr['instrument']} {tr['direction']} | P/L: {tr['pnl']:.2f} {ts} {tps}"):
                if tr.get('screenshots'):
                    for i, img in enumerate(tr['screenshots'], 1): st.markdown(f'<a href="data:image/png;base64,{img}" download="screenshot_{i}.png">📥 Скриншот {i}: тык!</a>', unsafe_allow_html=True)
                st.write(f"Вход: {es} | Выход: {xs} | Объём: {tr['volume']} лотов")
        if st.button("🗑️ Очистить журнал"): delete_trades(user_id); st.rerun()
    else: st.info(t("no_trades"))

# ==================== АККАУНТЫ ====================
elif st.session_state.current_page == "💼 Аккаунты":
    st.header("💼 Аккаунты")
    with st.expander("➕ Создать аккаунт"):
        with st.form("af", clear_on_submit=True):
            an = st.text_input("Название"); at = st.selectbox("Тип", ["personal","prop"], format_func=lambda x: "Личный" if x=="personal" else "Проп")
            ai = st.number_input("Начальный баланс", step=100.0)
            if st.form_submit_button("Создать") and an.strip():
                create_account(user_id, an, at, ai); st.session_state.accounts = load_accounts(user_id); st.success("Создан!"); st.rerun()
    for a in st.session_state.accounts:
        ta = [t for t in st.session_state.trades if t.get("account_id")==a["id"]]
        bal = a["initial_balance"] + sum(t["pnl"] for t in ta)
        st.metric(a["name"], f"{bal:.2f} $", f"{len(ta)} сделок")

# ==================== КАЛЬКУЛЯТОР ====================
elif st.session_state.current_page == "🧮 Калькулятор":
    st.header("🧮 Калькулятор")
    pv = 10.0
    if st.radio("Тип", ["Личный","Проп"], horizontal=True) == "Проп": pv = 10 / st.number_input("Плечо", value=10)
    bal = st.number_input("Баланс", 10000.0); rp = st.number_input("Риск %", 1.0)
    sl = st.number_input("Стоп-лосс", 50); tp_val = st.number_input("Тейк-профит", 100)
    if sl > 0:
        lot = bal*(rp/100)/(sl*pv); c1,c2,c3,c4 = st.columns(4)
        c1.metric("Лоты", f"{lot:.2f}"); c2.metric("Риск", f"{bal*(rp/100):.2f}")
        c3.metric("Прибыль", f"{tp_val*pv*lot:.2f}"); c4.metric("R/R", f"1:{tp_val/sl:.1f}")

# ==================== ЗАМЕТКИ ====================
elif st.session_state.current_page == "📝 Заметки":
    st.header("📝 Заметки")
    with st.form("nf", clear_on_submit=True):
        if st.form_submit_button("➕ Добавить") and (ct := st.text_area("Текст", height=120)):
            save_note_card("", ct, user_id); st.session_state.note_cards = load_note_cards(user_id); st.rerun()
    for cd in st.session_state.note_cards:
        st.markdown(f"<div class='note-card'>{cd['content'][:200]}</div>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"d_{cd['id']}"): delete_note_card(cd['id']); st.rerun()

# ==================== НОВОСТИ ====================
elif st.session_state.current_page == "📅 Новости":
    st.header("📅 Новости")
    if nw := load_news(): st.dataframe(pd.DataFrame(nw).sort_values("time"), use_container_width=True)
    else: st.info("Пока нет новостей.")

# ==================== БАЗА ЗНАНИЙ ====================
elif st.session_state.current_page == "📚 База знаний":
    st.header("📚 База знаний")
    st.info("Раздел в разработке")

# ==================== НАСТРОЙКИ ====================
elif st.session_state.current_page == "⚙️ Настройки":
    st.header("⚙️ Настройки")
    tb1, tb2 = st.tabs([t("profile_tab"), t("backgrounds_tab")])
    with tb1:
        if avatar_base64: st.image(f"data:image/png;base64,{avatar_base64}", width=100)
        if st.button("Удалить аватар"): supabase.table("profiles").update({"avatar_base64":None}).eq("user_id",user_id).execute(); st.session_state.avatar_base64=None; st.rerun()
        if uf := st.file_uploader("Аватар (200 КБ)", type=["jpg","jpeg","png"]):
            if uf.size <= 200*1024: b64 = base64.b64encode(uf.read()).decode(); supabase.table("profiles").upsert({"user_id":user_id,"avatar_base64":b64}).execute(); st.session_state.avatar_base64=b64; st.rerun()
        with st.form("nick_f"):
            nk = st.text_input("Никнейм", nickname or "")
            if st.form_submit_button("Сохранить") and nk.strip(): supabase.table("profiles").upsert({"user_id":user_id,"nickname":nk}).execute(); st.session_state.nickname=nk; st.rerun()
        lg = st.selectbox("Язык", ["ru","en"], 0 if st.session_state.lang=="ru" else 1)
        if lg != st.session_state.lang: st.session_state.lang=lg; st.rerun()
    with tb2:
        for bg, key, name in [("sidebar_bg","sidebar","Боковое меню"),("main_bg","main","Рабочее пространство"),("login_bg","login","Страница входа")]:
            st.markdown(f"**{name}**")
            if st.session_state.get(bg):
                if st.button("Удалить", key=f"d_{key}"): supabase.table("profiles").update({f"{key}_bg_base64":None}).eq("user_id",user_id).execute(); st.session_state[bg]=None; st.rerun()
            if uf := st.file_uploader("Загрузить (до 5 МБ)", type=["jpg","jpeg","png"], key=f"u_{key}"):
                if uf.size > 5*1024*1024: st.error("Максимум 5 МБ!")
                else:
                    try: b64 = base64.b64encode(uf.read()).decode(); supabase.table("profiles").upsert({"user_id":user_id,f"{key}_bg_base64":b64}).execute(); st.session_state[bg]=b64; st.rerun()
                    except Exception as e: st.error(f"Ошибка: {e}")

# ==================== АДМИНКА ====================
elif st.session_state.current_page == "🔧 Админка" and is_admin:
    st.header("🔧 Админка")
    with st.form("news_f", clear_on_submit=True):
        nt = st.datetime_input("Дата"); cu = st.text_input("Валюта","USD"); ev = st.text_input("Событие"); im = st.selectbox("Важность",["High","Medium","Low"])
        if st.form_submit_button("Добавить"): add_news({"time":nt.isoformat(),"currency":cu,"event":ev,"importance":im}); st.rerun()
    for n in load_news():
        if st.button(f"🗑️ {n['time']} — {n['event']}", key=f"dn_{n['id']}"): delete_news(n['id']); st.rerun()
