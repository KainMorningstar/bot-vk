import os
import re
import sqlite3
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
from datetime import datetime, timedelta

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise Exception("Переменная окружения TOKEN не задана!")

ADMIN_ID = 711301702

DATA_DIR = os.environ.get("DATA_DIR", ".")
DB_PATH = os.path.join(DATA_DIR, "homework.db")

TEACHERS = {
    "анатомия": "Чеканин Игорь, сын Михаила",
    "биология": "Постнова Маргарита, дочь Виктора",
    "гистология": "Вондрачек Людмила, дочь Виктора",
    "история": "Киценко Роман, сын Николая",
    "психология": "Артюхина Александра, дочь Ивана",
    "орг": "Самоходкина Татьяна, дочь Виктора",
    "физра": "Садыкова Наталья, дочь Романа",
    "физика": "Чеусова Лолита, дочь Александра",
    "химия": "Финагеева Мария, дочь Олега",
    "латинский язык": "Выстропова Ольга, дочь Станислава",
    "английский": "Анкин Даниил, сын Юрия",
    "философия": "Пашарина Екатерина, дочь Сергея"
}

LINKS = {
    "история": "https://telemost.yandex.ru/j/2560443856",
    "психология": "https://telemost.yandex.ru/j/93311157027821",
    "орг": "https://telemost.yandex.ru/j/5504789628",
    "философия": "https://telemost.yandex.ru/j/82394246600604",
}

LECTURE_ROOM_5F = "ауд. 2, 5 этаж"
LECTURE_ROOM_HIM = "ауд. 1, 8 этаж хим. корпуса"

