import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase import create_client, Client
import os
import base64
import yfinance as yf
import calendar
import json
from io import BytesIO

# ---------- Конфигурация Supabase ----------
SUPABASE_URL = "https://pidvreatfpmwqtuapthy.supabase.co"
SUPABASE_KEY = "sb_publishable_sPvLakingoiqo7y9d11R0Q_0aKDn5r0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_EMAIL = "tokt2918@gmail.com"

# ---------- Прокси для yfinance (если задана переменная окружения YFINANCE_PROXY) ----------
proxy_url = os.getenv("YFINANCE_PROXY")
if proxy_url:
    session = yf.utils.get_session()
    session.proxies = {"http": proxy_url, "https": proxy_url}
    yf.shared._session = session
    yf.shared._session_treadsafe = session

# ---------- Настройка страницы ----------
st.set_page_config(page_title="Voyage Mind", layout="wide")

# ---------- Локализация ----------
LOCALES = {
    "ru": {
        "title": "Voyage Mind",
        "dashboard": "📊 Дашборд",
        "login": "Вход",
        "register": "Регистрация",
        "email": "Email",
        "password": "Пароль",
        "remember": "Запомнить меня",
        "login_btn": "Войти",
        "register_btn": "Зарегистрироваться",
        "nickname": "Никнейм (обязательно)",
        "trade_journal": "📒 Журнал сделок",
        "accounts": "💼 Аккаунты",
        "calc": "🧮 Калькулятор",
        "checklists": "📋 Чек-листы",
        "notes": "📝 Заметки",
        "news": "📅 Новости",
        "chart": "📈 График",
        "knowledge_base": "📚 База знаний",
        "profile": "👤 Профиль",
        "admin_news": "⚙️ Админка новостей",
        "logout": "🚪 Выйти",
        "add_trade": "➕ Добавить сделку",
        "clear_journal": "🗑️ Очистить журнал",
        "save_note": "💾 Сохранить заметки",
        "add_note": "➕ Добавить заметку",
        "edit": "✏️ Редактировать",
        "delete": "🗑️ Удалить",
        "cancel": "Отмена",
        "save": "Сохранить",
        "change_email": "📧 Изменить email",
        "change_password": "🔒 Изменить пароль",
        "change_nickname": "✏️ Изменить никнейм",
        "avatar": "🖼️ Аватар",
        "sidebar_bg": "🖼️ Фон бокового меню",
        "main_bg": "🖼️ Фон рабочего пространства",
        "login_bg": "🖼️ Фон страницы входа",
        "public_login_bg": "🌐 Общий фон страницы входа (для всех)",
        "language": "🌐 Язык",
        "price_alert": "🔔 Алерт на цену",
        "alert_symbol": "Инструмент",
        "alert_condition": "Условие",
        "alert_price": "Цена",
        "check_alert": "Проверить",
        "alert_triggered": "🎯 Алерт сработал!",
        "alert_not_triggered": "😴 Алерт не сработал. Текущая цена: ",
        "all_trades": "📋 Все сделки",
        "no_trades": "Сделок пока нет.",
        "no_news": "Пока нет новостей.",
        "no_materials": "Пока нет материалов.",
        "download": "Скачать",
        "open_material": "Открыть",
        "add_material": "➕ Добавить материал",
        "main_material": "Основной материал",
        "material_title": "Название",
        "material_description": "Краткое описание",
        "material_category": "Категория",
        "material_file": "PDF или другой файл",
        "material_preview": "Превью-изображение",
        "daily_loss_warning": "⚠️ Дневной убыток по счёту {account} достиг {loss} (лимит {limit})",
        "export_csv": "📥 Скачать CSV",
        "export_excel": "📥 Скачать Excel",
        "screenshots": "Скриншоты (до 5 шт., JPG/PNG)",
        "emotion": "Эмоция",
        "confidence": "Уверенность (1-10)",
        "stress": "Стресс (1-10)",
        "psych_note": "Заметка (психология)",
        "psychology_block": "🧠 Психология сделки",
        "full_text": "Полный текст",
        "version": "Версия",
        "add_psychology": "Добавить психологию",
        "profile_filter": "Профили",
        "calc_help_title": "📘 Как пользоваться калькулятором",
        "calc_help_text": """
        1. Выберите тип счёта (Личный или Проп).
        2. Укажите баланс счёта.
        3. Задайте процент риска на сделку (обычно 1-2%).
        4. Введите стоп-лосс в пунктах (расстояние от входа до стопа).
        5. Опционально укажите тейк-профит в пунктах.
        6. Расчёт происходит автоматически.
        7. Получите объём позиции (лоты), риск в валюте, потенциальную прибыль и соотношение Risk/Reward.

        **Для проп-счетов:**
        - При выборе типа «Проп» появляется поле «Кредитное плечо». Обычно проп-фирмы предоставляют плечо от 1:10 до 1:100, чаще это 1:100.
        - Цена пункта рассчитывается автоматически как `10 / Кредитное плечо` (стандартный лот равен 10 единицам базовой валюты).
        - Риск = (% риска / 100) * Баланс. Это сумма, которую вы готовы потерять в одной сделке.
        - Размер позиции (лоты) = Риск / (Стоп-лосс в пунктах * Цена пункта).
        - Пример: Баланс 100 000$, риск 1% (1000$), стоп-лосс 50 пунктов, плечо 100, цена пункта = 0.1$. Тогда лоты = 1000 / (50 * 0.1) = 200 лотов.
        """
    },
    "en": {
        "title": "Voyage Mind",
        "dashboard": "📊 Dashboard",
        "login": "Login",
        "register": "Register",
        "email": "Email",
        "password": "Password",
        "remember": "Remember me",
        "login_btn": "Log in",
        "register_btn": "Sign up",
        "nickname": "Nickname (required)",
        "trade_journal": "📒 Trade Journal",
        "accounts": "💼 Accounts",
        "calc": "🧮 Calculator",
        "checklists": "📋 Checklists",
        "notes": "📝 Notes",
        "news": "📅 News",
        "chart": "📈 Chart",
        "knowledge_base": "📚 Knowledge Base",
        "profile": "👤 Profile",
        "admin_news": "⚙️ Admin News",
        "logout": "🚪 Log out",
        "add_trade": "➕ Add Trade",
        "clear_journal": "🗑️ Clear Journal",
        "save_note": "💾 Save Notes",
        "add_note": "➕ Add Note",
        "edit": "✏️ Edit",
        "delete": "🗑️ Delete",
        "cancel": "Cancel",
        "save": "Save",
        "change_email": "📧 Change Email",
        "change_password": "🔒 Change Password",
        "change_nickname": "✏️ Change Nickname",
        "avatar": "🖼️ Avatar",
        "sidebar_bg": "🖼️ Sidebar Background",
        "main_bg": "🖼️ Workspace Background",
        "login_bg": "🖼️ Login Page Background",
        "public_login_bg": "🌐 Public Login Background",
        "language": "🌐 Language",
        "price_alert": "🔔 Price Alert",
        "alert_symbol": "Symbol",
        "alert_condition": "Condition",
        "alert_price": "Price",
        "check_alert": "Check",
        "alert_triggered": "🎯 Alert triggered!",
        "alert_not_triggered": "😴 Alert not triggered. Current price: ",
        "all_trades": "📋 All Trades",
        "no_trades": "No trades yet.",
        "no_news": "No news yet.",
        "no_materials": "No materials yet.",
        "download": "Download",
        "open_material": "Open",
        "add_material": "➕ Add Material",
        "main_material": "Main Material",
        "material_title": "Title",
        "material_description": "Short Description",
        "material_category": "Category",
        "material_file": "PDF or other file",
        "material_preview": "Preview Image",
        "daily_loss_warning": "⚠️ Daily loss for account {account} reached {loss} (limit {limit})",
        "export_csv": "📥 Download CSV",
        "export_excel": "📥 Download Excel",
        "screenshots": "Screenshots (up to 5, JPG/PNG)",
        "emotion": "Emotion",
        "confidence": "Confidence (1-10)",
        "stress": "Stress (1-10)",
        "psych_note": "Note (psychology)",
        "psychology_block": "🧠 Trade Psychology",
        "full_text": "Full Text",
        "version": "Version",
        "add_psychology": "Add Psychology",
        "profile_filter": "Profiles",
        "calc_help_title": "📘 How to use the calculator",
        "calc_help_text": """
        1. Choose account type (Personal or Prop).
        2. Enter account balance.
        3. Set risk percentage per trade (usually 1-2%).
        4. Input stop loss in pips.
        5. Optionally input take profit in pips.
        6. The calculation updates automatically.
        7. You get position size (lots), risk amount, potential profit, and Risk/Reward ratio.

        **For prop accounts:**
        - When selecting "Prop", leverage field appears. Prop firms usually offer leverage from 1:10 to 1:100, most commonly 1:100.
        - Pip value = 10 / Leverage (standard lot = 10 units of base currency).
        - Risk = (Risk % / 100) * Balance.
        - Lot size = Risk / (Stop Loss in pips * Pip value).
        - Example: Balance $100,000, risk 1% ($1,000), stop loss 50 pips, leverage 100, pip value = $0.1. Lot size = 1000 / (50 * 0.1) = 200 lots.
        """
    }
}

