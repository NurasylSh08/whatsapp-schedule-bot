#!/usr/bin/env python3
"""
Автономный облачный WhatsApp-бот расписания группы ИИ-261/2 (КазУТБ)
для бесплатной работы 24/7 через GitHub Actions + GREEN-API (без включённого ПК и без VPS-сервера).
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

API_URL = (os.getenv("GREEN_API_URL") or "https://api.green-api.com").rstrip("/")
ID_INSTANCE = (os.getenv("GREEN_ID_INSTANCE") or "").strip()
API_TOKEN = (os.getenv("GREEN_API_TOKEN") or "").strip()
CHAT_ID = (os.getenv("GREEN_CHAT_ID") or "").strip()
BOT_MODE = (os.getenv("BOT_MODE") or "auto").strip().lower()

TIMEZONE = ZoneInfo("Asia/Almaty")
SKIP_CONSECUTIVE_SAME_ROOM = False

SCHEDULE = {
    1: {
        "day_name": "Понедельник (Дүйсенбі)",
        "classes": [
            {"start": "11:00", "end": "11:50", "subject": "Шешім қабылдау теориясы", "type": "дәріс (лекция)", "room": "1/300", "teacher": "Мәлік О., магистр, сеньор-лектор"},
            {"start": "12:00", "end": "12:50", "subject": "Ықтималдықтар теориясы және математикалық статистика", "type": "дәріс (лекция)", "room": "1/300", "teacher": "Кенжебекова Г.С., сеньор-лектор"},
            {"start": "13:00", "end": "13:50", "subject": "Ақпараттық-коммуникациялық технологиялар", "type": "лаб. (лабораторная)", "room": "3/510", "teacher": "Ағыбаева Б.С., ассистент магистр"},
            {"start": "14:00", "end": "14:50", "subject": "Ақпараттық-коммуникациялық технологиялар", "type": "лаб. (лабораторная)", "room": "3/510", "teacher": "Ағыбаева Б.С., ассистент магистр"},
            {"start": "15:00", "end": "15:50", "subject": "Сызықтық алгебра", "type": "дәріс (лекция)", "room": "1/300", "teacher": "Солтыбаева Л.С., магистр, сеньор-лектор"},
            {"start": "16:00", "end": "16:50", "subject": "Ықтималдықтар теориясы және математикалық статистика", "type": "лаб. (лабораторная)", "room": "3/506", "teacher": "Кенжебекова Г.С., сеньор-лектор"},
            {"start": "17:00", "end": "17:50", "subject": "Ықтималдықтар теориясы және математикалық статистика", "type": "лаб. (лабораторная)", "room": "3/506", "teacher": "Кенжебекова Г.С., сеньор-лектор"},
        ],
    },
    2: {
        "day_name": "Вторник (Сейсенбі)",
        "classes": [
            {"start": "10:00", "end": "10:50", "subject": "Дене шынықтыру", "type": "тәж. (практика)", "room": "с/з (спортзал)", "teacher": "Ахметов К.Х., сеньор-лектор"},
            {"start": "11:00", "end": "11:50", "subject": "Дене шынықтыру", "type": "тәж. (практика)", "room": "с/з (спортзал)", "teacher": "Ахметов К.Х., сеньор-лектор"},
            {"start": "12:00", "end": "12:50", "subject": "Ақпараттық-коммуникациялық технологиялар", "type": "дәріс (лекция)", "room": "4/402", "teacher": "Ерсултанова А.С., магистр, сеньор-лектор"},
            {"start": "13:00", "end": "13:50", "subject": "Тұрақты даму, экология және тіршілік қауіпсіздігі", "type": "дәріс (лекция)", "room": "4/301", "teacher": "Абеуханова Е.Б., магистр, сеньор-лектор"},
            {"start": "14:00", "end": "14:50", "subject": "Тұрақты даму, экология және тіршілік қауіпсіздігі", "type": "дәріс (лекция)", "room": "4/301", "teacher": "Абеуханова Е.Б., магистр, сеньор-лектор"},
        ],
    },
    3: {
        "day_name": "Среда (Сәрсенбі)",
        "classes": [
            {"start": "12:00", "end": "12:50", "subject": "Сызықтық алгебра", "type": "тәж. (практика)", "room": "2/512", "teacher": "Мажитова А., ассистент магистр"},
            {"start": "13:00", "end": "13:50", "subject": "Сызықтық алгебра", "type": "тәж. (практика)", "room": "2/512", "teacher": "Мажитова А., ассистент магистр"},
            {"start": "14:00", "end": "14:50", "subject": "Экономикалық және кәсіпкерліктің негіздері, құқық негіздері және сыбайлас жемқорлыққа қарсы мәдениет, қаржылық сауаттылық негіздері", "type": "тәж. (практика)", "room": "2/505", "teacher": "Сарсенбаева К.А., магистр, сеньор-лектор"},
            {"start": "15:00", "end": "15:50", "subject": "Экономикалық және кәсіпкерліктің негіздері, құқық негіздері және сыбайлас жемқорлыққа қарсы мәдениет, қаржылық сауаттылық негіздері", "type": "тәж. (практика)", "room": "4/305", "teacher": "Нуридин С.Н., PhD, асс. профессор"},
            {"start": "16:00", "end": "16:50", "subject": "Экономикалық және кәсіпкерліктің негіздері, құқық негіздері және сыбайлас жемқорлыққа қарсы мәдениет, қаржылық сауаттылық негіздері", "type": "тәж. (практика)", "room": "1/402", "teacher": "Таханова Г.Т., магистр, сеньор-лектор"},
        ],
    },
    4: {
        "day_name": "Четверг (Бейсенбі)",
        "classes": [
            {"start": "08:00", "end": "08:50", "subject": "Шет тілі", "type": "тәж. (практика)", "room": "2/514", "teacher": "Нурдыбаева А.К., сеньор-лектор"},
            {"start": "09:00", "end": "09:50", "subject": "Шет тілі", "type": "тәж. (практика)", "room": "2/514", "teacher": "Нурдыбаева А.К., сеньор-лектор"},
            {"start": "10:00", "end": "10:50", "subject": "Шет тілі", "type": "тәж. (практика)", "room": "2/514", "teacher": "Нурдыбаева А.К., сеньор-лектор"},
            {"start": "11:00", "end": "11:50", "subject": "Тұрақты даму, экология және тіршілік қауіпсіздігі", "type": "тәж. (практика)", "room": "3/401", "teacher": "Нусупходжа А.С., ассистент магистр"},
        ],
    },
    5: {
        "day_name": "Пятница (Жұма)",
        "classes": [
            {"start": "08:00", "end": "08:50", "subject": "Орыс тілі", "type": "тәж. (практика)", "room": "1/306", "teacher": "Ешниязова З.А., магистр, ассистент"},
            {"start": "09:00", "end": "09:50", "subject": "Орыс тілі", "type": "тәж. (практика)", "room": "1/306", "teacher": "Ешниязова З.А., магистр, ассистент"},
            {"start": "10:00", "end": "10:50", "subject": "Орыс тілі", "type": "тәж. (практика)", "room": "1/306", "teacher": "Ешниязова З.А., магистр, ассистент"},
            {"start": "11:00", "end": "11:50", "subject": "Шешім қабылдау теориясы", "type": "лаб. (лабораторная)", "room": "3/502", "teacher": "Нуралбаева Д.Б., ассистент магистр"},
            {"start": "12:00", "end": "12:50", "subject": "Шешім қабылдау теориясы", "type": "лаб. (лабораторная)", "room": "2/502", "teacher": "Нуралбаева Д.Б., ассистент магистр"},
        ],
    },
}

def send_whatsapp_message(text: str) -> None:
    if not ID_INSTANCE or not API_TOKEN or not CHAT_ID:
        print("Ошибка: не заданы переменные GREEN_ID_INSTANCE, GREEN_API_TOKEN или GREEN_CHAT_ID.")
        sys.exit(1)
    url = f"{API_URL}/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = json.dumps({"chatId": CHAT_ID, "message": text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"Сообщение отправлено в {CHAT_ID}: {resp.read().decode('utf-8')}")
    except urllib.error.HTTPError as err:
        print(f"HTTP ошибка GREEN-API ({err.code}): {err.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as exc:
        print(f"Ошибка соединения с GREEN-API: {exc}")
        sys.exit(1)

def print_available_chats() -> None:
    if not ID_INSTANCE or not API_TOKEN:
        print("Задайте GREEN_ID_INSTANCE и GREEN_API_TOKEN в Secrets репозитория.")
        sys.exit(1)
    url = f"{API_URL}/waInstance{ID_INSTANCE}/getContacts/{API_TOKEN}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=20) as resp:
        contacts = json.loads(resp.read().decode("utf-8"))
        for g in [c for c in contacts if str(c.get("id", "")).endswith("@g.us")]:
            print(f"Название: {g.get('name', 'Без названия')} | GREEN_CHAT_ID: {g.get('id')}")

def format_day_schedule(day_num: int, is_tomorrow: bool = False) -> str:
    day_data = SCHEDULE.get(day_num)
    if not day_data or not day_data["classes"]:
        if is_tomorrow:
            return "📅 Завтра по расписанию группы *ИИ-261/2* занятий нет — выходной! 🎉"
        return "📅 На сегодня занятий по расписанию группы *ИИ-261/2* нет — выходной! 🎉"
    header = "🌙 *Добрый вечер! Расписание группы ИИ-261/2 на завтра:*" if is_tomorrow else "🌅 *Доброе утро! Расписание группы ИИ-261/2 на сегодня:*"
    lines = [header, f"🗓 *{day_data['day_name']}*", ""]
    for idx, cls in enumerate(day_data["classes"], start=1):
        lines.append(f"*{idx}. {cls['start']}–{cls['end']}* | 🚪 Ауд. *{cls['room']}*\n   📚 {cls['subject']} _({cls['type']})_\n   👨‍🏫 {cls['teacher']}")
    return "\n".join(lines)

def format_class_reminder(lesson: dict, minutes_left: int = 15) -> str:
    return (
        f"⏰ *Напоминание: занятие начинается через {minutes_left} мин. (в {lesson['start']})!*\n\n"
        f"📚 *Дисциплина:* {lesson['subject']}\n"
        f"📝 *Вид занятия:* {lesson['type']}\n"
        f"🚪 *Аудитория:* *{lesson['room']}*\n"
        f"🕒 *Время:* {lesson['start']}–{lesson['end']}\n"
        f"👨‍🏫 *Преподаватель:* {lesson['teacher']}"
    )

def main() -> None:
    now = datetime.now(TIMEZONE)
    day_num = now.isoweekday()
    now_minutes = now.hour * 60 + now.minute
    if BOT_MODE == "get_chats":
        print_available_chats()
        return
    if BOT_MODE == "test":
        send_whatsapp_message(format_class_reminder(SCHEDULE[1]["classes"][0], 15))
        return
    if BOT_MODE == "today":
        send_whatsapp_message(format_day_schedule(day_num, is_tomorrow=False))
        return
    if BOT_MODE == "tomorrow":
        tomorrow_num = (day_num % 7) + 1
        send_whatsapp_message(format_day_schedule(tomorrow_num, is_tomorrow=True))
        return
    if 19 * 60 + 45 <= now_minutes <= 20 * 60 + 25:
        tomorrow_num = (day_num % 7) + 1
        if tomorrow_num in SCHEDULE:
            send_whatsapp_message(format_day_schedule(tomorrow_num, is_tomorrow=True))
        return
    day_data = SCHEDULE.get(day_num)
    if not day_data:
        return
    if 7 * 60 + 15 <= now_minutes <= 7 * 60 + 40:
        send_whatsapp_message(format_day_schedule(day_num, is_tomorrow=False))
        return
    classes = day_data["classes"]
    for i, lesson in enumerate(classes):
        prev_lesson = classes[i - 1] if i > 0 else None
        if SKIP_CONSECUTIVE_SAME_ROOM and prev_lesson and prev_lesson["subject"] == lesson["subject"] and prev_lesson["room"] == lesson["room"] and prev_lesson["teacher"] == lesson["teacher"]:
            continue
        start_h, start_m = map(int, lesson["start"].split(":"))
        diff_minutes = (start_h * 60 + start_m) - now_minutes
        if 1 <= diff_minutes <= 28:
            send_whatsapp_message(format_class_reminder(lesson, diff_minutes))
            return

if __name__ == "__main__":
    main()
