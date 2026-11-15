#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPM TOOL - Sade Telegram Botu
Çalıştırma: python bot.py
Gerekli: pip install pycryptodome brotli requests urllib3 certifi pyTelegramBotAPI
"""

import os
import sys
import time
import json
import hashlib
import struct
import zlib
import uuid
import base64
import random
import string
import re
import sqlite3
import threading
import ssl
import certifi
import urllib.request
import urllib.parse
import urllib.error
import io
from datetime import datetime, timezone

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except ImportError:
    sys.exit("pycryptodome eksik: pip install pycryptodome")

try:
    import brotli
except ImportError:
    sys.exit("brotli eksik: pip install brotli")

try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
except ImportError:
    sys.exit("pyTelegramBotAPI eksik: pip install pyTelegramBotAPI")

# ═══════════════════════════════════════════════════════════
# AYARLAR
# ═══════════════════════════════════════════════════════════

BOT_TOKEN = "8267489409:AAEHjA6_xNq8wQ2en_HrQaSjrT44O6QhDAE"
CONTACT_USERNAME = "deep_oq"

ADMIN_ID = 8984033559

FREE_TRIAL_CLONE_LIMIT = 1
PAID_DAILY_CLONE_LIMIT = 20
ADMIN_DAILY_CLONE_LIMIT = 9999

FIREBASE_API_KEY = "AIzaSyBxDbYXBlWGRVYkmm4XVgvVi487jfsa-Ug"
FIREBASE_PROJECT = "cpmtool-de966"
FIRESTORE_BASE = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}/databases/(default)/documents"

FK = "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA"
LOAD_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/GetPlayerRecords3"
SAVE_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/SavePlayerRecordsPartially8"
CPM_EU = "https://europe-west1-cp-multiplayer.cloudfunctions.net"
CPM_CARS_FETCH_URL = f"{CPM_EU}/GetAllCars2"
CPM_CARS_SAVE_URL = f"{CPM_EU}/SaveCarsPartially8"

GAME_HEADERS = {
    "Accept": "*/*", "Accept-Encoding": "gzip", "Content-Type": "application/json",
    "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
    "X-Unity-Version": "2022.3.62f2",
}

DB_DIR = os.path.join(os.path.expanduser("~"), "cpm_data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "cpm_tokens.db")
LICENSE_DB_PATH = os.path.join(DB_DIR, "cpm_licenses.db")
USER_SETTINGS_DB_PATH = os.path.join(DB_DIR, "cpm_user_settings.db")
CONFIG_DB_PATH = os.path.join(DB_DIR, "cpm_config.db")

# ═══════════════════════════════════════════════════════════
# ÇEVİRİLER
# ═══════════════════════════════════════════════════════════

TRANSLATIONS = {
    "tr": {
        "welcome": "<b>CPM ACCOUNT STUDIO</b>\n\nHesap kopyalama paneli.\n\nAşağıdan işlem seçin.",
        "welcome_new": "<b>CPM ACCOUNT STUDIO</b>\n\nHoş geldin. Sana <b>1 ücretsiz hesap kopyalama</b> hakkı tanımlandı.\n\nBu hakkı kullandıktan sonra devam etmek için lisans gerekir.",
        "trial_used": "Ücretsiz kopyalama hakkını kullandın.\n\nDevam etmek için lisans gerekli.\nDestek: @{contact}",
        "key_required": "<b>Lisans Gerekli</b>\n\nBotu kullanmaya devam etmek için geçerli bir lisans anahtarına ihtiyacın var.\n\nDestek: @{contact}\n\nAnahtarı aşağıya yaz:\nÖrnek: <code>CPM-XXXX-XXXX</code>",
        "menu_clone": "Hesap Kopyala",
        "menu_contact": "Destek",
        "menu_change_lang": "Dil Değiştir",
        "menu_back": "Ana Menü",
        "lang_select": "<b>Dil Seçin</b>",
        "enter_clone_email": "Kopyalanacak kaynak hesabın e-posta adresini gir:",
        "enter_clone_pass": "E-posta alındı.\nKaynak hesabın şifresini gir:",
        "enter_clone_count": "Kaç kopya oluşturulsun? (En fazla: {max})",
        "enter_number": "Geçerli bir sayı gir.",
        "clone_invalid_count": "Miktar 1 ile {max} arasında olmalı.",
        "clone_started": "<b>Kopyalama Başlatıldı</b>\n({count} hesap oluşturuluyor)\nİşlem sürerken bekle...\n\n0/{count}",
        "clone_progress": "<b>Kopyalama Sürüyor...</b>\n\n{done}/{total} tamamlandı",
        "clone_done": "<b>Kopyalama Tamamlandı</b>\n\nBaşarılı: {success}/{total}\n\nHesaplar .txt olarak gönderiliyor...",
        "clone_none": "Hiçbir hesap kopyalanamadı.",
        "clone_error": "Kopyalama sırasında hata: <code>{err}</code>",
        "clone_cars_fail": "Kaynak hesaptan araçlar çekilemedi.",
        "clone_login_fail": "Kaynak hesap girişi başarısız: <code>{err}</code>",
        "clone_doc_caption": "{success} hesap başarıyla oluşturuldu.",
        "daily_limit_reached": "<b>Günlük Limit Doldu</b>\n\nBugünkü kopyalama limitin bitti (Maks: {limit}).\nDestek: @{contact}",
        "cancel": "İptal",
        "cancelled": "İşlem iptal edildi.",
        "use_buttons": "Lütfen menüdeki butonları kullan.",
        "contact_info": "Destek: @{contact}",
        "invalid_key": "<b>Geçersiz Lisans</b>\n{msg}\n\nDestek: @{contact}",
        "settings_menu": "<b>Dil Ayarları</b>\n\nDil seç:",
        "banned": "<b>Yasaklandın</b>\nBu botu kullanma yetkin admin tarafından engellendi.",
        "channel_sub_required": "<b>Kanal Aboneliği Gerekli</b>\n\nBotu kullanabilmek için önce kanalımıza katılman gerekiyor.\n\n<a href='{channel_url}'>Kanala Katıl</a>\n\nKatıldıktan sonra /start komutuna tekrar bas.",
    },
    "en": {
        "welcome": "<b>CPM ACCOUNT STUDIO</b>\n\nAccount cloning panel.\n\nSelect an action below.",
        "welcome_new": "<b>CPM ACCOUNT STUDIO</b>\n\nWelcome. You have <b>1 free account clone</b> right.\n\nAfter using it, you need a license to continue.",
        "trial_used": "You used your free clone right.\n\nA license is required to continue.\nSupport: @{contact}",
        "key_required": "<b>License Required</b>\n\nYou need a valid license key to continue using the bot.\n\nSupport: @{contact}\n\nEnter your key below:\nExample: <code>CPM-XXXX-XXXX</code>",
        "menu_clone": "Clone Account",
        "menu_contact": "Support",
        "menu_change_lang": "Change Language",
        "menu_back": "Main Menu",
        "lang_select": "<b>Select Language</b>",
        "enter_clone_email": "Enter the source account email to clone:",
        "enter_clone_pass": "Email received.\nEnter the source account password:",
        "enter_clone_count": "How many copies? (Max: {max})",
        "enter_number": "Enter a valid number.",
        "clone_invalid_count": "Amount must be between 1 and {max}.",
        "clone_started": "<b>Cloning Started</b>\n({count} accounts generating)\nPlease wait...\n\n0/{count}",
        "clone_progress": "<b>Clone in Progress...</b>\n\n{done}/{total} completed",
        "clone_done": "<b>Clone Complete</b>\n\nSuccess: {success}/{total}\n\nAccounts are being sent as .txt...",
        "clone_none": "No accounts could be cloned.",
        "clone_error": "Error during clone: <code>{err}</code>",
        "clone_cars_fail": "Could not fetch cars from source account.",
        "clone_login_fail": "Source account login failed: <code>{err}</code>",
        "clone_doc_caption": "{success} accounts successfully created.",
        "daily_limit_reached": "<b>Daily Limit Reached</b>\n\nYou have reached your daily clone limit (Max: {limit}).\nSupport: @{contact}",
        "cancel": "Cancel",
        "cancelled": "Action cancelled.",
        "use_buttons": "Please use the menu buttons.",
        "contact_info": "Support: @{contact}",
        "invalid_key": "<b>Invalid License</b>\n{msg}\n\nSupport: @{contact}",
        "settings_menu": "<b>Language Settings</b>\n\nSelect language:",
        "banned": "<b>You are Banned</b>\nYour access to this bot has been restricted by admin.",
        "channel_sub_required": "<b>Channel Subscription Required</b>\n\nYou must join our channel to use this bot.\n\n<a href='{channel_url}'>Join Channel</a>\n\nAfter joining, press /start again.",
    },
    "ru": {
        "welcome": "<b>CPM ACCOUNT STUDIO</b>\n\nПанель клонирования аккаунтов.\n\nВыберите действие.",
        "welcome_new": "<b>CPM ACCOUNT STUDIO</b>\n\nДобро пожаловать. Тебе дано <b>1 бесплатное клонирование</b>.\n\nПосле использования потребуется лицензия.",
        "trial_used": "Ты использовал бесплатное клонирование.\n\nДля продолжения нужна лицензия.\nПоддержка: @{contact}",
        "key_required": "<b>Требуется Лицензия</b>\n\nДля использования бота нужен лицензионный ключ.\n\nПоддержка: @{contact}\n\nВведи ключ:\nПример: <code>CPM-XXXX-XXXX</code>",
        "menu_clone": "Клонировать",
        "menu_contact": "Поддержка",
        "menu_change_lang": "Сменить Язык",
        "menu_back": "Главное Меню",
        "lang_select": "<b>Выберите Язык</b>",
        "enter_clone_email": "Введите email исходного аккаунта:",
        "enter_clone_pass": "Email получен.\nВведите пароль исходного аккаунта:",
        "enter_clone_count": "Сколько копий? (Макс: {max})",
        "enter_number": "Введите корректное число.",
        "clone_invalid_count": "Число должно быть от 1 до {max}.",
        "clone_started": "<b>Клонирование Запущено</b>\n(создаётся {count} аккаунтов)\nПодожди...\n\n0/{count}",
        "clone_progress": "<b>Клонирование...</b>\n\n{done}/{total} завершено",
        "clone_done": "<b>Клонирование Завершено</b>\n\nУспешно: {success}/{total}\n\nАккаунты отправляются как .txt...",
        "clone_none": "Не удалось клонировать ни один аккаунт.",
        "clone_error": "Ошибка клонирования: <code>{err}</code>",
        "clone_cars_fail": "Не удалось получить машины с исходного аккаунта.",
        "clone_login_fail": "Ошибка входа в исходный аккаунт: <code>{err}</code>",
        "clone_doc_caption": "Успешно создано аккаунтов: {success}.",
        "daily_limit_reached": "<b>Лимит Исчерпан</b>\n\nДневной лимит клонирования исчерпан (Макс: {limit}).\nПоддержка: @{contact}",
        "cancel": "Отмена",
        "cancelled": "Действие отменено.",
        "use_buttons": "Используй кнопки меню.",
        "contact_info": "Поддержка: @{contact}",
        "invalid_key": "<b>Неверная Лицензия</b>\n{msg}\n\nПоддержка: @{contact}",
        "settings_menu": "<b>Настройки Языка</b>\n\nВыберите язык:",
        "banned": "<b>Ты Заблокирован</b>\nДоступ ограничен администратором.",
        "channel_sub_required": "<b>Требуется Подписка на Канал</b>\n\nДля использования бота подпишись на канал.\n\n<a href='{channel_url}'>Подписаться</a>\n\nПосле подписки нажми /start.",
    }
}

def t(lang, key, **kwargs):
    text = TRANSLATIONS.get(lang, TRANSLATIONS["tr"]).get(key, TRANSLATIONS["tr"].get(key, key))
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError):
        return text

# ═══════════════════════════════════════════════════════════
# CONFIG DB
# ═══════════════════════════════════════════════════════════

class ConfigDB:
    def __init__(self, path=CONFIG_DB_PATH):
        self.path = path
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS required_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                invite_link TEXT NOT NULL,
                title TEXT DEFAULT '',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(channel_id)
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )""")
            c.commit()

    def add_channel(self, channel_id, invite_link, title=""):
        with sqlite3.connect(self.path) as c:
            c.execute("""INSERT OR REPLACE INTO required_channels
                (channel_id, invite_link, title) VALUES (?, ?, ?)""",
                (str(channel_id), invite_link, title))
            c.commit()

    def remove_channel(self, channel_id):
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM required_channels WHERE channel_id = ?", (str(channel_id),))
            c.commit()

    def list_channels(self):
        with sqlite3.connect(self.path) as c:
            rows = c.execute("SELECT channel_id, invite_link, title FROM required_channels ORDER BY id").fetchall()
        return [{"channel_id": r[0], "invite_link": r[1], "title": r[2] or ""} for r in rows]

    def get_config(self, key, default=None):
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
        return row[0] if row else default

    def set_config(self, key, value):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
            c.commit()