def t(key):
    lang = st.session_state.get("lang", "ru")
    return LOCALES[lang].get(key, key)

# ---------- Состояние сессии ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "trades" not in st.session_state:
    st.session_state.trades = []
if "note_cards" not in st.session_state:
    st.session_state.note_cards = []
if "accounts" not in st.session_state:
    st.session_state.accounts = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "📊 Дашборд"
if "auth_screen" not in st.session_state:
    st.session_state.auth_screen = "login"
if "remembered_email" not in st.session_state:
    st.session_state.remembered_email = ""
if "lang" not in st.session_state:
    st.session_state.lang = "ru"
if "active_account_id" not in st.session_state:
    st.session_state.active_account_id = None
if "selected_notion_page" not in st.session_state:
    st.session_state.selected_notion_page = None
if "selected_material" not in st.session_state:
    st.session_state.selected_material = None
if "selected_account" not in st.session_state:
    st.session_state.selected_account = None

# ---------- Функции работы с облаком ----------
def sign_up(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

def sign_in(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def safe_call(func, default=[]):
    try:
        return func()
    except Exception:
        return default

def load_trades(user_id):
    return safe_call(lambda: supabase.table("trades").select("*").eq("user_id", user_id).order("entry_datetime", desc=True).execute().data, [])

def add_trade(trade, user_id):
    trade["user_id"] = user_id
    supabase.table("trades").insert(trade).execute()

def delete_trades(user_id):
    supabase.table("trades").delete().eq("user_id", user_id).execute()

def load_note_cards(user_id):
    return safe_call(lambda: supabase.table("note_cards").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data, [])

def save_note_card(title, content, user_id):
    supabase.table("note_cards").insert({
        "user_id": user_id, "title": title, "content": content,
        "created_at": datetime.now().isoformat()
    }).execute()

def update_note_card(note_id, title, content):
    supabase.table("note_cards").update({"title": title, "content": content}).eq("id", note_id).execute()

def delete_note_card(note_id):
    supabase.table("note_cards").delete().eq("id", note_id).execute()

def load_news():
    return safe_call(lambda: supabase.table("news").select("*").order("time").execute().data, [])

def add_news(news_item):
    supabase.table("news").insert(news_item).execute()

def delete_news(news_id):
    supabase.table("news").delete().eq("id", news_id).execute()

def get_profile(user_id):
    data = safe_call(lambda: supabase.table("profiles").select("*").eq("user_id", user_id).execute().data, None)
    return data[0] if isinstance(data, list) and data else None

def get_app_setting():
    data = safe_call(lambda: supabase.table("app_settings").select("*").eq("id", 1).execute().data, None)
    return data[0] if isinstance(data, list) and data else None

def save_avatar_base64(user_id, b64):
    supabase.table("profiles").upsert({"user_id": user_id, "avatar_base64": b64}).execute()

def save_sidebar_bg_base64(user_id, b64):
    supabase.table("profiles").upsert({"user_id": user_id, "sidebar_bg_base64": b64}).execute()

def save_main_bg_base64(user_id, b64):
    supabase.table("profiles").upsert({"user_id": user_id, "main_bg_base64": b64}).execute()

def save_login_bg_base64(user_id, b64):
    supabase.table("profiles").upsert({"user_id": user_id, "login_bg_base64": b64}).execute()

def load_accounts(user_id):
    return safe_call(lambda: supabase.table("accounts").select("*").eq("user_id", user_id).order("created_at").execute().data, [])

def create_account(user_id, name, acc_type, initial_balance, target=None, phase=None, purchase_date=None, daily_loss_limit=None, profile=None):
    data = {"user_id": user_id, "name": name, "type": acc_type, "initial_balance": initial_balance}
    if target: data["target"] = target
    if phase: data["phase"] = phase
    if purchase_date: data["purchase_date"] = purchase_date.isoformat()
    if daily_loss_limit: data["daily_loss_limit"] = daily_loss_limit
    if profile: data["profile"] = profile
    supabase.table("accounts").insert(data).execute()

# Чек-листы
def load_checklist_templates(user_id):
    return safe_call(lambda: supabase.table("checklist_templates").select("*").eq("user_id", user_id).order("created_at").execute().data, [])

def create_checklist_template(user_id, title, items_json, days_json):
    supabase.table("checklist_templates").insert({
        "user_id": user_id, "title": title, "items": items_json, "days": days_json
    }).execute()

def delete_checklist_template(template_id):
    supabase.table("checklist_templates").delete().eq("id", template_id).execute()

def load_checklist_runs(user_id, template_id=None, run_date=None):
    query = supabase.table("checklist_runs").select("*").eq("user_id", user_id)
    if template_id: query = query.eq("template_id", template_id)
    if run_date: query = query.eq("run_date", run_date.isoformat())
    return safe_call(lambda: query.execute().data, [])

def save_checklist_run(user_id, template_id, run_date, items_status_json):
    existing = load_checklist_runs(user_id, template_id, run_date)
    if existing:
        supabase.table("checklist_runs").update({"items_status": items_status_json}).eq("id", existing[0]["id"]).execute()
    else:
        supabase.table("checklist_runs").insert({
            "user_id": user_id, "template_id": template_id, "run_date": run_date.isoformat(), "items_status": items_status_json
        }).execute()

# Учебные материалы
def load_learning_materials():
    return safe_call(lambda: supabase.table("learning_materials").select("*").order("created_at", desc=True).execute().data, [])

def add_learning_material(title, description, file_base64, file_name, category, preview_base64=None, full_text=None, version=None):
    supabase.table("learning_materials").insert({
        "title": title,
        "description": description,
        "file_base64": file_base64,
        "file_name": file_name,
        "category": category,
        "preview_base64": preview_base64,
        "full_text": full_text,
        "version": version
    }).execute()

def delete_learning_material(material_id):
    supabase.table("learning_materials").delete().eq("id", material_id).execute()

# ---------- Динамический CSS ----------
profile = None
main_bg = None
sidebar_bg = None
login_bg = None
public_login_bg = None
if st.session_state.user:
    profile = get_profile(st.session_state.user.id)
    if profile:
        sidebar_bg = profile.get("sidebar_bg_base64")
        main_bg = profile.get("main_bg_base64")
        login_bg = profile.get("login_bg_base64")
else:
    app_setting = get_app_setting()
    public_login_bg = app_setting["login_bg_base64"] if app_setting and app_setting.get("login_bg_base64") else None

main_bg_style = ".stApp { background-color: #0D1117; }"
if main_bg:
    main_bg_style = f"""
    .stApp {{
        background-image: url(data:image/png;base64,{main_bg});
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        position: relative;
    }}
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(13, 17, 23, 0.85);
        z-index: 0;
    }}
    .stApp > * {{ position: relative; z-index: 1; }}
    """

sidebar_bg_style = "section[data-testid=\"stSidebar\"] { background-color: #0D1117; }"
if sidebar_bg:
    sidebar_bg_style = f"""
    section[data-testid="stSidebar"] {{
        background-image: url(data:image/png;base64,{sidebar_bg});
        background-size: cover;
        background-position: center;
        position: relative;
    }}
    section[data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(13, 17, 23, 0.7);
        z-index: 0;
    }}
    section[data-testid="stSidebar"] > * {{ position: relative; z-index: 1; }}
    """

login_css = ".stApp { background-color: #0D1117; }"
if st.session_state.user is None:
    if public_login_bg:
        login_css = f"""
        .stApp {{
            background-image: url(data:image/png;base64,{public_login_bg}) !important;
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 0;
        }}
        .stApp > * {{ position: relative; z-index: 1; }}
        """
    elif login_bg:
        login_css = f"""
        .stApp {{
            background-image: url(data:image/png;base64,{login_bg}) !important;
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 0;
        }}
        .stApp > * {{ position: relative; z-index: 1; }}
        """

css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
    }}
    .voyage-title {{
        font-family: 'Caveat', cursive;
        font-size: 2.5rem;
        font-weight: 600;
        color: #FFFFFF;
        text-align: center;
        margin: 0.5rem 0;
    }}
    {"/* Стили для страницы входа */" if st.session_state.user is None else "/* Основные стили приложения */"}
    {login_css if st.session_state.user is None else main_bg_style}
    {"" if st.session_state.user is None else sidebar_bg_style}
    [data-testid="stMetric"] {{
        background-color: #161B22 !important;
        border-radius: 16px !important;
        padding: 18px 16px !important;
        border: 1px solid #2A3441 !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4), 0 0 0 1px rgba(56, 189, 248, 0.1) inset !important;
        color: #FFFFFF !important;
        transition: all 0.25s ease;
    }}
    [data-testid="stMetric"]:hover {{
        box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15), 0 0 0 1px rgba(56, 189, 248, 0.3) inset !important;
        transform: translateY(-2px);
    }}
    .note-card, .psychology-card {{
        background: #161B22;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #2A3441;
        margin-bottom: 16px;
        color: #FFFFFF;
    }}
    .pulse-red {{
        animation: pulse 1s infinite;
        background-color: #2D1A1A;
        border-left: 4px solid #F87171;
        padding: 16px;
        border-radius: 8px;
        color: #FECACA;
    }}
    @keyframes pulse {{
        0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }}
    }}
    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        border-radius: 10px;
        margin-bottom: 8px;
        padding: 12px 16px;
        font-size: 15px;
        font-weight: 500;
        transition: all 0.25s ease;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(22,27,34,0.6);
        backdrop-filter: blur(10px);
        color: #FFFFFF;
    }}
    [data-testid="stSidebar"] .stButton > button[type="primary"] {{
        background: linear-gradient(135deg, #38BDF8, #2D8CF0) !important;
        color: #0D1117 !important;
        border-color: transparent !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(56,189,248,0.3);
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(56,189,248,0.1);
        border-color: rgba(56,189,248,0.3);
    }}
    input, textarea, select {{
        background-color: #161B22 !important;
        color: #FFFFFF !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }}
    input:focus, textarea:focus, select:focus {{
        border-color: #38BDF8 !important;
        box-shadow: 0 0 0 1px #38BDF8 !important;
    }}
    .stDateInput > div > div > input, .stTimeInput > div > div > input {{
        background-color: #161B22 !important;
        color: #FFFFFF !important;
    }}
    [data-baseweb="select"] {{
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }}
    [data-baseweb="select"] > div {{ background-color: #161B22 !important; }}
    [data-baseweb="select"] [data-baseweb="tag"] {{
        background-color: #30363D !important;
        color: #FFFFFF !important;
    }}
    div[data-baseweb="popover"] {{
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
    }}
    div[data-baseweb="popover"] ul {{ background-color: #161B22 !important; }}
    div[data-baseweb="popover"] li {{ color: #FFFFFF !important; }}
    div[data-baseweb="popover"] li:hover {{ background-color: #30363D !important; }}
    .stDataFrame, .stTable {{
        background-color: #161B22 !important;
        border-radius: 12px;
        border: 1px solid #30363D;
    }}
    .stDataFrame th, .stTable th {{
        background-color: #0D1117 !important;
        color: #FFFFFF !important;
    }}
    .stDataFrame td, .stTable td {{
        background-color: #161B22 !important;
        color: #FFFFFF !important;
    }}
    .account-card, .checklist-card, .trade-card, .material-card, .notion-card {{
        background-color: #161B22;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #2A3441;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        transition: all 0.2s;
        color: #FFFFFF;
        margin-bottom: 12px;
    }}
    .account-card:hover, .checklist-card:hover, .trade-card:hover, .material-card:hover, .notion-card:hover {{
        border-color: #38BDF8;
        box-shadow: 0 6px 20px rgba(56,189,248,0.25);
    }}
    .calendar-day {{
        text-align: center;
        padding: 8px;
        border-radius: 6px;
        min-height: 60px;
    }}
    .calendar-day.green {{ background-color: rgba(0,200,150,0.2); }}
    .calendar-day.red {{ background-color: rgba(255,100,100,0.2); }}
    .calendar-day.today {{ border: 1px solid #38BDF8; }}
    .progress-bar {{
        width: 100%;
        background-color: #30363D;
        border-radius: 10px;
        height: 12px;
        margin: 8px 0;
        overflow: hidden;
    }}
    .progress-fill {{
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #4CAF50, #38BDF8);
        transition: width 0.3s ease;
    }}
    .tag-badge {{
        display: inline-block;
        background-color: #30363D;
        color: #FFFFFF;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-right: 4px;
    }}
    /* Стили для журнала сделок – раскрывающиеся карточки */
    .trade-expander .streamlit-expanderHeader {{
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
        transition: all 0.2s;
        color: #FFFFFF !important;
    }}
    .trade-expander .streamlit-expanderHeader:hover {{
        border-color: #38BDF8 !important;
        background-color: #1A2332 !important;
    }}
    .trade-expander .streamlit-expanderContent {{
        background-color: #0D1117;
        border: 1px solid #30363D;
        border-radius: 0 0 12px 12px;
        padding: 16px;
    }}
    /* Цветная полоса слева в зависимости от P/L */
    .trade-profit {{
        border-left: 4px solid #4CAF50 !important;
    }}
    .trade-loss {{
        border-left: 4px solid #F44336 !important;
    }}
    /* Стили для аккаунтов – большие карточки, похожие на дни календаря */
    .account-expander .streamlit-expanderHeader {{
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 18px 20px !important;
        font-size: 17px !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
        min-height: 70px;
        display: flex;
        align-items: center;
        color: #FFFFFF !important;
    }}
    .account-expander .streamlit-expanderHeader:hover {{
        border-color: #38BDF8 !important;
        background-color: #1A2332 !important;
    }}
    .account-expander .streamlit-expanderContent {{
        background-color: #0D1117;
        border: 1px solid #30363D;
        border-radius: 0 0 12px 12px;
        padding: 16px;
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Caps Lock
st.markdown("""<script>
document.addEventListener('DOMContentLoaded', function() {
    const pwd = document.querySelectorAll('input[type="password"]');
    pwd.forEach(i => i.addEventListener('keyup', e => {
        let w = document.getElementById('caps-warn');
        if (!w) { w = document.createElement('small'); w.id = 'caps-warn'; w.style.color='red'; w.style.display='none'; i.parentNode.appendChild(w); }
        w.style.display = e.getModifierState('CapsLock') ? 'block' : 'none';
        w.textContent = '⚠️ Caps Lock включён';
    }));
});
</script>""", unsafe_allow_html=True)

# ---------- Экран входа / регистрации ----------
if st.session_state.user is None:
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="voyage-title">⛵ VOYAGE MIND</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.auth_screen == "login":
            with st.form("login_form"):
                email = st.text_input(t("email"), value=st.session_state.remembered_email)
                pwd = st.text_input(t("password"), type="password")
                rem = st.checkbox(t("remember"))
                if st.form_submit_button(t("login_btn")):
                    try:
                        res = sign_in(email, pwd)
                        st.session_state.user = res.user
                        st.session_state.current_page = "📊 Дашборд"
                        if rem: st.session_state.remembered_email = email
                        else: st.session_state.remembered_email = ""
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {e}")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(t("register_btn"), key="to_reg"):
                st.session_state.auth_screen = "register"
                st.rerun()
        else:
            with st.form("register_form"):
                email = st.text_input(t("email"))
                nickname = st.text_input(t("nickname"))
                pwd = st.text_input(t("password"), type="password")
                rem = st.checkbox(t("remember"))
                if st.form_submit_button(t("register_btn")):
                    if not nickname.strip():
                        st.error("Никнейм обязателен!")
                    else:
                        try:
                            res = sign_up(email, pwd)
                            supabase.table("profiles").upsert({"user_id": res.user.id, "nickname": nickname}).execute()
                            st.session_state.user = res.user
                            st.session_state.current_page = "📊 Дашборд"
                            if rem: st.session_state.remembered_email = email
                            else: st.session_state.remembered_email = ""
                            st.success("Регистрация успешна!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка: {e}")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(t("login_btn"), key="to_log"):
                st.session_state.auth_screen = "login"
                st.rerun()
    st.stop()

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================
user = st.session_state.user
user_id = user.id
is_admin = (user.email == ADMIN_EMAIL)

if not st.session_state.trades:
    st.session_state.trades = load_trades(user_id)
if not st.session_state.note_cards:
    st.session_state.note_cards = load_note_cards(user_id)
if not st.session_state.accounts:
    st.session_state.accounts = load_accounts(user_id)

if not profile:
    profile = get_profile(user_id)
avatar_base64 = profile["avatar_base64"] if profile and profile.get("avatar_base64") else None
nickname = profile["nickname"] if profile and profile.get("nickname") else None

# ---------- Боковое меню ----------
with st.sidebar:
    if avatar_base64:
        st.markdown(f'<img src="data:image/png;base64,{avatar_base64}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;box-shadow:0 4px 10px rgba(56,189,248,0.3);">', unsafe_allow_html=True)
    else:
        name_for_initials = nickname or user.email.split("@")[0]
        initials = "".join([part[0].upper() for part in name_for_initials.split(".") if part])[:2]
        st.markdown(f"""<div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#38BDF8,#2D8CF0);color:#0D1117;
                    display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;box-shadow:0 4px 10px rgba(56,189,248,0.4);">{initials}</div>""", unsafe_allow_html=True)
    display_name = nickname if nickname else user.email
    st.markdown(f"**{display_name}**")
    st.markdown("---")

    acc_names = {None: "Без аккаунта"}
    for acc in st.session_state.accounts:
        acc_names[acc["id"]] = acc["name"]
    if "active_account_id" not in st.session_state:
        st.session_state.active_account_id = None
    selected_acc = st.selectbox(
        "Активный счёт",
        options=list(acc_names.keys()),
        format_func=lambda x: acc_names[x],
        index=list(acc_names.keys()).index(st.session_state.active_account_id)
    )
    if selected_acc != st.session_state.active_account_id:
        st.session_state.active_account_id = selected_acc
        st.rerun()

    active_acc = next((a for a in st.session_state.accounts if a["id"] == st.session_state.active_account_id), None)
    if active_acc and active_acc.get("daily_loss_limit"):
        today_trades = [tr for tr in st.session_state.trades if tr.get("account_id") == active_acc["id"] and pd.to_datetime(tr["entry_datetime"]).date() == date.today()]
        daily_pnl = sum(tr["pnl"] for tr in today_trades)
        limit = float(active_acc["daily_loss_limit"])
        if daily_pnl < -limit:
            st.error(t("daily_loss_warning").format(account=active_acc['name'], loss=abs(daily_pnl), limit=limit))

    st.markdown("---")
    pages = [
        "📊 Дашборд",
        "📒 Журнал сделок",
        "💼 Аккаунты",
        "🧮 Калькулятор",
        "📝 Заметки",
        "📅 Новости",
        "📈 График",
        "📚 База знаний",
        "👤 Профиль"
    ]
    if is_admin:
        pages.append("⚙️ Админка новостей")
    for name in pages:
        tpe = "primary" if st.session_state.current_page == name else "secondary"
        if st.button(name, key=name, use_container_width=True, type=tpe):
            st.session_state.current_page = name
            st.rerun()
    st.markdown("---")
    if st.button("🚪 Выйти", type="secondary"):
        st.session_state.user = None
        st.session_state.trades = []
        st.session_state.note_cards = []
        st.session_state.accounts = []
        st.rerun()

st.markdown('<div class="voyage-title">⛵ VOYAGE MIND</div>', unsafe_allow_html=True)

# ==================== ДАШБОРД ====================
if st.session_state.current_page == "📊 Дашборд":
    st.header("📊 Дашборд эффективности")
    if not st.session_state.trades:
        st.info("Нет сделок для отображения.")
    else:
        df = pd.DataFrame(st.session_state.trades)
        df['entry_datetime'] = pd.to_datetime(df['entry_datetime'])
        if st.session_state.active_account_id:
            df = df[df['account_id'] == st.session_state.active_account_id]
        if df.empty:
            st.info("Нет сделок по выбранному счёту.")
        else:
            total_pnl = df['pnl'].sum()
            win_rate = (df['pnl'] > 0).mean() * 100
            count = len(df)
            avg_pnl = df['pnl'].mean()
            best = df['pnl'].max()
            worst = df['pnl'].min()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Общий P/L", f"{total_pnl:.2f}")
            col2.metric("Винрейт", f"{win_rate:.1f}%")
            col3.metric("Средний P/L", f"{avg_pnl:.2f}")
            col4.metric("Сделок", count)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Лучшая", f"{best:.2f}")
            col2.metric("Худшая", f"{worst:.2f}")
            col3.metric("Прибыльных", f"{(df['pnl'] > 0).sum()}")
            col4.metric("Убыточных", f"{(df['pnl'] < 0).sum()}")

            st.subheader("📈 График эквити")
            df_sorted = df.sort_values('entry_datetime')
            df_sorted['equity'] = df_sorted['pnl'].cumsum()
            fig = px.line(df_sorted, x='entry_datetime', y='equity', template="plotly_dark")
            fig.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22", font=dict(color="#E6EDF3"))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📅 P/L по дням недели")
            df_sorted['dayofweek'] = df_sorted['entry_datetime'].dt.day_name()
            day_pnl = df_sorted.groupby('dayofweek')['pnl'].sum().reset_index()
            fig2 = px.bar(day_pnl, x='dayofweek', y='pnl', template="plotly_dark")
            fig2.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22", font=dict(color="#E6EDF3"))
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("Последние 5 сделок")
            recent = df.sort_values('entry_datetime', ascending=False).head(5)
            for idx, trade in recent.iterrows():
                pnl_color = "#4CAF50" if trade['pnl'] > 0 else "#F44336"
                st.markdown(f"""
                <div class="trade-card">
                    <h4>{trade['instrument']} <small>{trade['direction']}</small></h4>
                    <p><strong>Вход:</strong> {trade['entry_datetime'].strftime('%d.%m.%Y %H:%M')}</p>
                    <p><strong>P/L:</strong> <span style="color:{pnl_color}">{trade['pnl']:.2f}</span></p>
                </div>
                """, unsafe_allow_html=True)

            def fix_datetime(df_in):
                df_out = df_in.copy()
                for col in df_out.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
                    if hasattr(df_out[col].dtype, 'tz') and df_out[col].dt.tz is not None:
                        df_out[col] = df_out[col].dt.tz_convert(None)
                return df_out

            df_export = fix_datetime(df)
            st.download_button(
                label=t("export_csv"),
                data=df_export.to_csv(index=False).encode('utf-8'),
                file_name='trades.csv',
                mime='text/csv'
            )
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False)
            st.download_button(
                label=t("export_excel"),
                data=output.getvalue(),
                file_name='trades.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

# ==================== ЖУРНАЛ СДЕЛОК ====================
elif st.session_state.current_page == "📒 Журнал сделок":
    st.header("📒 Журнал сделок")
    with st.expander("➕ Добавить сделку", expanded=True):
        with st.form("trade_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                trade_date = st.date_input("Дата входа", datetime.now().date())
                entry_time = st.time_input("Время входа", datetime.now().time())
                exit_time = st.time_input("Время выхода", value=None)
                instrument = st.text_input("Инструмент", "EURUSD")
            with col2:
                direction = st.selectbox("Направление", ["Long", "Short"])
                if st.session_state.accounts:
                    trade_account = st.selectbox("Аккаунт", options=[a["id"] for a in st.session_state.accounts],
                                                 format_func=lambda x: next(a["name"] for a in st.session_state.accounts if a["id"] == x))
                else:
                    trade_account = None
                entry = st.number_input("Цена входа", step=0.00001, format="%.5f")
                exit_price = st.number_input("Цена выхода", step=0.00001, format="%.5f")
            with col3:
                volume = st.number_input("Объём (лоты)", step=0.01, format="%.2f", value=1.0)
                pnl = st.number_input("P/L", step=0.01, format="%.2f")
                comment = st.text_area("Комментарий")
                tags_input = st.text_input("Теги (через запятую)", placeholder="например: тренд, откат, новости")
                screenshot_files = st.file_uploader(t("screenshots"), type=["jpg","jpeg","png"], accept_multiple_files=True, key="screenshot_upload")

            # Психология по чекбоксу (по умолчанию выключено)
            add_psych = st.checkbox(t("add_psychology"), value=False)
            if add_psych:
                st.markdown("---")
                st.markdown(f"**{t('psychology_block')}**")
                col_psy1, col_psy2 = st.columns(2)
                with col_psy1:
                    emotion = st.selectbox(t("emotion"), ["😊 Отлично", "😐 Нормально", "😟 Тревожно", "😡 Злой", "😴 Устал"])
                    confidence = st.slider(t("confidence"), 1, 10, 5)
                with col_psy2:
                    stress = st.slider(t("stress"), 1, 10, 5)
                    psych_note = st.text_area(t("psych_note"), height=68)
            else:
                emotion = None
                confidence = None
                stress = None
                psych_note = None

            if st.form_submit_button("➕ Добавить сделку"):
                screenshots_b64 = []
                if screenshot_files:
                    total_size = sum(f.size for f in screenshot_files)
                    if total_size > 2 * 1024 * 1024:
                        st.error("Суммарный размер скриншотов не должен превышать 2 МБ.")
                        st.stop()
                    for file in screenshot_files:
                        if file.size > 500 * 1024:
                            st.error(f"Файл {file.name} слишком большой. Максимум 500 КБ на файл.")
                            st.stop()
                    for file in screenshot_files:
                        try:
                            b64 = base64.b64encode(file.read()).decode()
                            screenshots_b64.append(b64)
                        except Exception as e:
                            st.error(f"Ошибка загрузки {file.name}: {e}")
                            st.stop()
                tag_list = [tg.strip() for tg in tags_input.split(',') if tg.strip()][:10]
                trade = {
                    "entry_datetime": datetime.combine(trade_date, entry_time).isoformat(),
                    "exit_datetime": datetime.combine(trade_date, exit_time).isoformat() if exit_time else None,
                    "instrument": instrument,
                    "direction": direction,
                    "entry": entry,
                    "exit": exit_price,
                    "volume": volume,
                    "pnl": pnl,
                    "comment": comment,
                    "tags": tag_list,
                    "account_id": trade_account if trade_account else None,
                    "screenshots": screenshots_b64,
                    "emotion": emotion,
                    "confidence": confidence,
                    "stress": stress,
                    "psych_note": psych_note
                }
                add_trade(trade, user_id)
                st.session_state.trades = load_trades(user_id)
                st.success("Сделка добавлена!")

    if st.session_state.trades:
        st.subheader("📋 Все сделки")
        all_tags = set()
        for tr in st.session_state.trades:
            if tr.get("tags"):
                all_tags.update(tr["tags"])
        selected_tags = st.multiselect("🔍 Фильтр по тегам", sorted(all_tags))

        df = pd.DataFrame(st.session_state.trades)
        df['entry_datetime'] = pd.to_datetime(df['entry_datetime'])
        if 'exit_datetime' in df.columns:
            df['exit_datetime'] = pd.to_datetime(df['exit_datetime'])
        if st.session_state.active_account_id:
            df = df[df['account_id'] == st.session_state.active_account_id]
        if selected_tags:
            df = df[df['tags'].apply(lambda x: bool(set(x) & set(selected_tags)) if x else False)]
        df = df.sort_values("entry_datetime", ascending=False)

        # Компактные раскрывающиеся карточки
        for idx, trade in df.iterrows():
            pnl = trade['pnl']
            pnl_color = "#4CAF50" if pnl > 0 else "#F44336"
            direction_icon = "🟢" if trade['direction'] == "Long" else "🔴"
            tags_str = ' '.join([f'<span class="tag-badge">{tag}</span>' for tag in trade.get('tags', [])])
            exit_str = trade['exit_datetime'].strftime('%d.%m.%Y %H:%M') if pd.notnull(trade.get('exit_datetime')) else '—'
            label = f"{direction_icon} {trade['entry_datetime'].strftime('%d.%m.%Y %H:%M')} | {trade['instrument']} {trade['direction']} | P/L: {pnl:.2f} {tags_str}"
            pnl_class = "trade-profit" if pnl > 0 else "trade-loss"
            with st.expander(label, expanded=False):
                screenshots = trade.get('screenshots')
                if not screenshots and trade.get('screenshot_base64'):
                    screenshots = [trade['screenshot_base64']]
                if screenshots:
                    cols = st.columns(min(len(screenshots), 5))
                    for i, img_b64 in enumerate(screenshots):
                        cols[i % 5].markdown(
                            f'<a href="data:image/png;base64,{img_b64}" target="_blank"><img src="data:image/png;base64,{img_b64}" style="width:120px; cursor:pointer; margin:4px; border-radius:6px; border:1px solid #30363D;"></a>',
                            unsafe_allow_html=True
                        )
                if trade.get('emotion'):
                    psych_lines = []
                    psych_lines.append(f"Эмоция: {trade['emotion']}")
                    if trade.get('confidence'): psych_lines.append(f"Уверенность: {trade['confidence']}/10")
                    if trade.get('stress'): psych_lines.append(f"Стресс: {trade['stress']}/10")
                    if trade.get('psych_note'): psych_lines.append(f"Заметка: {trade['psych_note']}")
                    st.markdown("**Психология:** " + " | ".join(psych_lines))
                st.write(f"Вход: {trade['entry_datetime'].strftime('%d.%m.%Y %H:%M')} | Выход: {exit_str}")
                st.write(f"Цена входа: {trade['entry']} | Цена выхода: {trade['exit']}")
                st.write(f"Объём: {trade['volume']} лотов")
                if trade.get('comment'):
                    st.write(f"Комментарий: {trade['comment']}")
                if trade.get('tags'):
                    st.write("Теги: " + ', '.join(trade['tags']))

        if st.button("🗑️ Очистить журнал"):
            delete_trades(user_id)
            st.session_state.trades = []
            st.rerun()

        def fix_datetime(df_in):
            df_out = df_in.copy()
            for col in df_out.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
                if hasattr(df_out[col].dtype, 'tz') and df_out[col].dt.tz is not None:
                    df_out[col] = df_out[col].dt.tz_convert(None)
            return df_out

        df_export = fix_datetime(df)
        st.download_button(label=t("export_csv"), data=df_export.to_csv(index=False).encode('utf-8'), file_name='trades.csv', mime='text/csv')
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False)
        st.download_button(label=t("export_excel"), data=output.getvalue(), file_name='trades.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.info("Сделок пока нет.")

# ==================== АККАУНТЫ ====================
elif st.session_state.current_page == "💼 Аккаунты":
    st.header("💼 Аккаунты")
    # Собираем список уникальных профилей
    all_profiles = set()
    for acc in st.session_state.accounts:
        if acc.get("profile"):
            all_profiles.add(acc["profile"])

    if all_profiles:
        selected_profiles = st.multiselect(t("profile_filter"), sorted(all_profiles))
        if selected_profiles:
            filtered_accounts = [acc for acc in st.session_state.accounts if acc.get("profile") in selected_profiles]
        else:
            filtered_accounts = st.session_state.accounts
    else:
        filtered_accounts = st.session_state.accounts

    with st.expander("➕ Создать аккаунт", expanded=False):
        with st.form("account_form", clear_on_submit=True):
            acc_name = st.text_input("Название аккаунта")
            acc_type = st.selectbox("Тип аккаунта", ["personal", "prop"],
                                    format_func=lambda x: "Личный" if x == "personal" else "Проп-челлендж")
            acc_initial = st.number_input("Начальный баланс", step=100.0, format="%.2f")
            target = None
            phase = None
            purchase_date = None
            daily_loss_limit = None
            profile_input = st.text_input("Профиль (например, Индексы, Форекс)")
            if acc_type == "prop":
                target = st.number_input("Цель по прибыли", step=100.0, format="%.2f")
                phase = st.selectbox("Фаза", ["1 фаза", "2 фаза", "Funded"])
                if phase != "Funded":
                    purchase_date = st.date_input("Дата покупки", datetime.now().date())
            else:
                set_target = st.checkbox("Задать цель по прибыли")
                if set_target:
                    target = st.number_input("Цель по прибыли", step=100.0, format="%.2f")
            daily_loss_limit = st.number_input("Дневной лимит убытка (необязательно)", step=10.0, format="%.2f", value=0.0)
            if st.form_submit_button("Создать аккаунт"):
                if acc_name.strip():
                    create_account(user_id, acc_name, acc_type, acc_initial, target, phase, purchase_date, daily_loss_limit if daily_loss_limit > 0 else None, profile_input if profile_input.strip() else None)
                    st.session_state.accounts = load_accounts(user_id)
                    st.success("Аккаунт создан!")
                    st.rerun()
                else:
                    st.error("Название не может быть пустым")

    # Карточки аккаунтов, похожие на дни календаря
    for acc in filtered_accounts:
        trades_acc = [tr for tr in st.session_state.trades if tr.get("account_id") == acc["id"]]
        total_pnl = sum(tr["pnl"] for tr in trades_acc)
        balance = acc["initial_balance"] + total_pnl
        count = len(trades_acc)
        win_rate = (sum(1 for tr in trades_acc if tr["pnl"] > 0) / count * 100) if count > 0 else 0

        # Заголовок с крупным балансом и P/L
        label = f"💰 {acc['name']} | Баланс: {balance:.2f} $ | P/L: {total_pnl:.2f} | Сделок: {count} | Win rate: {win_rate:.1f}%"
        with st.expander(label, expanded=False):
            # Детали внутри
            if trades_acc:
                df_acc = pd.DataFrame(trades_acc)
                df_acc['entry_datetime'] = pd.to_datetime(df_acc['entry_datetime'])
                df_acc = df_acc.sort_values("entry_datetime")
                df_acc['equity'] = df_acc['pnl'].cumsum() + acc["initial_balance"]
                total_pnl = df_acc['pnl'].sum()
                win_rate = (df_acc['pnl'] > 0).mean() * 100 if len(df_acc) > 0 else 0
                count = len(df_acc)

                st.markdown(f"""
                <div class="account-card">
                    <h3>{acc['name']} <small style="color:#8B949E;">({'Личный' if acc['type']=='personal' else 'Проп'})</small></h3>
                    <h2 style="color:{'#4CAF50' if total_pnl >= 0 else '#F44336'};">{balance:.2f} $</h2>
                    <p><strong>Сделок:</strong> {count} | <strong>Win rate:</strong> {win_rate:.1f}%</p>
                    <p><strong>P/L:</strong> {total_pnl:.2f} $</p>
                    {"<p><strong>Фаза:</strong> " + acc.get('phase','') + " | <strong>Куплен:</strong> " + acc.get('purchase_date','') + "</p>" if acc.get('phase') else ""}
                    {f'<div class="progress-bar"><div class="progress-fill" style="width:{min(max(total_pnl / acc["target"] * 100, 0), 100):.1f}%;"></div></div><small>{min(max(total_pnl / acc["target"] * 100, 0), 100):.1f}% до цели</small>' if acc.get('target') and acc['target'] > 0 else ""}
                </div>
                """, unsafe_allow_html=True)

                st.subheader("📈 Рост депозита")
                fig = px.line(df_acc, x='entry_datetime', y='equity', title='Рост депозита', markers='o', template="plotly_dark")
                fig.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22", font=dict(color="#E6EDF3"))
                st.plotly_chart(fig, use_container_width=True, key=f"acc_equity_{acc['id']}")

                st.subheader("📊 Аналитика")
                profits = df_acc[df_acc['pnl'] > 0]['pnl']
                losses = df_acc[df_acc['pnl'] < 0]['pnl']
                avg_profit = profits.mean() if not profits.empty else 0
                avg_loss = losses.mean() if not losses.empty else 0
                avg_rr = avg_profit / abs(avg_loss) if avg_loss != 0 else 0
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Всего сделок", count)
                col2.metric("Общий P/L", f"{total_pnl:.2f}")
                col3.metric("Винрейт", f"{win_rate:.1f}%")
                col4.metric("Средний P/L", f"{df_acc['pnl'].mean():.2f}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Макс. P/L", f"{df_acc['pnl'].max():.2f}")
                col2.metric("Мин. P/L", f"{df_acc['pnl'].min():.2f}")
                col3.metric("Прибыльные", f"{(df_acc['pnl'] > 0).sum()} / {count}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Средняя прибыль", f"{avg_profit:.2f}")
                col2.metric("Средний убыток", f"{avg_loss:.2f}")
                col3.metric("Средний R/R", f"{avg_rr:.2f}")

                st.subheader("📅 Календарь сделок")
                now = datetime.now()
                cal_month = st.selectbox("Месяц", range(1,13), index=now.month-1, key=f"cal_month_{acc['id']}")
                cal_year = st.number_input("Год", value=now.year, step=1, key=f"cal_year_{acc['id']}")
                df_cal = df_acc[(df_acc['entry_datetime'].dt.month == cal_month) & (df_acc['entry_datetime'].dt.year == cal_year)]
                daily_pnl = df_cal.groupby(df_cal['entry_datetime'].dt.date)['pnl'].sum().reset_index()
                daily_pnl.columns = ['date', 'pnl']
                cal = calendar.Calendar()
                month_days = cal.monthdatescalendar(cal_year, cal_month)
                cols = st.columns(7)
                for i, day_name in enumerate(["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]):
                    cols[i].markdown(f"**{day_name}**")
                for week in month_days:
                    cols = st.columns(7)
                    for i, day in enumerate(week):
                        if day.month != cal_month:
                            cols[i].markdown("")
                            continue
                        day_str = day.isoformat()
                        pnl_row = daily_pnl[daily_pnl['date'] == day]
                        if not pnl_row.empty:
                            pnl_val = pnl_row.iloc[0]['pnl']
                            color_class = "green" if pnl_val > 0 else "red"
                            content = f"{day.day}<br><span style='color:{'#4CAF50' if pnl_val>0 else '#F44336'}'>{pnl_val:.2f}</span>"
                        else:
                            color_class = ""
                            content = f"{day.day}"
                        today_class = "today" if day == date.today() else ""
                        cols[i].markdown(f"<div class='calendar-day {color_class} {today_class}'>{content}</div>", unsafe_allow_html=True)

                st.subheader("Последние сделки")
                for idx, trade in df_acc.tail(5).iterrows():
                    pnl_color = "#4CAF50" if trade['pnl'] > 0 else "#F44336"
                    st.markdown(f"""
                    <div class="trade-card">
                        <h4>{trade['instrument']} <small>{trade['direction']}</small></h4>
                        <p><strong>Дата:</strong> {trade['entry_datetime'].strftime('%Y-%m-%d %H:%M')}</p>
                        <p><strong>P/L:</strong> <span style="color:{pnl_color}">{trade['pnl']:.2f}</span></p>
                        <p>{trade.get('comment', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Сделок пока нет.")

# ==================== КАЛЬКУЛЯТОР ====================
elif st.session_state.current_page == "🧮 Калькулятор":
    st.header("🧮 Калькулятор позиций")
    acc_type = st.radio("Тип счёта", ["Личный", "Проп"], horizontal=True)
    leverage = 1
    if acc_type == "Проп":
        leverage = st.number_input("Кредитное плечо", value=10, step=1, format="%d")
        pip_value_default = 10 / leverage
        pip_value = st.number_input("Цена пункта", value=pip_value_default, step=0.01, format="%.2f")
    else:
        pip_value = st.number_input("Цена пункта", value=10.0, step=0.01, format="%.2f")
    balance = st.number_input("Баланс", value=10000.0, step=100.0)
    risk_pct = st.number_input("Риск, %", value=1.0, step=0.1, format="%.1f")
    risk_curr = balance * (risk_pct / 100)
    stop_loss_pips = st.number_input("Стоп-лосс (пункты)", value=50, step=1)
    take_profit_pips = st.number_input("Тейк-профит (пункты)", value=100, step=1)
    if stop_loss_pips > 0 and pip_value > 0:
        lot_size = risk_curr / (stop_loss_pips * pip_value)
        risk_amount = risk_curr
        potential_profit = take_profit_pips * pip_value * lot_size
        rr = take_profit_pips / stop_loss_pips
    else:
        lot_size = 0
        risk_amount = 0
        potential_profit = 0
        rr = 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Объём лота", f"{lot_size:.2f} лотов")
    col2.metric("Риск", f"{risk_amount:.2f}")
    col3.metric("Потенциальная прибыль", f"{potential_profit:.2f}")
    col4.metric("R/R", f"1:{rr:.1f}")

    with st.expander(t("calc_help_title")):
        st.markdown(t("calc_help_text"))

# ==================== ЗАМЕТКИ (с чек-листами) ====================
elif st.session_state.current_page == "📝 Заметки":
    st.header("📝 Заметки")
    tab_notes, tab_checklists = st.tabs(["📝 Заметки", "✅ Чек-листы"])
    with tab_notes:
        with st.form("new_note", clear_on_submit=True):
            new_title = st.text_input("Заголовок (необязательно)")
            new_content = st.text_area("Текст заметки", height=120)
            if st.form_submit_button("➕ Добавить заметку"):
                if new_content.strip():
                    title = new_title if new_title.strip() else "Без названия"
                    save_note_card(title, new_content, user_id)
                    st.session_state.note_cards = load_note_cards(user_id)
                    st.success("Заметка добавлена!")
                else:
                    st.warning("Текст заметки не может быть пустым")
        st.write("---")
        for card in st.session_state.note_cards:
            with st.container():
                st.markdown(f"<div class='note-card'><h4>{card['title']}</h4><p>{card['content'][:200]}{'...' if len(card['content'])>200 else ''}</p><small>{card['created_at']}</small></div>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1])
                if col1.button("✏️ Редактировать", key=f"edit_{card['id']}"):
                    st.session_state[f"edit_{card['id']}"] = True
                if col2.button("🗑️ Удалить", key=f"del_{card['id']}"):
                    delete_note_card(card['id'])
                    st.session_state.note_cards = load_note_cards(user_id)
                    st.rerun()
                if st.session_state.get(f"edit_{card['id']}"):
                    with st.form(f"edit_form_{card['id']}"):
                        edit_title = st.text_input("Заголовок", value=card['title'], key=f"title_{card['id']}")
                        edit_content = st.text_area("Текст", value=card['content'], height=150, key=f"content_{card['id']}")
                        if st.form_submit_button("Сохранить"):
                            update_note_card(card['id'], edit_title, edit_content)
                            st.session_state.note_cards = load_note_cards(user_id)
                            st.session_state[f"edit_{card['id']}"] = False
                            st.rerun()
                    if st.button("Отмена", key=f"cancel_{card['id']}"):
                        st.session_state[f"edit_{card['id']}"] = False
                        st.rerun()
    with tab_checklists:
        sub_tab1, sub_tab2 = st.tabs(["Мои шаблоны", "Сегодняшний чек-лист"])
        with sub_tab1:
            with st.expander("➕ Создать новый шаблон", expanded=False):
                with st.form("new_template_form", clear_on_submit=True):
                    title = st.text_input("Название шаблона")
                    items_text = st.text_area("Пункты (каждый с новой строки)", height=150)
                    days_options = st.multiselect("Дни недели", ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"], default=["Пн","Вт","Ср","Чт","Пт"])
                    if st.form_submit_button("Сохранить"):
                        if title.strip() and items_text.strip():
                            items = [item.strip() for item in items_text.split('\n') if item.strip()]
                            days_json = json.dumps(days_options, ensure_ascii=False)
                            create_checklist_template(user_id, title, json.dumps(items), days_json)
                            st.success("Шаблон создан!")
                            st.rerun()
                        else:
                            st.warning("Заполните название и хотя бы один пункт.")
            templates = load_checklist_templates(user_id)
            if not templates:
                st.info("Нет шаблонов. Создайте первый!")
            else:
                for tmpl in templates:
                    items = json.loads(tmpl['items'])
                    days = json.loads(tmpl.get('days', '[]'))
                    with st.container():
                        st.markdown(f"<div class='checklist-card'><h4>{tmpl['title']}</h4><ul>" + "".join(f"<li>{item}</li>" for item in items) + f"</ul><small>Дни: {', '.join(days)}</small></div>", unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        if col1.button("🚀 Запустить на сегодня", key=f"run_{tmpl['id']}"):
                            empty_status = {str(i): False for i in range(len(items))}
                            save_checklist_run(user_id, tmpl['id'], date.today(), json.dumps(empty_status))
                            st.success("Чек-лист запущен! Перейдите на вкладку 'Сегодняшний чек-лист'.")
                            st.rerun()
                        if col2.button("🗑️ Удалить", key=f"del_tmpl_{tmpl['id']}"):
                            delete_checklist_template(tmpl['id'])
                            st.rerun()
        with sub_tab2:
            today = date.today()
            day_name = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"][today.weekday()]
            runs = load_checklist_runs(user_id, run_date=today)
            active_runs = []
            for run in runs:
                template = next((tmpl for tmpl in load_checklist_templates(user_id) if tmpl['id'] == run['template_id']), None)
                if template:
                    days = json.loads(template.get('days', '[]'))
                    if day_name in days:
                        active_runs.append(run)
            if not active_runs:
                st.info("На сегодня нет активных чек-листов.")
            else:
                for run in active_runs:
                    template = next((tmpl for tmpl in load_checklist_templates(user_id) if tmpl['id'] == run['template_id']), None)
                    items = json.loads(template['items'])
                    status = json.loads(run['items_status']) if run.get('items_status') else {}
                    st.subheader(template['title'])
                    updated_status = {}
                    for i, item in enumerate(items):
                        checked = status.get(str(i), False)
                        new_val = st.checkbox(item, value=checked, key=f"check_{run['id']}_{i}")
                        updated_status[str(i)] = new_val
                    if st.button("💾 Сохранить", key=f"save_run_{run['id']}"):
                        save_checklist_run(user_id, run['template_id'], today, json.dumps(updated_status))
                        st.success("Статус обновлён!")
                        st.rerun()

# ==================== НОВОСТИ ====================
elif st.session_state.current_page == "📅 Новости":
    st.header("📅 Новости")
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
                c2.markdown(f'<div class="pulse-red">⚠️ Осталось: {timer_str}</div>', unsafe_allow_html=True)
            else:
                c2.info(f"До события: {timer_str}")
        else:
            st.info("Все новости уже прошли.")
        st.subheader("📆 Все новости")
        df = pd.DataFrame(news_items)
        df['time'] = pd.to_datetime(df['time'])
        st.dataframe(df.sort_values("time"), use_container_width=True)

# ==================== ГРАФИК (Plotly, без VPN будет работать на облаке) ====================
elif st.session_state.current_page == "📈 График":
    st.header("📈 График")
    symbol = st.selectbox("Инструмент", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD", "ETH-USD", "AAPL", "TSLA"], key="tv_symbol")
    period = st.selectbox("Период", ["1d","5d","1mo","3mo","6mo","1y","2y","5y"], index=2)
    interval = st.selectbox("Интервал", ["1m","5m","15m","30m","1h","1d"], index=3)

    @st.cache_data(ttl=300)
    def load_chart_data(symbol, period, interval):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                return None
            df.reset_index(inplace=True)
            return df
        except Exception as e:
            st.error(f"Не удалось загрузить данные: {e}")
            return None

    data = load_chart_data(symbol, period, interval)
    if data is not None and not data.empty:
        fig = px.line(data, x='Datetime', y='Close', title=f'{symbol} ({period}, {interval})')
        fig.update_layout(template="plotly_dark", xaxis_title="Время", yaxis_title="Цена")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных для отображения. Если вы за границей или используете прокси, всё должно работать.")

    st.markdown("---")
    st.subheader("🔔 Алерт на цену")
    alert_symbol = st.selectbox("Инструмент", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD", "ETH-USD", "AAPL", "TSLA"], key="alert_sym")
    condition = st.selectbox("Условие", ["Выше", "Ниже"])
    alert_price = st.number_input("Цена", step=0.00001, format="%.5f")
    if st.button("Проверить"):
        ticker = yf.Ticker(alert_symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            if (condition == "Выше" and current_price > alert_price) or (condition == "Ниже" and current_price < alert_price):
                st.success(f"🎯 Алерт сработал! {current_price:.5f}")
            else:
                st.info(f"😴 Алерт не сработал. Текущая цена: {current_price:.5f}")
        else:
            st.error("Не удалось получить цену. Проверьте тикер.")

# ==================== БАЗА ЗНАНИЙ ====================
elif st.session_state.current_page == "📚 База знаний":
    st.header("📚 База знаний")
    if is_admin:
        with st.expander("➕ Добавить материал", expanded=False):
            with st.form("material_form", clear_on_submit=True):
                title = st.text_input(t("material_title"))
                description = st.text_area(t("material_description"))
                category = st.selectbox(t("material_category"), ["Психология", "Обучение", "Стратегии", "Общее"])
                uploaded_file = st.file_uploader(t("material_file"), type=["pdf", "jpg", "jpeg", "png", "docx"])
                preview_file = st.file_uploader(t("material_preview"), type=["jpg", "jpeg", "png"])
                full_text = st.text_area(t("full_text"), height=200)
                version = st.text_input(t("version"))
                if st.form_submit_button(t("add_material")):
                    if title and uploaded_file is not None:
                        if uploaded_file.size > 5 * 1024 * 1024:
                            st.error("Файл слишком большой. Максимум 5 МБ.")
                        else:
                            try:
                                file_bytes = uploaded_file.read()
                                b64_str = base64.b64encode(file_bytes).decode()
                                file_name = uploaded_file.name
                                preview_b64 = None
                                if preview_file is not None:
                                    if preview_file.size > 1 * 1024 * 1024:
                                        st.error("Превью слишком большое. Максимум 1 МБ.")
                                        st.stop()
                                    preview_bytes = preview_file.read()
                                    preview_b64 = base64.b64encode(preview_bytes).decode()
                                add_learning_material(
                                    title=title,
                                    description=description,
                                    file_base64=b64_str,
                                    file_name=file_name,
                                    category=category,
                                    preview_base64=preview_b64,
                                    full_text=full_text if full_text.strip() else None,
                                    version=version if version.strip() else None
                                )
                                st.success("Материал добавлен!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Ошибка загрузки: {e}")
                    else:
                        st.warning("Заполните название и загрузите файл.")

    materials = load_learning_materials()
    if not materials:
        st.info(t("no_materials"))
    else:
        # Карточки материалов на всю ширину
        for mat in materials:
            version_str = f" (v{mat['version']})" if mat.get('version') else ""
            desc = mat.get('description', '')[:100]
            label = f"📄 {mat['title']}{version_str} – {desc}..."
            with st.expander(label, expanded=False):
                if mat.get('preview_base64'):
                    st.image(base64.b64decode(mat['preview_base64']), width=300)
                st.write(f"**Категория:** {mat.get('category', 'общее')}")
                if mat.get('description'):
                    st.write(mat['description'])
                if mat.get('full_text'):
                    st.markdown("**Полный текст:**")
                    st.markdown(mat['full_text'])
                if mat.get('file_base64'):
                    st.markdown(f"**Файл:** {mat['file_name']}")
                    file_bytes = base64.b64decode(mat['file_base64'])
                    st.download_button(label=t("download"), data=file_bytes, file_name=mat['file_name'], mime="application/octet-stream", key=f"download_{mat['id']}")
                if is_admin:
                    if st.button("🗑️ Удалить", key=f"del_mat_{mat['id']}"):
                        delete_learning_material(mat['id'])
                        st.rerun()

# ==================== ПРОФИЛЬ ====================
elif st.session_state.current_page == "👤 Профиль":
    st.header("👤 Личный профиль")
    created_at = user.created_at if hasattr(user, 'created_at') else "неизвестно"
    st.write(f"**Дата регистрации:** {created_at}")
    st.subheader("🖼️ Аватар")
    if avatar_base64:
        st.markdown(f'<img src="data:image/png;base64,{avatar_base64}" style="width:100px;border-radius:50%;">', unsafe_allow_html=True)
        if st.button("Удалить аватар"):
            supabase.table("profiles").update({"avatar_base64": None}).eq("user_id", user_id).execute()
            st.rerun()
    else:
        st.write("Аватар не установлен.")
    uploaded = st.file_uploader("Загрузить изображение", type=["jpg","jpeg","png"])
    if uploaded:
        if uploaded.size > 200 * 1024:
            st.error("Файл слишком большой. Максимум 200 КБ.")
        else:
            try:
                bytes_data = uploaded.read()
                b64_str = base64.b64encode(bytes_data).decode()
                save_avatar_base64(user_id, b64_str)
                st.success("Аватар обновлён!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка загрузки: {e}")
    st.write("---")
    st.subheader("🖼️ Фон бокового меню")
    sidebar_bg_current = profile["sidebar_bg_base64"] if profile and profile.get("sidebar_bg_base64") else None
    if sidebar_bg_current:
        st.markdown(f'<img src="data:image/png;base64,{sidebar_bg_current}" style="width:100px;border-radius:8px;">', unsafe_allow_html=True)
        if st.button("Удалить фон"):
            supabase.table("profiles").update({"sidebar_bg_base64": None}).eq("user_id", user_id).execute()
            st.rerun()
    else:
        st.write("Фон не установлен.")
    bg_uploaded = st.file_uploader("Загрузить фон", type=["jpg","jpeg","png"], key="bg_upload_sidebar")
    if bg_uploaded:
        if bg_uploaded.size > 500 * 1024:
            st.error("Файл слишком большой. Максимум 500 КБ.")
        else:
            try:
                bytes_data = bg_uploaded.read()
                b64_str = base64.b64encode(bytes_data).decode()
                save_sidebar_bg_base64(user_id, b64_str)
                st.success("Фон бокового меню обновлён!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка загрузки фона: {e}")
    st.write("---")
    st.subheader("🖼️ Фон рабочего пространства")
    main_bg_current = profile["main_bg_base64"] if profile and profile.get("main_bg_base64") else None
    if main_bg_current:
        st.markdown(f'<img src="data:image/png;base64,{main_bg_current}" style="width:100px;border-radius:8px;">', unsafe_allow_html=True)
        if st.button("Удалить фон рабочего пространства"):
            supabase.table("profiles").update({"main_bg_base64": None}).eq("user_id", user_id).execute()
            st.rerun()
    else:
        st.write("Фон рабочего пространства не установлен.")
    main_bg_uploaded = st.file_uploader("Загрузить фон рабочего пространства", type=["jpg","jpeg","png"], key="bg_upload_main")
    if main_bg_uploaded:
        if main_bg_uploaded.size > 500 * 1024:
            st.error("Файл слишком большой. Максимум 500 КБ.")
        else:
            try:
                bytes_data = main_bg_uploaded.read()
                b64_str = base64.b64encode(bytes_data).decode()
                save_main_bg_base64(user_id, b64_str)
                st.success("Фон рабочего пространства обновлён!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка загрузки фона: {e}")
    st.write("---")
    st.subheader("🖼️ Фон страницы входа")
    login_bg_current = profile["login_bg_base64"] if profile and profile.get("login_bg_base64") else None
    if login_bg_current:
        st.markdown(f'<img src="data:image/png;base64,{login_bg_current}" style="width:100px;border-radius:8px;">', unsafe_allow_html=True)
        if st.button("Удалить фон"):
            supabase.table("profiles").update({"login_bg_base64": None}).eq("user_id", user_id).execute()
            st.rerun()
    else:
        st.write("Фон не установлен.")
    login_bg_uploaded = st.file_uploader("Загрузить фон страницы входа", type=["jpg","jpeg","png"], key="bg_upload_login")
    if login_bg_uploaded:
        if login_bg_uploaded.size > 500 * 1024:
            st.error("Файл слишком большой. Максимум 500 КБ.")
        else:
            try:
                bytes_data = login_bg_uploaded.read()
                b64_str = base64.b64encode(bytes_data).decode()
                save_login_bg_base64(user_id, b64_str)
                st.success("Фон страницы входа обновлён!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка загрузки фона: {e}")
    if is_admin:
        st.write("---")
        st.subheader("🌐 Общий фон страницы входа (для всех)")
        app_setting = get_app_setting()
        current_public_bg = app_setting["login_bg_base64"] if app_setting and app_setting.get("login_bg_base64") else None
        if current_public_bg:
            st.markdown(f'<img src="data:image/png;base64,{current_public_bg}" style="width:100px;border-radius:8px;">', unsafe_allow_html=True)
            if st.button("Удалить общий фон"):
                supabase.table("app_settings").upsert({"id": 1, "login_bg_base64": None}).execute()
                st.success("Общий фон удалён!")
                st.rerun()
        else:
            st.write("Общий фон не установлен.")
        uploaded_public = st.file_uploader("Загрузить изображение", type=["jpg","jpeg","png"], key="bg_upload_public_login")
        if uploaded_public:
            if uploaded_public.size > 500 * 1024:
                st.error("Файл слишком большой. Максимум 500 КБ.")
            else:
                try:
                    bytes_data = uploaded_public.read()
                    b64_str = base64.b64encode(bytes_data).decode()
                    supabase.table("app_settings").upsert({"id": 1, "login_bg_base64": b64_str}).execute()
                    st.success("Общий фон обновлён!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка загрузки: {e}")
    st.write("---")
    st.subheader("✏️ Изменить никнейм")
    with st.form("change_nickname"):
        new_nick = st.text_input("Новый никнейм", value=nickname or "")
        if st.form_submit_button("Сохранить никнейм"):
            if new_nick.strip():
                supabase.table("profiles").upsert({"user_id": user_id, "nickname": new_nick}).execute()
                st.success("Никнейм обновлён!")
                st.rerun()
            else:
                st.error("Никнейм не может быть пустым")
    st.write("---")
    st.subheader("🌐 Язык")
    lang = st.selectbox("Язык / Language", ["ru", "en"], index=0 if st.session_state.lang == "ru" else 1)
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()
    st.write("---")
    st.subheader("📧 Изменить email")
    with st.form("change_email"):
        old_e = st.text_input("Текущий email")
        pwd = st.text_input("Пароль для подтверждения", type="password")
        new_e = st.text_input("Новый email")
        if st.form_submit_button("Сохранить новый email"):
            if old_e != user.email:
                st.error("Текущий email неверен.")
            else:
                try:
                    sign_in(old_e, pwd)
                    supabase.auth.update_user({"email": new_e})
                    st.success("Письмо с подтверждением отправлено на новый адрес.")
                except Exception as e:
                    st.error("Неверный пароль или ошибка: " + str(e))
    st.write("---")
    st.subheader("🔒 Изменить пароль")
    with st.form("change_pwd"):
        cur_p = st.text_input("Текущий пароль", type="password")
        new_p = st.text_input("Новый пароль", type="password")
        if st.form_submit_button("Обновить пароль"):
            if not cur_p or not new_p:
                st.warning("Заполните оба поля.")
            else:
                try:
                    sign_in(user.email, cur_p)
                    supabase.auth.update_user({"password": new_p})
                    st.success("Пароль изменён!")
                except Exception as e:
                    st.error("Неверный текущий пароль или ошибка: " + str(e))

# ==================== АДМИНКА НОВОСТЕЙ ====================
elif st.session_state.current_page == "⚙️ Админка новостей" and is_admin:
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
            add_news({"time": news_time.isoformat(), "currency": currency, "event": event, "importance": importance})
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