SCHEDULE = {
    "понедельник": {
        "pairs": [
            {"time": "10:20–12:00", "subject": "История России (лекция)", "room": LECTURE_ROOM_5F},
            {"time": "12:30–14:10", "subject": "Гистология (лекция)", "room": LECTURE_ROOM_5F, "dates": ["2026-10-05", "2026-11-02"]},
            {"time": "12:30–14:10", "subject": "Анатомия (лекция)", "room": LECTURE_ROOM_5F, "dates": ["2026-10-12", "2026-11-09"]},
            {"time": "12:30–14:10", "subject": "Биология (лекция)", "room": LECTURE_ROOM_5F, "dates": ["2026-10-19", "2026-11-16"]},
            {"time": "12:30–14:10", "subject": "ОРГ (лекция)", "room": LECTURE_ROOM_5F, "dates": ["2026-10-26"]},
            {"time": "12:30–14:10", "subject": "ОРГ (лекция)", "room": LECTURE_ROOM_5F, "weekly_from": "2026-11-23"},
            {"time": "14:20–17:50", "subject": "Анатомия (семинар)", "room": "5-11"},
        ],
        "day_note": "Весь день в морфологическом корпусе",
        "fun_note": "Ну что, начало недели, берем прекрасные синие ручки, открываем прекрасные тетрадки и начинаем..."
    },
    "вторник": {
        "pairs": [
            {"time": "8:30–10:10", "subject": "Химия (лекция)", "room": LECTURE_ROOM_HIM, "dates": ["2026-10-06", "2026-11-10"]},
            {"time": "8:30–10:10", "subject": "Физика (лекция)", "room": LECTURE_ROOM_HIM, "dates": ["2026-10-13", "2026-11-17"]},
            {"time": "8:30–10:10", "subject": "Философия (лекция)", "room": LECTURE_ROOM_HIM, "dates": ["2026-10-20", "2026-11-24"]},
            {"time": "8:30–10:10", "subject": "Физкультура (лекция)", "room": LECTURE_ROOM_HIM, "dates": ["2026-10-27", "2026-12-01"]},
            {"time": "8:30–10:10", "subject": "Психология (лекция)", "room": LECTURE_ROOM_HIM, "dates": ["2026-11-03", "2026-12-08"]},
            {"time": "10:20–12:00", "subject": "Физика (семинар)", "room": "корпус Б, 5-06"},
            {"time": "12:30–14:10", "subject": "Латинский язык", "room": "корпус Б, 6-04", "dates": ["2026-10-13", "2026-10-27", "2026-11-10", "2026-11-24", "2026-12-08", "2026-12-22"]},
        ],
        "day_note": "Весь день в главном корпусе",
        "fun_note": "Итак, как люди в белых халатах, продолжайте учиться ускорять или замедлять встречу остальных человеков с создателем."
    },
    "среда": {
        "pairs": [
            {"time": "11:00–12:00", "subject": "Физическая культура и спорт", "room": "кафедра физ-ры", "dates": ["2026-10-07", "2026-10-21", "2026-11-04", "2026-11-18", "2026-12-02", "2026-12-16"]},
            {"time": "13:00–16:30", "subject": "Химия (семинар)", "room": "2-15"},
        ],
        "day_note": None,
        "fun_note": "Подпиши на физру хотя бы не в кроссах? А то вырастили из вас потребителей, по любому пишите мне на айфоне."
    },
    "четверг": {
        "pairs": [
            {"time": "8:30–12:00", "subject": "История России (семинар)"},
            {"time": "12:30–14:10", "subject": "Психология (семинар)"},
            {"time": "14:20–16:00", "subject": "ОРГ (семинар)"},
        ],
        "day_note": "Весь день дистант",
        "fun_note": "Итак, день, когда получить снежинку проще всего... Белая снежинка, кружится, летииит."
    },
    "пятница": {
        "pairs": [
            {"time": "8:30–12:00", "subject": "Биология (семинар)", "room": "3-07"},
            {"time": "13:00–14:40", "subject": "Физра (элективные модули)"},
            {"time": "15:40–17:20", "subject": "Философия (семинар)", "note": "дистант"},
        ],
        "day_note": None,
        "fun_note": "Почти конец недели, скоро и конъякулы, а пока лишь вечером философия — наука о пиздабольстве..."
    },
    "суббота": {
        "pairs": [
            {"time": "8:30–10:10", "subject": "Гистология (семинар)", "room": "7-01"},
            {"time": "10:50–12:30", "subject": "Английский язык", "room": "корпус Б, 6-04"},
        ],
        "day_note": None,
        "fun_note": "Полдня поработайте и добрый Игорь Михайлович отпускает вас на конъякулы."
    },
    "воскресенье": {
        "pairs": [],
        "day_note": "Завтра конъякулы 😌",
        "fun_note": None
    },
}

DAYS_RU = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS homework (
            date TEXT,
            subject TEXT,
            task TEXT,
            PRIMARY KEY (date, subject)
        )
    """)
    conn.commit()
    conn.close()

def save_homework(date_str, subject, task):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO homework (date, subject, task)
        VALUES (?, ?, ?)
    """, (date_str, subject.lower(), task))
    conn.commit()
    conn.close()

def delete_homework(date_str, subject):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM homework WHERE date = ? AND subject = ?", (date_str, subject.lower()))
    conn.commit()
    conn.close()