_config_db = ConfigDB()

# ═══════════════════════════════════════════════════════════
# KULLANICI DB
# ═══════════════════════════════════════════════════════════

class UserSettingsDB:
    def __init__(self, path=USER_SETTINGS_DB_PATH):
        self.path = path
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS settings (
                chat_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'tr',
                daily_clone_count INTEGER DEFAULT 0,
                last_clone_date TEXT,
                total_clone_count INTEGER DEFAULT 0,
                free_trial_used INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                started_bot INTEGER DEFAULT 0,
                first_start_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            for ddl in [
                "ALTER TABLE settings ADD COLUMN is_banned INTEGER DEFAULT 0",
                "ALTER TABLE settings ADD COLUMN free_trial_used INTEGER DEFAULT 0",
                "ALTER TABLE settings ADD COLUMN total_clone_count INTEGER DEFAULT 0",
                "ALTER TABLE settings ADD COLUMN started_bot INTEGER DEFAULT 0",
            ]:
                try:
                    c.execute(ddl)
                except:
                    pass
            c.commit()

    def get_lang(self, chat_id):
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT lang FROM settings WHERE chat_id = ?", (chat_id,)).fetchone()
        return row[0] if row else None

    def set_lang(self, chat_id, lang):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT OR IGNORE INTO settings (chat_id, lang) VALUES (?, ?)", (chat_id, lang))
            c.execute("UPDATE settings SET lang = ? WHERE chat_id = ?", (lang, chat_id))
            c.commit()

    def is_banned(self, chat_id):
        if chat_id == ADMIN_ID:
            return False
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT is_banned FROM settings WHERE chat_id = ?", (chat_id,)).fetchone()
        return bool(row[0]) if row else False

    def set_ban(self, chat_id, status):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT OR IGNORE INTO settings (chat_id, is_banned) VALUES (?, ?)", (chat_id, status))
            c.execute("UPDATE settings SET is_banned = ? WHERE chat_id = ?", (status, chat_id))
            c.commit()

    def mark_started(self, chat_id):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT OR IGNORE INTO settings (chat_id, started_bot) VALUES (?, 1)", (chat_id,))
            c.execute("UPDATE settings SET started_bot = 1 WHERE chat_id = ?", (chat_id,))
            c.commit()

    def get_all_started_users(self):
        with sqlite3.connect(self.path) as c:
            rows = c.execute("SELECT chat_id FROM settings WHERE started_bot = 1 AND is_banned = 0").fetchall()
        return [r[0] for r in rows]

    def get_daily_clone_count(self, chat_id):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT daily_clone_count, last_clone_date FROM settings WHERE chat_id = ?", (chat_id,)).fetchone()
        if not row or row[1] != today:
            return 0
        return row[0] or 0

    def get_total_clone_count(self, chat_id):
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT total_clone_count FROM settings WHERE chat_id = ?", (chat_id,)).fetchone()
        return (row[0] or 0) if row else 0

    def get_free_trial_used(self, chat_id):
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT free_trial_used FROM settings WHERE chat_id = ?", (chat_id,)).fetchone()
        return bool(row[0]) if row else False

    def mark_free_trial_used(self, chat_id):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT OR IGNORE INTO settings (chat_id, free_trial_used) VALUES (?, 1)", (chat_id,))
            c.execute("UPDATE settings SET free_trial_used = 1 WHERE chat_id = ?", (chat_id,))
            c.commit()

    def increment_clone_count(self, chat_id):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT daily_clone_count, last_clone_date, total_clone_count FROM settings WHERE chat_id = ?", (chat_id,)).fetchone()
            if row:
                daily = (row[0] or 0) + 1 if row[1] == today else 1
                total = (row[2] or 0) + 1
                c.execute("UPDATE settings SET daily_clone_count = ?, last_clone_date = ?, total_clone_count = ? WHERE chat_id = ?",
                          (daily, today, total, chat_id))
            else:
                c.execute("INSERT INTO settings (chat_id, daily_clone_count, last_clone_date, total_clone_count) VALUES (?, 1, ?, 1)",
                          (chat_id, today))
            c.commit()

_user_settings = UserSettingsDB()

# ═══════════════════════════════════════════════════════════
# LİSANS DB
# ═══════════════════════════════════════════════════════════

class LicenseDB:
    def __init__(self, path=LICENSE_DB_PATH):
        self.path = path
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS licenses (
                chat_id INTEGER PRIMARY KEY,
                api_key TEXT NOT NULL,
                ip TEXT,
                expires_at_ms INTEGER DEFAULT 0,
                is_free INTEGER DEFAULT 0,
                daily_clone_limit INTEGER DEFAULT 20,
                last_check INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            try:
                c.execute("ALTER TABLE licenses ADD COLUMN is_free INTEGER DEFAULT 0")
            except:
                pass
            try:
                c.execute("ALTER TABLE licenses ADD COLUMN daily_clone_limit INTEGER DEFAULT 20")
            except:
                pass
            c.commit()

    def save(self, chat_id, api_key, ip, expires_at_ms, is_free=0, daily_clone_limit=20):
        with sqlite3.connect(self.path) as c:
            c.execute("""INSERT OR REPLACE INTO licenses
                (chat_id, api_key, ip, expires_at_ms, is_free, daily_clone_limit, last_check)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (chat_id, api_key, ip, int(expires_at_ms), is_free, daily_clone_limit, int(time.time())))
            c.commit()

    def get(self, chat_id):
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT api_key, ip, expires_at_ms, is_free, daily_clone_limit FROM licenses WHERE chat_id = ?", (chat_id,)).fetchone()
        if not row:
            return None
        return {"api_key": row[0], "ip": row[1], "expires_at_ms": row[2],
                "is_free": row[3] or 0, "daily_clone_limit": row[4] or 20}

    def delete(self, chat_id):
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM licenses WHERE chat_id = ?", (chat_id,))
            c.commit()

    def clear_expired(self):
        now_ms = int(time.time() * 1000)
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM licenses WHERE expires_at_ms > 0 AND expires_at_ms < ?", (now_ms,))
            c.commit()

_license_db = LicenseDB()

# ═══════════════════════════════════════════════════════════
# YARDIMCI
# ═══════════════════════════════════════════════════════════

def get_public_ip():
    endpoints = ["https://api.ipify.org?format=json", "https://ipv4.icanhazip.com"]
    ctx = ssl.create_default_context(cafile=certifi.where())
    for url in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CPM-Tool"})
            with urllib.request.urlopen(req, timeout=6, context=ctx) as r:
                data = r.read().decode().strip()
                if data.startswith("{"):
                    return json.loads(data).get("ip", "").strip()
                if data:
                    return data
        except Exception:
            continue
    return None

# ═══════════════════════════════════════════════════════════
# FIRESTORE
# ═══════════════════════════════════════════════════════════

def _fs_get(key):
    url = f"{FIRESTORE_BASE}/keys/{urllib.parse.quote(key)}?key={FIREBASE_API_KEY}"
    ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except Exception as e:
        raise RuntimeError(f"Firestore hatasi: {e}")

def _fs_patch(key, fields):
    mask = "&".join(f"updateMask.fieldPaths={k}" for k in fields.keys())
    url = f"{FIRESTORE_BASE}/keys/{urllib.parse.quote(key)}?{mask}&key={FIREBASE_API_KEY}"
    body = {"fields": {}}
    for k, v in fields.items():
        if isinstance(v, bool):
            body["fields"][k] = {"booleanValue": v}
        elif isinstance(v, int):
            body["fields"][k] = {"integerValue": str(v)}
        elif isinstance(v, str):
            body["fields"][k] = {"stringValue": v}
        elif isinstance(v, list):
            body["fields"][k] = {"arrayValue": {"values": [{"stringValue": str(x)} for x in v]}}
    data = json.dumps(body).encode()
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, data=data, method="PATCH", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
        return json.loads(r.read().decode())

def _fs_value(field):
    if "stringValue" in field:
        return field["stringValue"]
    if "integerValue" in field:
        return int(field["integerValue"])
    if "doubleValue" in field:
        return float(field["doubleValue"])
    if "booleanValue" in field:
        return field["booleanValue"]
    if "arrayValue" in field:
        return [_fs_value(v) for v in field["arrayValue"].get("values", [])]
    if "timestampValue" in field:
        return field["timestampValue"]
    return None

def validate_key(api_key, current_ip, chat_id=None):
    if not api_key or len(api_key) < 8:
        return False, "Geçersiz anahtar formatı.", 0, False, 20
    try:
        doc = _fs_get(api_key)
    except Exception as e:
        return False, f"Sunucu hatası: {e}", 0, False, 20
    if not doc or "fields" not in doc:
        return False, f"Anahtar bulunamadı. Destek: @{CONTACT_USERNAME}", 0, False, 20

    f = doc["fields"]
    active = _fs_value(f.get("active", {"booleanValue": True}))
    expires_ms = _fs_value(f.get("expiresAtMs", {"integerValue": "0"})) or 0
    is_free = _fs_value(f.get("isFree", {"booleanValue": False})) or False
    daily_limit = _fs_value(f.get("dailyCloneLimit", {"integerValue": "20"})) or 20
    user_limit = f.get("userLimit")
    user_limit_val = _fs_value(user_limit) if user_limit else None
    used_users = _fs_value(f.get("usedUsers", {"arrayValue": {"values": []}})) or []

    if not active:
        return False, f"Bu anahtar devre dışı. @{CONTACT_USERNAME}", 0, False, 20
    now_ms = int(time.time() * 1000)
    if expires_ms and now_ms > expires_ms:
        return False, f"Anahtar süresi dolmuş. @{CONTACT_USERNAME}", 0, False, 20

    if user_limit_val is not None and user_limit_val > 0:
        user_str = str(chat_id) if chat_id else current_ip
        if user_str not in used_users:
            if len(used_users) >= user_limit_val:
                return False, f"Kullanıcı limiti doldu ({len(used_users)}/{user_limit_val})", 0, False, 20
            try:
                _fs_patch(api_key, {"usedUsers": used_users + [user_str]})
            except Exception as e:
                return False, f"Kayıt hatası: {e}", 0, False, 20

    kalan = "Sınırsız"
    if expires_ms:
        kalan_gun = max(0, (expires_ms - now_ms) // (1000 * 60 * 60 * 24))
        kalan = f"{kalan_gun} gün"

    limit = daily_limit if is_free else PAID_DAILY_CLONE_LIMIT
    key_type = "Deneme" if is_free else "Premium"
    return True, f"Lisans doğrulandı ({key_type}, Kalan: {kalan})", expires_ms, is_free, limit

def check_saved_license(chat_id, current_ip):
    saved = _license_db.get(chat_id)
    if not saved:
        return False, "Kayıtlı lisans yok.", None
    api_key = saved["api_key"]
    ok, msg, expires_ms, is_free, daily_limit = validate_key(api_key, current_ip, chat_id)
    if ok:
        _license_db.save(chat_id, api_key, current_ip, expires_ms, is_free, daily_limit)
        return True, msg, api_key
    else:
        _license_db.delete(chat_id)
        return False, msg, None

# ═══════════════════════════════════════════════════════════
# BYTE CRYPTO
# ═══════════════════════════════════════════════════════════

def make_by_key(uid):
    chars = list(str(uid or ""))
    if len(chars) >= 9:
        chars[1], chars[8] = chars[8], chars[1]
    if len(chars) >= 3:
        chars.pop(2)
    if len(chars) >= 5:
        chars.append(chars[4])
    return "".join(chars).encode("utf-8") or b"0"

def by_xor(data, key):
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def by_decompress(data):
    try:
        return brotli.decompress(data)
    except:
        pass
    for args in ((zlib.MAX_WBITS | 16,), tuple()):
        try:
            return zlib.decompress(data, *args)
        except:
            pass
    return None

def _md5(t):
    return hashlib.md5(str(t).encode()).digest()

def _sha1(t):
    return hashlib.sha1(str(t).encode()).digest()[:16]

def by_decrypt_aes(data, key):
    try:
        cipher = AES.new(key[:16], AES.MODE_CBC, b"\x00" * 16)
        return unpad(cipher.decrypt(data), 16)
    except:
        return None

def by_build_aes_keys(uid, password=None, email=None):
    keys = [_md5("olzhas_carparking")]
    if password:
        keys += [_md5(password), _sha1(password)]
    if uid:
        keys += [_md5(uid), _sha1(uid)]
    if email:
        keys.append(_md5(email))
    return keys

class ByReader:
    def __init__(self, data):
        self.by_buf = data
        self.by_pos = 0

    def by_has(self, n):
        return self.by_pos + n <= len(self.by_buf)

    def by_byte(self):
        if not self.by_has(1):
            return 0
        v = self.by_buf[self.by_pos]
        self.by_pos += 1
        return v

    def by_i(self):
        if not self.by_has(4):
            self.by_pos = len(self.by_buf)
            return 0
        v = struct.unpack_from("<i", self.by_buf, self.by_pos)[0]
        self.by_pos += 4
        return v

    def by_f(self):
        if not self.by_has(4):
            self.by_pos = len(self.by_buf)
            return 0.0
        v = struct.unpack_from("<f", self.by_buf, self.by_pos)[0]
        self.by_pos += 4
        return v

    def by_s(self):
        m = self.by_i()
        if m in (0, -1):
            return ""
        ln = (-m) - 1 if m < -1 else m
        if m < -1:
            self.by_i()
        ln = max(0, min(ln, 1000000))
        if not self.by_has(ln):
            return ""
        t = self.by_buf[self.by_pos:self.by_pos + ln].decode("utf-8", errors="replace")
        self.by_pos += ln
        return t.replace("\x00", "").strip()

    def by_lst(self, fn):
        n = self.by_i()
        if n <= 0 or n > 1000000:
            return []
        out = []
        for _ in range(n):
            if self.by_pos >= len(self.by_buf):
                break
            v = fn()
            if v is not None:
                out.append(v)
        return out

    def by_dct(self):
        n = self.by_i()
        if n <= 0 or n > 1000000:
            return {}
        out = {}
        for _ in range(n):
            if self.by_pos >= len(self.by_buf):
                break
            out[self.by_i()] = self.by_i()
        return out

    def by_equip(self):
        if self.by_byte() == 0:
            return None
        keys = ["hair", "face", "beard", "cap", "mask", "top", "gloves", "bag", "pants", "shoes", "glasses", "SelectedEquipments"]
        d = {k: self.by_lst(self.by_i) for k in keys}
        d["Gender"] = self.by_i()
        return d

def by_parse_player(buf):
    r = ByReader(buf)
    if r.by_byte() == 0:
        return None
    p = {}
    p["Name"] = r.by_s()
    p["money"] = r.by_i()
    p["coin"] = r.by_i()
    p["localID"] = r.by_s()
    p["boughtFsos"] = r.by_lst(r.by_i)
    p["FriendsID"] = r.by_lst(lambda: (r.by_byte(), {"id": r.by_s(), "Name": r.by_s(), "accountID": r.by_s()})[1])
    p["LevelsDoneTime"] = r.by_lst(r.by_f)
    p["floats"] = r.by_lst(r.by_f)
    p["integers"] = r.by_lst(r.by_i)
    p["fcar"] = r.by_lst(r.by_i)
    p["favouriteWheels"] = r.by_lst(r.by_i)
    p["favouriteVinyls"] = r.by_lst(r.by_i)
    p["favouriteEmojis"] = r.by_lst(r.by_i)
    p["personEquipmentsMale"] = r.by_equip()
    p["personEquipmentsFemale"] = r.by_equip()

    if r.by_byte() == 0:
        p["platesData"] = None
    else:
        def rv():
            fc = r.by_byte()
            return {"_fieldCount": fc, "vectors": r.by_lst(lambda: {"x": r.by_f(), "y": r.by_f(), "z": r.by_f()}), "v": r.by_lst(r.by_s), "floats": r.by_lst(r.by_f), "text": r.by_s()}

        def rp():
            fc = r.by_byte()
            return {"_fieldCount": fc, "plateId": r.by_i(), "frontCarId": r.by_i(), "rearCarId": r.by_i(), "vinyls": r.by_lst(rv)}

        p["platesData"] = {"allPlates": r.by_lst(rp)}

    if r.by_byte() == 0:
        p["carIDnStatus"] = None
    else:
        p["carIDnStatus"] = {"carGeneratedIDs": r.by_lst(r.by_s), "carStatus": r.by_lst(r.by_i)}

    p["allData"] = r.by_s()
    p["flags"] = r.by_dct()
    p["animations"] = r.by_lst(r.by_i)
    p["emojiPacks"] = r.by_lst(r.by_i)
    p["wheels"] = r.by_lst(r.by_i)
    p["boughtPoliceLights"] = r.by_lst(r.by_i)
    p["boughtPoliceSirens"] = r.by_lst(r.by_i)
    return p

def by_try_parse(buf):
    cands = [buf]
    d1 = by_decompress(buf)
    if d1:
        cands.append(d1)
        d2 = by_decompress(d1)
        if d2:
            cands.append(d2)
    for c in cands:
        if not c:
            continue
        if c[0] in (17, 23, 24):
            try:
                p = by_parse_player(c)
                if p and p.get("Name") is not None:
                    return p
            except:
                pass
        try:
            clean = c[3:] if len(c) >= 3 and c[:2] == b"\xef\xbb" else c
            if clean and clean[0] == 123:
                return json.loads(clean.decode("utf-8"))
        except:
            pass
    return None

def by_decrypt_record(b64_text, uid, password=None, email=None):
    try:
        buf = base64.b64decode(b64_text)
    except:
        return {"success": False, "message": "bad_base64"}
    if len(buf) < 10:
        return {"success": False, "message": "too_small"}
    direct = by_try_parse(buf)
    if direct:
        return {"success": True, "record": direct}
    try:
        decoded = by_decompress(by_xor(buf, make_by_key(uid)))
        if decoded:
            p = by_try_parse(decoded)
            if p:
                return {"success": True, "record": p}
    except:
        pass
    for k in by_build_aes_keys(uid, password, email):
        plain = by_decrypt_aes(buf, k)
        if not plain:
            continue
        p = by_try_parse(plain)
        if p:
            return {"success": True, "record": p}
    return {"success": False, "message": "decrypt_failed"}

class ByWriter:
    def __init__(self):
        self.by_parts = []

    def by_byte(self, v):
        self.by_parts.append(bytes([int(v or 0) & 0xFF]))

    def by_i(self, v):
        self.by_parts.append(struct.pack("<i", int(v or 0)))

    def by_f(self, v):
        self.by_parts.append(struct.pack("<f", float(v or 0.0)))

    def by_s(self, s):
        if s is None:
            self.by_parts.append(struct.pack("<i", -1))
            return
        s = str(s)
        if s == "":
            self.by_parts.append(struct.pack("<i", 0))
            return
        enc = s.encode("utf-8")
        self.by_parts.append(struct.pack("<ii", -len(enc) - 1, len(s)) + enc)

    def by_lst(self, l, fn):
        if l is None:
            self.by_parts.append(struct.pack("<i", -1))
            return
        self.by_parts.append(struct.pack("<i", len(l)))
        for x in l:
            fn(x)

    def by_equip(self, d):
        if not d:
            self.by_byte(0)
            return
        self.by_byte(13)
        keys = ["hair", "face", "beard", "cap", "mask", "top", "gloves", "bag", "pants", "shoes", "glasses", "SelectedEquipments"]
        for k in keys:
            self.by_lst(d.get(k, []), self.by_i)
        self.by_i(d.get("Gender", 0))

    def by_plates(self, d):
        if not d:
            self.by_byte(0)
            return
        self.by_byte(1)
        pl = d.get("allPlates", [])
        self.by_parts.append(struct.pack("<i", len(pl)))
        for p in pl:
            self.by_byte(int(p.get("_fieldCount", 4) or 4))
            self.by_i(p.get("plateId", 0))
            self.by_i(p.get("frontCarId", 0))
            self.by_i(p.get("rearCarId", 0))
            vs = p.get("vinyls", [])
            self.by_parts.append(struct.pack("<i", len(vs)))
            for v in vs:
                self.by_byte(int(v.get("_fieldCount", 4) or 4))
                vecs = v.get("vectors", [])
                self.by_parts.append(struct.pack("<i", len(vecs)))
                for vec in vecs:
                    self.by_parts.append(struct.pack("<fff", float(vec.get("x", 0) or 0), float(vec.get("y", 0) or 0), float(vec.get("z", 0) or 0)))
                self.by_lst(v.get("v", []), self.by_s)
                self.by_lst(v.get("floats", []), self.by_f)
                self.by_s(v.get("text", ""))

    def by_carstat(self, d):
        if not d:
            self.by_byte(0)
            return
        self.by_byte(2)
        self.by_lst(d.get("carGeneratedIDs", []), self.by_s)
        self.by_lst(d.get("carStatus", []), self.by_i)

    def by_to_bytes(self):
        return b"".join(self.by_parts)

FIELD_MAP = [
    (1, "localID"), (2, "money"), (3, "Name"), (4, "coin"), (5, "allData"),
    (6, "boughtFsos"), (7, "boughtPoliceLights"), (8, "boughtPoliceSirens"),
    (9, "FriendsID"), (10, "LevelsDoneTime"), (11, "floats"), (12, "integers"),
    (13, "fcar"), (14, "favouriteWheels"), (15, "favouriteVinyls"),
    (16, "favouriteEmojis"), (18, "emojiPacks"),
    (41, "personEquipmentsMale"), (42, "personEquipmentsFemale"),
    (43, "platesData"), (44, "carIDnStatus"), (45, "flags"),
    (46, "animations"), (48, "wheels"),
]
INT_LIST = {6, 7, 8, 12, 13, 14, 15, 16, 18, 46, 48}
FLOAT_LIST = {10, 11}

def by_serialize(fid, v):
    w = ByWriter()
    if fid in (1, 3, 5):
        w.by_s(v)
        return w.by_to_bytes()
    if fid in (2, 4):
        w.by_i(v or 0)
        return w.by_to_bytes()
    if fid == 9:
        fr = v or []
        w.by_parts.append(struct.pack("<i", len(fr)))
        for f in fr:
            f = f or {}
            w.by_byte(3)
            w.by_s(f.get("id", ""))
            w.by_s(f.get("Name", ""))
            w.by_s(f.get("accountID", ""))
        return w.by_to_bytes()
    if fid in INT_LIST:
        w.by_lst(v or [], w.by_i)
        return w.by_to_bytes()
    if fid in FLOAT_LIST:
        w.by_lst(v or [], w.by_f)
        return w.by_to_bytes()
    if fid in (41, 42):
        w.by_equip(v)
        return w.by_to_bytes()
    if fid == 43:
        w.by_plates(v)
        return w.by_to_bytes()
    if fid == 44:
        w.by_carstat(v)
        return w.by_to_bytes()
    if fid == 45:
        fl = v or {}
        w.by_parts.append(struct.pack("<i", len(fl)))
        for k, val in fl.items():
            w.by_i(int(k))
            w.by_i(int(val))
        return w.by_to_bytes()
    return None

def by_build_payload(record, uid, force_fields=None):
    force = set(force_fields or [])
    fields = []
    for fid, key in FIELD_MAP:
        if key not in force:
            continue
        v = record.get(key)
        if v is None:
            continue
        raw = by_serialize(fid, v)
        if raw is not None:
            fields.append((fid, raw))
    parts = [struct.pack("<i", len(fields))]
    for fid, raw in fields:
        parts.append(struct.pack("<hi", fid, len(raw)))
        parts.append(raw)
    combined = b"".join(parts)
    compressed = brotli.compress(combined)
    encrypted = by_xor(compressed, make_by_key(uid))
    return base64.b64encode(encrypted).decode("ascii")

# ═══════════════════════════════════════════════════════════
# TOOL API
# ═══════════════════════════════════════════════════════════

def tool_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FK}"
    h = {"Content-Type": "application/json", "User-Agent": "UnityPlayer/2022.3.62f2", "X-Unity-Version": "2022.3.62f2"}
    payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
    try:
        r = requests.post(url, json=payload, headers=h, timeout=30, verify=False)
        data = r.json()
    except Exception as e:
        return {"ok": False, "msg": f"network: {e}"}
    if "idToken" in data:
        return {"ok": True, "auth": data["idToken"], "fuid": data.get("localId", "")}
    return {"ok": False, "msg": str(data.get("error", {}).get("message", "")).upper() or "login_failed"}

def tool_fetch_record(auth, fuid):
    h = {**GAME_HEADERS, "Authorization": f"Bearer {auth}"}
    try:
        r = requests.post(LOAD_URL, json={"data": {"data": fuid}}, headers=h, timeout=30, verify=False)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def tool_find_encrypted(resp):
    if not resp:
        return None
    if isinstance(resp, str):
        return resp if len(resp) > 50 else None
    if isinstance(resp, dict):
        for k in ("result", "data", "record", "PlayerRecord"):
            v = resp.get(k)
            if isinstance(v, str) and len(v) > 50:
                return v
            if isinstance(v, dict):
                r = tool_find_encrypted(v)
                if r:
                    return r
    return None

def _ok(v):
    if v in (1, True):
        return True
    if v in (0, False, None):
        return False
    if isinstance(v, str):
        if v.strip() == "1":
            return True
        if v.strip() == "0":
            return False
        try:
            return _ok(json.loads(v))
        except:
            return False
    if isinstance(v, dict):
        for k in ("result", "ok", "success"):
            if k in v:
                return _ok(v[k])
    return False

def tool_save_record(auth, fuid, record, force_fields):
    payload = by_build_payload(record, fuid, force_fields)
    h = {**GAME_HEADERS, "Authorization": f"Bearer {auth}"}
    body = {"data": {"data": payload, "deviceId": fuid[:8]}}
    try:
        r = requests.post(SAVE_URL, json=body, headers=h, timeout=30, verify=False)
        return {"ok": _ok(r.json()), "resp": r.text}
    except Exception as e:
        return {"ok": False, "msg": str(e)}

# ═══════════════════════════════════════════════════════════
# CLONE SİSTEMİ
# ═══════════════════════════════════════════════════════════

class CloneDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS tokens (
                user_id INTEGER PRIMARY KEY,
                auth_token TEXT, email TEXT, password TEXT,
                refresh_token TEXT, firebase_uid TEXT,
                token_expires_at REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            c.commit()

    def _post_sync(self, url, payload, headers):
        try:
            clean_headers = {k: v for k, v in headers.items() if k.lower() != "host"}
            r = requests.post(url, json=payload, headers=clean_headers, timeout=60, verify=False)
            try:
                return r.json()
            except:
                return {"raw": r.text, "status": r.status_code}
        except Exception:
            return None

    def login(self, email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FK}"
        headers = {"Accept": "*/*", "Content-Type": "application/json", "User-Agent": "UnityPlayer/2022.3.62f2", "X-Unity-Version": "2022.3.62f2"}
        payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
        result = self._post_sync(url, payload, headers)
        if not result:
            return {"ok": False, "message": "NETWORK_ERROR"}
        if "idToken" in result:
            return {"ok": True, "message": "OK", "auth": result["idToken"], "refresh_token": result.get("refreshToken", ""), "firebase_uid": result.get("localId", "")}
        err = str(result.get("error", {}).get("message", "")).upper()
        return {"ok": False, "message": f"LOGIN_FAILED: {err[:80]}"}

    def _ok(self, value):
        if value in (1, True):
            return True
        if value in (0, False, None):
            return False
        if isinstance(value, str):
            text = value.strip()
            if text == "1":
                return True
            if text == "0":
                return False
            try:
                return self._ok(json.loads(text))
            except:
                return False
        if isinstance(value, dict):
            for key in ("result", "ok", "success"):
                if key in value:
                    return self._ok(value[key])
        return False

    def _send(self, auth, record, fuid, original=None, force_fields=None):
        if not fuid:
            return False, "NO_FIREBASE_UID"
        try:
            payload = clone_build_payload(record, fuid, original, force_fields=force_fields)
            result = self._post_sync(SAVE_URL, {"data": {"data": payload, "deviceId": fuid[:8]}},
                {**GAME_HEADERS, "Authorization": f"Bearer {auth}", "Connection": "Keep-Alive", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12)"})
            if result and self._ok(result):
                return True, "OK"
            return False, f"SAVE_FAILED: {str(result)[:160]}"
        except Exception as exc:
            return False, str(exc)

    def create_account(self, email, password, display_name="Player"):
        email = (email or "").strip().lower()
        password = (password or "").strip()
        display_name = (display_name or "Player").strip()[:32] or "Player"
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FK}"
        h = {"Accept": "*/*", "Content-Type": "application/json", "User-Agent": "UnityPlayer/2022.3.62f2", "X-Unity-Version": "2022.3.62f2"}
        payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
        try:
            r = requests.post(url, json=payload, headers=h, timeout=60, verify=False)
            data = r.json()
        except:
            return {"ok": False, "message": "NETWORK_ERROR"}

        if "idToken" not in data:
            return {"ok": False, "message": "SIGNUP_FAILED"}

        auth = data["idToken"]
        fuid = data.get("localId", "")
        local_id = (fuid[:8] if fuid else "".join(random.choice("0123456789ABCDEF") for _ in range(8))).upper()

        record = {
            "Name": display_name, "money": 50_000_000, "coin": 30_000, "localID": local_id,
            "boughtFsos": [], "FriendsID": [], "LevelsDoneTime": [], "floats": [0.0] * 54,
            "integers": [0] * 120, "fcar": [], "favouriteWheels": [], "favouriteVinyls": [],
            "favouriteEmojis": [], "personEquipmentsMale": None, "personEquipmentsFemale": None,
            "platesData": None, "carIDnStatus": None, "allData": "", "flags": {},
            "animations": [], "emojiPacks": [], "wheels": [], "boughtPoliceLights": [], "boughtPoliceSirens": [],
        }
        try:
            self._send(auth, record, fuid, original=None)
        except:
            pass

        return {"ok": True, "auth": auth, "firebase_uid": fuid, "email": email, "localID": local_id, "Name": display_name}

class CloneWriter:
    def __init__(self):
        self._p = []

    def write_byte(self, v):
        self._p.append(bytes([int(v or 0) & 0xFF]))

    def write_int(self, v):
        self._p.append(struct.pack("<i", int(v or 0)))

    def write_float(self, v):
        self._p.append(struct.pack("<f", float(v or 0.0)))

    def write_string(self, s):
        if s is None:
            self._p.append(struct.pack("<i", -1))
            return
        s = str(s)
        if s == "":
            self._p.append(struct.pack("<i", 0))
            return
        enc = s.encode("utf-8")
        self._p.append(struct.pack("<ii", -(len(enc)) - 1, len(s)) + enc)

    def write_list(self, lst, fn):
        if lst is None:
            self._p.append(struct.pack("<i", -1))
            return
        self._p.append(struct.pack("<i", len(lst)))
        for item in lst:
            fn(item)

    def write_equipment(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(13)
        for key in ["hair", "face", "beard", "cap", "mask", "top", "gloves", "bag", "pants", "shoes", "glasses", "SelectedEquipments"]:
            self.write_list(data.get(key, []), self.write_int)
        self.write_int(data.get("Gender", 0))

    def write_plates(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(1)
        plates = data.get("allPlates", [])
        self._p.append(struct.pack("<i", len(plates)))
        for plate in plates:
            self.write_byte(int(plate.get("_fieldCount", 4) or 4))
            self.write_int(plate.get("plateId", 0))
            self.write_int(plate.get("frontCarId", 0))
            self.write_int(plate.get("rearCarId", 0))
            vinyls = plate.get("vinyls", [])
            self._p.append(struct.pack("<i", len(vinyls)))
            for vinyl in vinyls:
                self.write_byte(int(vinyl.get("_fieldCount", 4) or 4))
                vecs = vinyl.get("vectors", [])
                self._p.append(struct.pack("<i", len(vecs)))
                for vec in vecs:
                    self._p.append(struct.pack("<fff", float(vec.get("x", 0) or 0), float(vec.get("y", 0) or 0), float(vec.get("z", 0) or 0)))
                self.write_list(vinyl.get("v", []), self.write_string)
                self.write_list(vinyl.get("floats", []), self.write_float)
                self.write_string(vinyl.get("text", ""))

    def write_car_id_status(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(2)
        self.write_list(data.get("carGeneratedIDs", []), self.write_string)
        self.write_list(data.get("carStatus", []), self.write_int)

    def to_bytes(self):
        return b"".join(self._p)

def _field_modified(new_value, old_value):
    if new_value is None and old_value is None:
        return False
    if new_value is None or old_value is None:
        return True
    if type(new_value) != type(old_value):
        return True
    if isinstance(new_value, (dict, list)):
        return json.dumps(new_value, sort_keys=True) != json.dumps(old_value, sort_keys=True)
    return new_value != old_value

def clone_serialize_field(fid, value):
    w = CloneWriter()
    if fid in (1, 3, 5):
        w.write_string(value)
        return w.to_bytes()
    if fid in (2, 4):
        w.write_int(value or 0)
        return w.to_bytes()
    if fid == 9:
        friends = value or []
        w._p.append(struct.pack("<i", len(friends)))
        for friend in friends:
            friend = friend or {}
            w.write_byte(3)
            w.write_string(friend.get("id", ""))
            w.write_string(friend.get("Name", ""))
            w.write_string(friend.get("accountID", ""))
        return w.to_bytes()
    if fid in INT_LIST:
        w.write_list(value or [], w.write_int)
        return w.to_bytes()
    if fid in FLOAT_LIST:
        w.write_list(value or [], w.write_float)
        return w.to_bytes()
    if fid in (41, 42):
        w.write_equipment(value)
        return w.to_bytes()
    if fid == 43:
        w.write_plates(value)
        return w.to_bytes()
    if fid == 44:
        w.write_car_id_status(value)
        return w.to_bytes()
    if fid == 45:
        flags = value or {}
        w._p.append(struct.pack("<i", len(flags)))
        for key, val in flags.items():
            w.write_int(int(key))
            w.write_int(int(val))
        return w.to_bytes()
    return None

def clone_build_payload(record, uid, original=None, force_fields=None):
    force_fields = set(force_fields or [])
    fields = []
    for fid, key in FIELD_MAP:
        value = record.get(key)
        if value is None:
            continue
        if key == "allData":
            should_send = isinstance(value, str) and len(value) > 0
        elif key in force_fields:
            should_send = True
        elif original is not None:
            should_send = _field_modified(value, original.get(key))
        else:
            should_send = True
        if not should_send:
            continue
        raw = clone_serialize_field(fid, value)
        if raw is not None:
            fields.append((fid, raw))
    parts = [struct.pack("<i", len(fields))]
    for fid, raw in fields:
        parts.append(struct.pack("<hi", fid, len(raw)))
        parts.append(raw)
    combined = b"".join(parts)
    compressed = brotli.compress(combined)
    encrypted = by_xor(compressed, make_by_key(uid))
    return base64.b64encode(encrypted).decode("ascii")

CPM_FIELD_NAMES = {
    1: 'CarID', 2: 'dataVersion', 3: 'vectors', 4: 'floats', 5: 'gears',
    6: 'typeToInstall', 7: 'BoughtParts', 8: 'texts', 9: 'flagID',
    10: 'fsoData', 11: 'installedPoliceLights', 12: 'Vynils', 13: 'WindowVinyls',
}

http_session = requests.Session()
http_session.verify = True
_cpm_thread_local = threading.local()

def _get_cpm_http_session():
    session = getattr(_cpm_thread_local, "session", None)
    if session is None:
        session = requests.Session()
        session.verify = True
        _cpm_thread_local.session = session
    return session

def cpm1_ios_headers(token):
    return {
        'accept': '*/*', 'authorization': f'Bearer {token}', 'content-type': 'application/json; charset=utf-8',
        'user-agent': 'CarParking/265 CFNetwork/3860.600.12 Darwin/25.5.0', 'x-client-platform': 'IOS',
        'x-client-version': '4.9.10', 'x-client-deviceid': str(uuid.uuid4()).upper(), 'x-request-nonce': str(uuid.uuid4()),
        'x-unity-version': '2022.3.62f2', 'accept-encoding': 'gzip', 'connection': 'Keep-Alive',
    }

def cpm1_write_memorypack_string(s):
    if s is None or s == "":
        return struct.pack("<i", 0)
    sb = str(s).encode("utf-8")
    return struct.pack("<ii", -len(sb) - 1, len(sb)) + sb

def cpm1_looks_like_base64(val):
    if not isinstance(val, str):
        return False
    if len(val) < 4 or len(val) % 4 != 0:
        return False
    return bool(re.match(r'^[A-Za-z0-9+/]+={0,2}$', val))

def cpm1_deserialize_string_list(b64):
    if not b64 or not isinstance(b64, str):
        return []
    try:
        compressed = base64.b64decode(b64)
    except:
        return []
    try:
        decompressed = brotli.decompress(compressed)
    except:
        try:
            decompressed = zlib.decompress(compressed, zlib.MAX_WBITS | 16)
        except:
            decompressed = compressed
    if not decompressed or len(decompressed) < 4:
        return []
    out = []
    pos = 4
    count = struct.unpack_from("<i", decompressed, 0)[0]
    if count <= 0 or count > 100000:
        return []
    for _ in range(count):
        if pos + 4 > len(decompressed):
            break
        marker = struct.unpack_from("<i", decompressed, pos)[0]
        pos += 4
        if marker == 0:
            out.append("")
            continue
        if marker == -1:
            break
        if marker < -1:
            byte_len = -marker - 1
            if pos + 4 > len(decompressed):
                break
            pos += 4
        else:
            byte_len = marker
        if pos + byte_len > len(decompressed):
            break
        s = decompressed[pos:pos + byte_len].decode("utf-8", errors="replace")
        pos += byte_len
        out.append(s.replace("\x00", "").strip())
    return out

def cpm1_generate_random_cpm_id():
    L = string.ascii_uppercase
    D = string.digits
    return ''.join(random.choice(L) for _ in range(2)) + ''.join(random.choice(D) for _ in range(6))

def cpm1_generated_id_from_car(car):
    for k in ("generatedID", "generatedId", "carGeneratedID", "carGeneratedId"):
        v = car.get(k)
        if v and isinstance(v, str):
            return v
    texts = car.get("texts")
    if isinstance(texts, str):
        try:
            texts = cpm1_deserialize_string_list(texts)
        except:
            texts = []
    if isinstance(texts, list):
        for v in texts:
            if v and isinstance(v, str) and '_' in v and re.search(r'\d', v):
                return v
    return None

def cpm1_build_car_entries(cars, cpm_id):
    entries = []
    for car in cars:
        try:
            cid = int(car.get("CarID"))
        except:
            continue
        if cid < 0:
            continue
        gen = cpm1_generated_id_from_car(car) or f"{cpm_id}_{cid}XX000"
        entries.append([cid, gen])
    return entries

def cpm1_entries_to_sparse(car_entries):
    if not car_entries:
        return {"carGeneratedIDs": [], "carStatus": []}
    ids = [int(e[0]) for e in car_entries if int(e[0]) >= 0]
    if not ids:
        return {"carGeneratedIDs": [], "carStatus": []}
    max_id = max(ids)
    gen_ids = [''] * (max_id + 1)
    statuses = [0] * (max_id + 1)
    for e in car_entries:
        cid = int(e[0])
        if 0 <= cid <= max_id:
            gen_ids[cid] = str(e[1]) if e[1] is not None else ''
            statuses[cid] = 1
    return {"carGeneratedIDs": gen_ids, "carStatus": statuses}

def cpm1_replace_uid_in_value(value, src_uid, tgt_uid):
    if not src_uid or src_uid == tgt_uid:
        return value
    if isinstance(value, str):
        if cpm1_looks_like_base64(value):
            return value
        return value.replace(str(src_uid), str(tgt_uid))
    if isinstance(value, list):
        return [cpm1_replace_uid_in_value(v, src_uid, tgt_uid) for v in value]
    if isinstance(value, dict):
        return {k: cpm1_replace_uid_in_value(v, src_uid, tgt_uid) for k, v in value.items()}
    return value

def cpm1_prepare_car(stock_car, cpm_id, new_car_id=None):
    car_copy = json.loads(json.dumps(stock_car))
    car_id = int(car_copy.get("CarID") or 0)
    if new_car_id is not None:
        car_id = int(new_car_id)
        car_copy["CarID"] = car_id
    if isinstance(car_copy.get("Vynils"), dict):
        car_copy["Vynils"]["CarID"] = car_id
    texts = car_copy.get("texts")
    if isinstance(texts, str):
        try:
            texts = cpm1_deserialize_string_list(texts)
        except:
            texts = []
    if not isinstance(texts, list):
        texts = []
    while len(texts) < 4:
        texts.append('')
    orig = texts[2]
    if isinstance(orig, str) and '_' in orig:
        texts[2] = f"{cpm_id}_" + "_".join(orig.split('_')[1:])
    else:
        texts[2] = f"{cpm_id}_{car_id}XX000"
    car_copy["texts"] = texts
    return car_copy

def cpm1_sanitize_car_for_encoding(car):
    clean = {}
    for key, value in car.items():
        if isinstance(value, str) and cpm1_looks_like_base64(value):
            clean[key] = value
            continue
        if key == 'floats':
            arr = value if isinstance(value, list) else []
            clean[key] = [float(v) for v in arr] + [0.0] * (48 - len(arr))
        elif key == 'gears':
            arr = value if isinstance(value, list) else []
            clean[key] = [float(v) if v is not None else -10.0 for v in arr]
        elif key == 'vectors':
            arr = value if isinstance(value, list) else []
            clean[key] = [{'x': float(v.get('x') or 0), 'y': float(v.get('y') or 0), 'z': float(v.get('z') or 0)} if isinstance(v, dict) else {'x': 0, 'y': 0, 'z': 0} for v in arr]
        elif key in ('typeToInstall', 'BoughtParts', 'fsoData', 'installedPoliceLights'):
            arr = value if isinstance(value, list) else []
            clean[key] = [int(v) for v in arr if v is not None]
        elif key == 'texts':
            arr = value if isinstance(value, list) else []
            clean[key] = [str(v) if v is not None else '' for v in arr]
        elif key == 'Vynils':
            if isinstance(value, dict) and isinstance(value.get('allVynils'), list):
                nv = {'_fieldCount': int(value.get('_fieldCount', 2)), 'allVynils': [], 'CarID': int(car.get('CarID', 0))}
                for vinyl in value['allVynils']:
                    if not isinstance(vinyl, dict):
                        continue
                    cv = {'_fieldCount': int(vinyl.get('_fieldCount', 6))}
                    for fn in ('position', 'scaleRotation', 'iconPosition'):
                        vec = vinyl.get(fn) or {}
                        cv[fn] = {'x': float(vec.get('x') or 0), 'y': float(vec.get('y') or 0), 'z': float(vec.get('z') or 0)} if isinstance(vec, dict) else {'x': 0, 'y': 0, 'z': 0}
                    cv['text'] = str(vinyl.get('text', '') or '')
                    cv['color'] = int(vinyl.get('color', 0) or 0)
                    cv['packedData'] = int(vinyl.get('packedData', 0) or 0)
                    nv['allVynils'].append(cv)
                clean[key] = nv
            else:
                clean[key] = value
        elif key in ('CarID', 'dataVersion', 'flagID'):
            clean[key] = int(value) if value is not None else 0
        else:
            clean[key] = value
    return clean

def cpm1_encode_field_value_binary(name, value):
    if name == 'vectors':
        buf = struct.pack("<i", len(value))
        for vec in value:
            buf += struct.pack("<fff", vec['x'], vec['y'], vec['z'])
        return buf
    if name in ('floats', 'gears'):
        buf = struct.pack("<i", len(value))
        for v in value:
            buf += struct.pack("<f", v)
        return buf
    if name in ('typeToInstall', 'BoughtParts', 'fsoData', 'installedPoliceLights'):
        buf = struct.pack("<i", len(value))
        for v in value:
            buf += struct.pack("<i", v)
        return buf
    if name == 'texts':
        buf = struct.pack("<i", len(value))
        for v in value:
            buf += cpm1_write_memorypack_string(v)
        return buf
    if name == 'Vynils':
        if not isinstance(value, dict) or not isinstance(value.get('allVynils'), list):
            return b""
        fc = int(value.get('_fieldCount', 2))
        parts = [bytes([fc & 0xFF])]
        if fc == 0:
            return b"".join(parts)
        parts.append(struct.pack("<i", len(value['allVynils'])))
        for vinyl in value['allVynils']:
            vfc = int(vinyl.get('_fieldCount', 6))
            parts.append(bytes([vfc & 0xFF]))
            if vfc == 0:
                continue
            for fn in ('position', 'scaleRotation', 'iconPosition'):
                parts.append(struct.pack("<fff", vinyl[fn]['x'], vinyl[fn]['y'], vinyl[fn]['z']))
            parts.append(cpm1_write_memorypack_string(vinyl['text']))
            parts.append(struct.pack("<I", vinyl['color'] & 0xFFFFFFFF))
            parts.append(struct.pack("<q", vinyl['packedData']))
        if fc >= 2:
            parts.append(struct.pack("<i", value.get('CarID', 0)))
        return b"".join(parts)
    return b""

def cpm1_encode_car_to_memorypack(car):
    fields = [(fid, name, car[name]) for fid, name in CPM_FIELD_NAMES.items() if name in car and car[name] is not None]
    fields.sort(key=lambda x: x[0])
    parts = [struct.pack("<i", len(fields))]
    for fid, name, value in fields:
        parts.append(struct.pack("<h", fid))
        if name in ('CarID', 'dataVersion', 'flagID'):
            parts.append(cpm1_write_memorypack_string(str(int(value))))
        elif isinstance(value, str) and cpm1_looks_like_base64(value):
            parts.append(cpm1_write_memorypack_string(value))
        else:
            binv = cpm1_encode_field_value_binary(name, value)
            compressed = brotli.compress(binv, quality=4)
            parts.append(cpm1_write_memorypack_string(base64.b64encode(compressed).decode('ascii')))
    return b"".join(parts)

def cpm1_encrypt_car_for_save(car, uid):
    clean = cpm1_sanitize_car_for_encoding(car)
    mp = cpm1_encode_car_to_memorypack(clean)
    compressed = brotli.compress(mp, quality=4)
    return "__ver1__" + base64.b64encode(by_xor(compressed, make_by_key(uid))).decode('ascii')

def cpm1_fetch_cars_v2(token):
    try:
        resp = http_session.post(CPM_CARS_FETCH_URL, json={"data": ""}, headers=cpm1_ios_headers(token), timeout=20, verify=False)
        if resp.status_code < 200 or resp.status_code >= 300:
            return {"success": False, "error": f"HTTP {resp.status_code}", "cars": []}
        parsed = resp.json() if resp.text else {}
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        raw_result = parsed.get("result") or parsed.get("data", {}).get("result") if isinstance(parsed, dict) else None
        if raw_result is None:
            return {"success": True, "cars": []}
        cars = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
        if not isinstance(cars, list):
            cars = []
        return {"success": True, "cars": cars}
    except Exception as e:
        return {"success": False, "error": str(e), "cars": []}

def cpm1_save_car_encrypted_v2(token, car, uid, retries=2):
    try:
        payload = cpm1_encrypt_car_for_save(car, uid)
    except Exception as e:
        return {"success": False, "error": str(e)}
    headers = cpm1_ios_headers(token)
    for attempt in range(1, retries + 1):
        try:
            resp = _get_cpm_http_session().post(CPM_CARS_SAVE_URL, json={"data": payload}, headers=headers, timeout=8, verify=False)
            if resp.status_code < 300:
                return {"success": True, "status": resp.status_code, "data": resp.text}
        except:
            pass
        time.sleep(1)
    return {"success": False, "error": "max_retries"}

def cpm1_save_car_status(auth, fuid, car_entries):
    sparse = cpm1_entries_to_sparse(car_entries)
    record = {"carIDnStatus": {"carGeneratedIDs": sparse["carGeneratedIDs"], "carStatus": sparse["carStatus"]}}
    try:
        payload = clone_build_payload(record, fuid, original=None, force_fields={"carIDnStatus"})
        headers = {**GAME_HEADERS, "Authorization": f"Bearer {auth}", "Connection": "Keep-Alive"}
        r = requests.post(SAVE_URL, json={"data": {"data": payload, "deviceId": fuid[:8]}}, headers=headers, timeout=30, verify=False)
        return {"success": r.status_code == 200, "message": "OK" if r.status_code == 200 else f"HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

_clone_nuker = CloneDB(DB_PATH)

# ═══════════════════════════════════════════════════════════
# TELEGRAM BOT
# ═══════════════════════════════════════════════════════════

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

USER_SESSIONS = {}
TEMP_MSG_IDS = {}

def get_session(chat_id):
    if chat_id not in USER_SESSIONS:
        USER_SESSIONS[chat_id] = {
            "key_valid": False,
            "is_free": False,
            "daily_limit": (ADMIN_DAILY_CLONE_LIMIT if chat_id == ADMIN_ID else PAID_DAILY_CLONE_LIMIT),
            "auth": None, "fuid": None, "record": None,
            "email": None, "password": None,
            "name": None, "money": 0, "coin": 0,
            "state": None,
            "clone_results": [],
            "clone_in_progress": False,
            "lang": _user_settings.get_lang(chat_id) or "tr",
        }
    return USER_SESSIONS[chat_id]

def L(chat_id, key, **kwargs):
    lang = _user_settings.get_lang(chat_id) or "tr"
    return t(lang, key, **kwargs)

# ─── MENÜLER ───

def main_menu_inline(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Hesap Kopyala", callback_data="menu_clone"))
    markup.add(
        InlineKeyboardButton("Dil", callback_data="change_lang"),
        InlineKeyboardButton("Destek", callback_data="menu_contact"),
    )
    return markup

def lang_menu_inline():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("Türkçe", callback_data="lang_tr"),
        InlineKeyboardButton("English", callback_data="lang_en"),
        InlineKeyboardButton("Русский", callback_data="lang_ru"),
    )
    markup.add(InlineKeyboardButton("Ana Menü", callback_data="back_main"))
    return markup

def cancel_inline():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("İptal", callback_data="cancel_action"))
    return markup

def back_main_inline():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Ana Menü", callback_data="back_main"))
    return markup

def safe_delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

# ─── KANAL KONTROLÜ (SADECE ÜYELİK) ───

def check_channel_membership(chat_id):
    """
    Admin her zaman True.
    Diğer kullanıcılar için: tüm zorunlu kanallara üye olmalı.
    Yönetici olma zorunluluğu YOK.
    """
    if chat_id == ADMIN_ID:
        return True, None

    channels = _config_db.list_channels()
    if not channels:
        return True, None

    for ch in channels:
        channel_id = ch["channel_id"]
        invite_link = ch["invite_link"]
        try:
            member = bot.get_chat_member(channel_id, chat_id)
            status = member.status
            if status in ("left", "kicked"):
                return False, ("not_joined", invite_link)
            # member / administrator / creator / restricted → üye kabul
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ("user not found", "participant", "chat not found", "bad request")):
                return False, ("not_joined", invite_link)
            print(f"Kanal kontrol hatası ({channel_id}): {e}")
            continue
    return True, None

def send_channel_required_message(chat_id, reason, invite_link):
    text = L(chat_id, "channel_sub_required", channel_url=invite_link)
    bot.send_message(chat_id, text, disable_web_page_preview=False)

# ─── WELCOME ───

def send_welcome_message(chat_id, note=""):
    session = get_session(chat_id)
    if chat_id == ADMIN_ID:
        extra = "\n\n<b>Admin:</b> Sınırsız erişim aktif."
    elif session["key_valid"]:
        if session.get("is_free"):
            if _user_settings.get_free_trial_used(chat_id):
                extra = "\n\n" + L(chat_id, "trial_used", contact=CONTACT_USERNAME)
            else:
                extra = "\n\n<b>Ücretsiz Hak:</b> 1 hesap kopyalama"
        else:
            extra = "\n\n<b>Lisans:</b> Aktif"
    else:
        trial_used = _user_settings.get_free_trial_used(chat_id)
        if not trial_used:
            extra = "\n\n" + L(chat_id, "welcome_new")
        else:
            extra = "\n\n" + L(chat_id, "trial_used", contact=CONTACT_USERNAME)
    text = L(chat_id, "welcome") + extra
    bot.send_message(chat_id, text, reply_markup=main_menu_inline(chat_id))

# ═══════════════════════════════════════════════════════════
# KOMUTLAR
# ═══════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def cmd_start(message):
    chat_id = message.chat.id
    if _user_settings.is_banned(chat_id):
        bot.send_message(chat_id, L(chat_id, "banned"))
        return

    _user_settings.mark_started(chat_id)
    session = get_session(chat_id)
    session["state"] = None

    current_lang = _user_settings.get_lang(chat_id)
    if not current_lang:
        bot.send_message(chat_id, TRANSLATIONS["tr"]["lang_select"], reply_markup=lang_menu_inline())
        return

    ok, reason = check_channel_membership(chat_id)
    if not ok:
        reason_type, invite_link = reason
        send_channel_required_message(chat_id, reason_type, invite_link)
        return

    if chat_id == ADMIN_ID:
        session["key_valid"] = True
        session["daily_limit"] = ADMIN_DAILY_CLONE_LIMIT
        send_welcome_message(chat_id, "admin")
        return

    ip = get_public_ip() or "0.0.0.0"
    ok, msg, api_key = check_saved_license(chat_id, ip)
    if ok:
        saved = _license_db.get(chat_id)
        if saved:
            session["is_free"] = bool(saved.get("is_free"))
            session["daily_limit"] = saved.get("daily_clone_limit", PAID_DAILY_CLONE_LIMIT)
        session["key_valid"] = True
        send_welcome_message(chat_id, msg)
        return

    trial_used = _user_settings.get_free_trial_used(chat_id)
    if not trial_used:
        session["key_valid"] = True
        session["is_free"] = True
        session["daily_limit"] = FREE_TRIAL_CLONE_LIMIT
        send_welcome_message(chat_id, "trial")
        return

    session["key_valid"] = False
    session["state"] = "waiting_key"
    bot.send_message(chat_id, L(chat_id, "key_required", contact=CONTACT_USERNAME), reply_markup=cancel_inline())

@bot.message_handler(commands=['duyuru'])
def cmd_duyuru(message):
    if message.chat.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Örnek: <code>/duyuru Merhaba!</code>")
        return
    ann = args[1]
    users = _user_settings.get_all_started_users()
    count = 0
    for uid in users:
        try:
            bot.send_message(uid, f"<b>Duyuru</b>\n\n{ann}")
            count += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(message, f"Duyuru {count} kullanıcıya gönderildi.")

@bot.message_handler(commands=['kanalekle'])
def cmd_kanalekle(message):
    if message.chat.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        bot.reply_to(
            message,
            "Kullanım: <code>/kanalekle KANAL_ID [DAVET_LINKI] [BASLIK]</code>\n"
            "Örnek: <code>/kanalekle -1004372335776 https://t.me/+abc Kanalim</code>"
        )
        return
    try:
        channel_id = str(args[1]).strip()
        invite_link = args[2].strip() if len(args) >= 3 else ""
        title = ""
        if " " in invite_link:
            invite_link, title = invite_link.split(" ", 1)
        if not invite_link:
            try:
                chat = bot.get_chat(channel_id)
                if getattr(chat, "invite_link", None):
                    invite_link = chat.invite_link
                elif getattr(chat, "username", None):
                    invite_link = f"https://t.me/{chat.username}"
                title = chat.title or ""
            except Exception as e:
                bot.reply_to(message, f"Kanal bilgisi alınamadı: {e}")
                return
        _config_db.add_channel(channel_id, invite_link, title)
        bot.reply_to(message, f"Kanal eklendi.\nID: <code>{channel_id}</code>\nLink: {invite_link}")
    except Exception as e:
        bot.reply_to(message, f"Hata: {e}")

@bot.message_handler(commands=['kanalsil'])
def cmd_kanalsil(message):
    if message.chat.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Örnek: <code>/kanalsil -1004372335776</code>")
        return
    _config_db.remove_channel(str(args[1]).strip())
    bot.reply_to(message, "Kanal silindi.")

@bot.message_handler(commands=['kanallistele'])
def cmd_kanallistele(message):
    if message.chat.id != ADMIN_ID:
        return
    channels = _config_db.list_channels()
    if not channels:
        bot.reply_to(message, "Zorunlu kanal yok.")
        return
    lines = ["<b>Zorunlu Kanallar</b>"]
    for ch in channels:
        lines.append(f"\nID: <code>{ch['channel_id']}</code>\nLink: {ch['invite_link']}\nBaşlık: {ch['title']}")
    bot.reply_to(message, "\n".join(lines))

@bot.message_handler(commands=['yasakla'])
def cmd_yasakla(message):
    if message.chat.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Örnek: <code>/yasakla 123456789</code>")
        return
    try:
        target = int(args[1])
        _user_settings.set_ban(target, 1)
        bot.reply_to(message, f"Kullanıcı yasaklandı: <code>{target}</code>")
    except Exception as e:
        bot.reply_to(message, f"Hata: {e}")

@bot.message_handler(commands=['yasakkaldir'])
def cmd_yasakkaldir(message):
    if message.chat.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Örnek: <code>/yasakkaldir 123456789</code>")
        return
    try:
        target = int(args[1])
        _user_settings.set_ban(target, 0)
        bot.reply_to(message, f"Kullanıcının yasağı kaldırıldı: <code>{target}</code>")
    except Exception as e:
        bot.reply_to(message, f"Hata: {e}")

@bot.message_handler(commands=['bilgi'])
def cmd_bilgi(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "Bu komut sadece admin içindir.")
        return
    channels = _config_db.list_channels()
    users_started = len(_user_settings.get_all_started_users())
    bot.reply_to(
        message,
        f"<b>Bot Bilgisi</b>\n\n"
        f"Zorunlu kanal: {len(channels)}\n"
        f"Start veren: {users_started}\n"
        f"Ücretsiz deneme limiti: {FREE_TRIAL_CLONE_LIMIT}\n"
        f"Premium günlük limit: {PAID_DAILY_CLONE_LIMIT}\n"
        f"Admin ID: <code>{ADMIN_ID}</code>"
    )

# ─── CALLBACK ───

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    if _user_settings.is_banned(chat_id):
        bot.answer_callback_query(call.id, "Yasaklandın.", show_alert=True)
        return

    session = get_session(chat_id)
    data = call.data

    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    if data.startswith("lang_"):
        new_lang = data.split("_")[1]
        if new_lang in ("tr", "en", "ru"):
            _user_settings.set_lang(chat_id, new_lang)
            session["lang"] = new_lang
            ok, reason = check_channel_membership(chat_id)
            if not ok:
                reason_type, invite_link = reason
                try:
                    bot.edit_message_text(
                        L(chat_id, "channel_sub_required", channel_url=invite_link),
                        chat_id, call.message.message_id
                    )
                except:
                    pass
                return
            if chat_id == ADMIN_ID:
                session["key_valid"] = True
            else:
                ip = get_public_ip() or "0.0.0.0"
                ok2, _, _ = check_saved_license(chat_id, ip)
                if ok2:
                    session["key_valid"] = True
                elif not _user_settings.get_free_trial_used(chat_id):
                    session["key_valid"] = True
                    session["is_free"] = True
                    session["daily_limit"] = FREE_TRIAL_CLONE_LIMIT
                else:
                    session["key_valid"] = False
                    session["state"] = "waiting_key"
            if session["key_valid"]:
                try:
                    bot.edit_message_text(L(chat_id, "welcome"), chat_id, call.message.message_id,
                                          reply_markup=main_menu_inline(chat_id))
                except:
                    pass
            else:
                try:
                    bot.edit_message_text(L(chat_id, "key_required", contact=CONTACT_USERNAME),
                                          chat_id, call.message.message_id, reply_markup=cancel_inline())
                except:
                    pass
        return

    if data == "change_lang":
        bot.edit_message_text(L(chat_id, "lang_select"), chat_id, call.message.message_id, reply_markup=lang_menu_inline())
        return

    if data == "cancel_action":
        session["state"] = None
        if session["key_valid"]:
            bot.edit_message_text(L(chat_id, "cancelled"), chat_id, call.message.message_id, reply_markup=main_menu_inline(chat_id))
        else:
            bot.edit_message_text(L(chat_id, "cancelled") + "\n/start", chat_id, call.message.message_id)
        return

    if data == "back_main":
        session["state"] = None
        bot.edit_message_text(L(chat_id, "welcome"), chat_id, call.message.message_id, reply_markup=main_menu_inline(chat_id))
        return

    if not session["key_valid"]:
        bot.edit_message_text("Lisans gerekli. /start", chat_id, call.message.message_id)
        return

    if data == "menu_contact":
        bot.edit_message_text(L(chat_id, "contact_info", contact=CONTACT_USERNAME), chat_id, call.message.message_id, reply_markup=back_main_inline())
        return

    if data == "menu_clone":
        if session.get("clone_in_progress"):
            bot.answer_callback_query(call.id, "Devam eden clone var, bekle.", show_alert=True)
            return

        if chat_id != ADMIN_ID:
            trial_used = _user_settings.get_free_trial_used(chat_id)
            if session.get("is_free") and not trial_used:
                pass
            elif session.get("is_free") and trial_used:
                bot.edit_message_text(L(chat_id, "trial_used", contact=CONTACT_USERNAME),
                                      chat_id, call.message.message_id, reply_markup=back_main_inline())
                session["key_valid"] = False
                session["state"] = "waiting_key"
                return
            else:
                daily_count = _user_settings.get_daily_clone_count(chat_id)
                if daily_count >= session["daily_limit"]:
                    bot.edit_message_text(
                        L(chat_id, "daily_limit_reached", limit=session["daily_limit"], contact=CONTACT_USERNAME),
                        chat_id, call.message.message_id, reply_markup=back_main_inline()
                    )
                    return

        session["state"] = "waiting_clone_email"
        session["clone_results"] = []
        bot.edit_message_text(L(chat_id, "enter_clone_email"), chat_id, call.message.message_id, reply_markup=cancel_inline())
        return

# ─── TEXT HANDLER ───

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    if _user_settings.is_banned(chat_id):
        return

    text = message.text.strip()
    session = get_session(chat_id)

    if session.get("clone_in_progress"):
        safe_delete_message(chat_id, message.message_id)
        return

    if session["state"] == "waiting_key":
        safe_delete_message(chat_id, message.message_id)
        bot.send_chat_action(chat_id, 'typing')
        ip = get_public_ip() or "0.0.0.0"
        ok, msg, expires_ms, is_free, daily_limit = validate_key(text, ip, chat_id)
        if ok:
            _license_db.save(chat_id, text, ip, expires_ms, is_free, daily_limit)
            session["key_valid"] = True
            session["is_free"] = is_free
            session["daily_limit"] = daily_limit
            session["state"] = None
            send_welcome_message(chat_id, msg)
        else:
            m = bot.send_message(chat_id, L(chat_id, "invalid_key", msg=msg, contact=CONTACT_USERNAME), reply_markup=cancel_inline())
            TEMP_MSG_IDS[chat_id] = m.message_id
        return

    if session["state"] == "waiting_clone_email":
        safe_delete_message(chat_id, message.message_id)
        session["clone_email"] = text
        session["state"] = "waiting_clone_pass"
        m = bot.send_message(chat_id, L(chat_id, "enter_clone_pass"), reply_markup=cancel_inline())
        TEMP_MSG_IDS[chat_id] = m.message_id
        return

    if session["state"] == "waiting_clone_pass":
        safe_delete_message(chat_id, message.message_id)
        session["clone_pass"] = text
        if chat_id in TEMP_MSG_IDS:
            safe_delete_message(chat_id, TEMP_MSG_IDS.pop(chat_id))
        session["state"] = "waiting_clone_count"

        if chat_id == ADMIN_ID:
            max_count = ADMIN_DAILY_CLONE_LIMIT
        elif session.get("is_free") and not _user_settings.get_free_trial_used(chat_id):
            max_count = FREE_TRIAL_CLONE_LIMIT
        else:
            remaining = session["daily_limit"] - _user_settings.get_daily_clone_count(chat_id)
            max_count = max(1, min(20, remaining))

        m = bot.send_message(chat_id, L(chat_id, "enter_clone_count", max=max_count), reply_markup=cancel_inline())
        TEMP_MSG_IDS[chat_id] = m.message_id
        return

    if session["state"] == "waiting_clone_count":
        safe_delete_message(chat_id, message.message_id)
        if chat_id in TEMP_MSG_IDS:
            safe_delete_message(chat_id, TEMP_MSG_IDS.pop(chat_id))
        try:
            count = int(text)
        except:
            m = bot.send_message(chat_id, L(chat_id, "enter_number"), reply_markup=cancel_inline())
            TEMP_MSG_IDS[chat_id] = m.message_id
            return

        if chat_id == ADMIN_ID:
            max_allowed = ADMIN_DAILY_CLONE_LIMIT
        elif session.get("is_free") and not _user_settings.get_free_trial_used(chat_id):
            max_allowed = FREE_TRIAL_CLONE_LIMIT
        else:
            remaining = session["daily_limit"] - _user_settings.get_daily_clone_count(chat_id)
            max_allowed = max(1, min(20, remaining))

        if count < 1 or count > max_allowed:
            m = bot.send_message(chat_id, L(chat_id, "clone_invalid_count", max=max_allowed), reply_markup=cancel_inline())
            TEMP_MSG_IDS[chat_id] = m.message_id
            return

        session["state"] = None
        session["clone_in_progress"] = True
        src_email = session["clone_email"]
        src_pass = session["clone_pass"]
        is_free_run = session.get("is_free") and not _user_settings.get_free_trial_used(chat_id)

        status_msg = bot.send_message(chat_id, L(chat_id, "clone_started", count=count))
        status_msg_id = status_msg.message_id

        def run_clone():
            user_results = []
            try:
                lg = _clone_nuker.login(src_email, src_pass)
                if not lg.get("ok"):
                    bot.edit_message_text(L(chat_id, "clone_login_fail", err=lg.get('message')), chat_id, status_msg_id)
                    session["clone_in_progress"] = False
                    return

                src_uid = lg.get("firebase_uid", "")
                src_token = lg.get("auth", "")
                cars_res = cpm1_fetch_cars_v2(src_token)
                if not cars_res.get("success") or not cars_res.get("cars"):
                    bot.edit_message_text(L(chat_id, "clone_cars_fail"), chat_id, status_msg_id)
                    session["clone_in_progress"] = False
                    return

                source_cars = cars_res["cars"]
                total_to_generate = count

                for i in range(total_to_generate):
                    stamp = int(time.time() * 1000)
                    rand_part = random.randint(100000, 999999)
                    new_email = f"clone{stamp}_{i}_{rand_part}@gmail.com"
                    new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
                    new_name = f"Clone_{i+1}_{rand_part}"

                    try:
                        c_res = _clone_nuker.create_account(new_email, new_password, new_name)
                        if not c_res.get("ok"):
                            continue
                        n_lg = _clone_nuker.login(new_email, new_password)
                        if not n_lg.get("ok"):
                            continue

                        n_uid = n_lg.get("firebase_uid", "")
                        n_token = n_lg.get("auth", "")
                        cpm_id = cpm1_generate_random_cpm_id()

                        prepared = []
                        for car in source_cars:
                            try:
                                c2 = json.loads(json.dumps(car))
                                if src_uid:
                                    c2 = cpm1_replace_uid_in_value(c2, src_uid, n_uid)
                                prepared.append(cpm1_prepare_car(c2, cpm_id))
                            except:
                                pass

                        for car in prepared:
                            cpm1_save_car_encrypted_v2(n_token, car, n_uid, 1)

                        entries = cpm1_build_car_entries(prepared, cpm_id)
                        cpm1_save_car_status(n_token, n_uid, entries)

                        user_results.append((new_email, new_password))
                        _user_settings.increment_clone_count(chat_id)
                    except:
                        continue

                    try:
                        bot.edit_message_text(L(chat_id, "clone_progress", done=len(user_results), total=count), chat_id, status_msg_id)
                    except:
                        pass

                session["clone_in_progress"] = False

                if is_free_run and user_results:
                    _user_settings.mark_free_trial_used(chat_id)
                    session["is_free"] = False
                    session["key_valid"] = False
                    session["state"] = "waiting_key"

                if not user_results:
                    bot.edit_message_text(L(chat_id, "clone_none"), chat_id, status_msg_id)
                    return

                content = "\n".join(f"{e}:{p}" for e, p in user_results)
                bio = io.BytesIO(content.encode("utf-8"))
                bio.name = f"cpm_clone_{int(time.time())}.txt"

                bot.edit_message_text(L(chat_id, "clone_done", success=len(user_results), total=count), chat_id, status_msg_id)
                bot.send_document(chat_id, bio, caption=L(chat_id, "clone_doc_caption", success=len(user_results)))

                if is_free_run:
                    bot.send_message(chat_id, L(chat_id, "trial_used", contact=CONTACT_USERNAME), reply_markup=cancel_inline())
            except Exception as e:
                session["clone_in_progress"] = False
                try:
                    bot.edit_message_text(L(chat_id, "clone_error", err=str(e)), chat_id, status_msg_id)
                except:
                    pass

        threading.Thread(target=run_clone, daemon=True).start()
        return

    bot.send_message(chat_id, L(chat_id, "use_buttons"), reply_markup=main_menu_inline(chat_id))

# ═══════════════════════════════════════════════════════════
# ÇALIŞTIRMA
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("  CPM ACCOUNT STUDIO - Telegram Botu")
    print("=" * 60)
    try:
        _license_db.clear_expired()
    except:
        pass

    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
    except:
        pass

    if not _config_db.list_channels():
        try:
            _config_db.add_channel(
                "-1004372335776",
                "https://t.me/+ryhagfsW9fsyYmE0",
                "CPM Kanal"
            )
            print("Varsayılan zorunlu kanal eklendi.")
        except Exception as e:
            print(f"Kanal eklenemedi: {e}")

    print("  Bot aktif. Mesaj bekleniyor...")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=25, skip_pending=True)
        except Exception as e:
            print(f"Polling hatası: {e}")
            time.sleep(10)
