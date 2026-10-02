import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
from datetime import datetime, timedelta

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise Exception("Переменная окружения TOKEN не задана!")

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

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_message(user_id, message):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=random.randint(1, 2**31)
    )

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

def get_tomorrow_schedule():
    tomorrow = datetime.now() + timedelta(days=1)
    date_key = tomorrow.strftime("%Y-%m-%d")
    date_display = tomorrow.strftime("%d.%m.%Y")
    day_index = tomorrow.weekday()
    day_name = DAYS_RU[day_index]

    day_data = SCHEDULE.get(day_name)
    if not day_data:
        return "Расписание на эту дату ещё не загружено."

    return format_schedule(day_data, date_display, date_key, day_name)

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
    text += "• расписание / завтра — расписание на завтра\n"
    text += "• команды — этот список\n\n"
    text += "Учить команды по атласу — путь в никуда. Учить команды по списку — единственное, что отделяет тебя от уровня среднего специального образования."
    return text

print("Бот запущен и слушает сообщения...")
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower().strip()

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

        elif "расписание" in request or "завтра" in request:
            send_message(event.user_id, get_tomorrow_schedule())

        elif "привет" in request or "start" in request or "начать" in request:
            send_message(event.user_id, "Первый курс, стомат? Прикольно, ладно, и что тебе надо?")

        else:
            send_message(event.user_id, "Я не понял команду. Попробуй: 'преподы', 'ссылки', 'расписание' или 'привет'.")