def get_homework(date_str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT subject, task FROM homework WHERE date = ?", (date_str,))
    rows = cur.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def get_all_homework():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT date, subject, task FROM homework ORDER BY date")
    rows = cur.fetchall()
    conn.close()
    return rows

init_db()

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_message(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        keyboard=keyboard,
        random_id=random.randint(1, 2**31)
    )

def get_main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Преподы', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Завтра', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('ДЗ', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Ссылки', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Команды', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def is_pair_today(pair, date_key, day_name):
    if "dates" in pair:
        return date_key in pair["dates"]
    if "weekly_from" in pair:
        return date_key >= pair["weekly_from"]
    return True

def format_schedule(day_data, date_str, date_key, day_name):
    pairs = day_data.get("pairs", [])
    day_note = day_data.get("day_note")
    fun_note = day_data.get("fun_note")

    actual_pairs = [p for p in pairs if is_pair_today(p, date_key, day_name)]

    if not actual_pairs and not day_note and not fun_note:
        return f"Расписание на {date_str} ({day_name}):\nПар нет"

    lines = [f"Расписание на {date_str} ({day_name}):"]
    if not actual_pairs:
        lines.append("Пар нет")
    else:
        for i, p in enumerate(actual_pairs, 1):
            line = f"{i}. {p['time']} — {p['subject']}"
            if p.get("room"):
                line += f" [{p['room']}]"
            if p.get("note"):
                line += f" ({p['note']})"
            lines.append(line)

    if day_note:
        lines.append("")
        lines.append(f"❗ {day_note}")

    if fun_note:
        lines.append("")
        lines.append(f"💬 {fun_note}")

    return "\n".join(lines)

def get_schedule_for_date(target_date):
    date_key = target_date.strftime("%Y-%m-%d")
    date_display = target_date.strftime("%d.%m.%Y")
    day_index = target_date.weekday()
    day_name = DAYS_RU[day_index]

    day_data = SCHEDULE.get(day_name)
    if not day_data:
        return "Расписание на эту дату ещё не загружено."

    return format_schedule(day_data, date_display, date_key, day_name)

def get_today_schedule():
    return get_schedule_for_date(datetime.now())

def get_tomorrow_schedule():
    return get_schedule_for_date(datetime.now() + timedelta(days=1))

def get_schedule_by_user_date(text):
    match = re.search(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?", text)
    if not match:
        return None
    day = int(match.group(1))
    month = int(match.group(2))
    year_str = match.group(3)
    if year_str:
        year = int(year_str)
        if year < 100:
            year += 2000
    else:
        year = datetime.now().year
    try:
        return datetime(year, month, day)
    except ValueError:
        return None

def get_links(request):
    for subj in LINKS:
        if subj in request:
            return f"Ссылка на {subj}:\n{LINKS[subj]}"
    lines = ["Ссылки на дистанционные предметы:"]
    for subj, link in LINKS.items():
        lines.append(f"• {subj.capitalize()}: {link}")
    return "\n".join(lines)

def get_commands():
    text = "Вот что я умею:\n\n"
    text += "• привет / начать / start — поздороваться\n"
    text += "• преподы — список преподавателей\n"
    text += "• ссылки — все ссылки на дистанционные предметы\n"
    text += "• ссылки [предмет] — ссылка на конкретный предмет\n"
    text += "• расписание / сегодня — расписание на сегодня\n"
    text += "• завтра — расписание на завтра\n"
    text += "• расписание 12.10 — расписание на конкретную дату\n"
    text += "• дз / домашка — что задали на завтра\n"
    text += "• дз 12.10 — что задали на конкретную дату\n"
    text += "• команды — этот список\n\n"
    text += "Учить команды по атласу — путь в никуда. Учить команды по списку — единственное, что отделяет тебя от уровня среднего специального образования."
    return text

def get_homework_for_date(target_date):
    date_key = target_date.strftime("%Y-%m-%d")
    date_display = target_date.strftime("%d.%m.%Y")
    day_index = target_date.weekday()
    day_name = DAYS_RU[day_index]

    day_data = SCHEDULE.get(day_name)
    if not day_data:
        return f"ДЗ на {date_display}: расписание не загружено."

    actual_pairs = [p for p in day_data.get("pairs", []) if is_pair_today(p, date_key, day_name)]

    hw = get_homework(date_key)

    if not actual_pairs:
        return f"ДЗ на {date_display} ({day_name}):\nПар нет — и домашки нет 😌"

    lines = [f"ДЗ на {date_display} ({day_name}):"]
    has_any = False
    for p in actual_pairs:
        subj_full = p["subject"]
        subj_base = subj_full.split("(")[0].strip().lower()

        task = None
        for saved_subj, saved_task in hw.items():
            if saved_subj in subj_base or subj_base in saved_subj:
                task = saved_task
                break

        if task:
            lines.append(f"• {subj_full}:\n   {task}")
            has_any = True
        else:
            lines.append(f"• {subj_full}: не задано")

    if not has_any:
        lines.append("")
        lines.append("(пока ничего не задано)")

    return "\n".join(lines)

def parse_admin_command(request):
    match = re.match(r"задать\s+дз\s+(\d{1,2}\.\d{1,2}(?:\.\d{2,4})?)\s+(.+?):\s*(.+)", request)
    if not match:
        return None
    date_str_raw = match.group(1)
    subject = match.group(2).strip()
    task = match.group(3).strip()

    date_parsed = get_schedule_by_user_date(date_str_raw)
    if not date_parsed:
        return None

    return date_parsed.strftime("%Y-%m-%d"), subject, task

def parse_delete_command(request):
    match = re.match(r"удалить\s+дз\s+(\d{1,2}\.\d{1,2}(?:\.\d{2,4})?)\s+(.+)", request)
    if not match:
        return None
    date_str_raw = match.group(1)
    subject = match.group(2).strip()

    date_parsed = get_schedule_by_user_date(date_str_raw)
    if not date_parsed:
        return None

    return date_parsed.strftime("%Y-%m-%d"), subject

print("Бот запущен и слушает сообщения...")
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower().strip()
        is_admin = (event.user_id == ADMIN_ID)

        if is_admin and request.startswith("задать дз"):
            parsed = parse_admin_command(request)
            if parsed:
                date_key, subject, task = parsed
                save_homework(date_key, subject, task)
                send_message(event.user_id, f"✅ Сохранил: {subject} на {date_key} — «{task}»")
            else:
                send_message(event.user_id, "Не понял. Формат: задать дз 12.10 Анатомия: параграф 5")
            continue

        if is_admin and request.startswith("удалить дз"):
            parsed = parse_delete_command(request)
            if parsed:
                date_key, subject = parsed
                delete_homework(date_key, subject)
                send_message(event.user_id, f"🗑 Удалил: {subject} на {date_key}")
            else:
                send_message(event.user_id, "Не понял. Формат: удалить дз 12.10 Анатомия")
            continue

        if is_admin and request == "все дз":
            rows = get_all_homework()
            if not rows:
                send_message(event.user_id, "База домашки пуста.")
            else:
                lines = ["Вся сохранённая домашка:"]
                for date_str, subj, task in rows:
                    lines.append(f"• {date_str} — {subj}: {task}")
                send_message(event.user_id, "\n".join(lines))
            continue

        if "преподы" in request:
            send_message(event.user_id, "Ишь чего захотел. А синтетическую булочку с синтетическим кофе тебе не принести? Ладно, вот тебе.")
            text = "Список преподавателей:\n"
            for subj, name in TEACHERS.items():
                text += f"- {subj.capitalize()}: {name}\n"
            send_message(event.user_id, text)

        elif "ссылки" in request:
            send_message(event.user_id, get_links(request))

        elif "команды" in request or "помощь" in request:
            send_message(event.user_id, get_commands())

        elif request.startswith("дз") or "домашка" in request:
            parsed = get_schedule_by_user_date(request)
            if parsed:
                send_message(event.user_id, get_homework_for_date(parsed))
            else:
                send_message(event.user_id, get_homework_for_date(datetime.now() + timedelta(days=1)))

        elif "завтра" in request:
            send_message(event.user_id, get_tomorrow_schedule())

        elif "расписание" in request or "сегодня" in request:
            parsed = get_schedule_by_user_date(request)
            if parsed:
                send_message(event.user_id, get_schedule_for_date(parsed))
            else:
                send_message(event.user_id, get_today_schedule())

        elif "привет" in request or "start" in request or "начать" in request:
            send_message(
                event.user_id,
                "Первый курс, стомат? Прикольно, ладно, и что тебе надо?",
                keyboard=get_main_keyboard()
            )

        else:
            send_message(event.user_id, "Я не понял команду. Попробуй: 'преподы', 'ссылки', 'расписание', 'дз' или 'привет'.")
