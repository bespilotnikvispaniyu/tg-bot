# -*- coding: utf-8 -*-
import asyncio
import os
import sqlite3
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")
if not ADMIN_IDS_RAW:
    raise RuntimeError("ADMIN_ID не задан в .env")

ADMIN_IDS = {int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip()}

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

DB = "applications.db"


class Form(StatesGroup):
    direction = State()
    steam_discord = State()
    mafile = State()
    english = State()
    time = State()
    source = State()


def db_init():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            direction TEXT,
            steam_discord TEXT,
            mafile TEXT,
            english TEXT,
            daily_time TEXT,
            source TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❗ О нас", callback_data="about"),
            InlineKeyboardButton(text="👁 Как начать заниматься?", callback_data="how"),
        ],
        [InlineKeyboardButton(text="❤️ Подать заявку", callback_data="apply")],
    ])


def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
    ])


def direction_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 CS2", callback_data="dir_cs2")],
        [InlineKeyboardButton(text="🏠 Rust", callback_data="dir_rust")],
        [InlineKeyboardButton(text="⚔️ Dota 2", callback_data="dir_dota")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
    ])


def yes_no_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❤️ Да", callback_data="yn_yes"),
            InlineKeyboardButton(text="🖤 Нет", callback_data="yn_no"),
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
    ])


def english_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Да", callback_data="eng_good")],
        [InlineKeyboardButton(text="🖤 Так себе", callback_data="eng_mid")],
        [InlineKeyboardButton(text="🤍 Нет", callback_data="eng_no")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
    ])


def time_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ 1-2 часа", callback_data="time_1_2")],
        [InlineKeyboardButton(text="⏰ 4-6 часов", callback_data="time_4_6")],
        [InlineKeyboardButton(text="🌑 8+ часов", callback_data="time_8_plus")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
    ])


def admin_menu(app_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve:{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{app_id}"),
        ]
    ])


START_TEXT = (
    "<b>❤️ Poison Team</b>\n\n"
    "Добро пожаловать в тень.\n"
    "Выбери раздел ниже."
)

STEP1_TEXT = (
    "❤️ <b>Шаг 1 из 6</b>\n\n"
    "⚔️ Желаемое направление\n"
    "(позже можно работать по любому)"
)
STEP2_TEXT = (
    "❤️ <b>Шаг 2 из 6</b>\n\n"
    "🎧 Есть Steam с выбранной игрой и Discord с микрофоном?"
)
STEP3_TEXT = (
    "❤️ <b>Шаг 3 из 6</b>\n\n"
    "🕯️ Есть опыт в подмене / mafile Steam?"
)
STEP4_TEXT = (
    "❤️ <b>Шаг 4 из 6</b>\n\n"
    "🗣 Знаешь английский?"
)
STEP5_TEXT = (
    "❤️ <b>Шаг 5 из 6</b>\n\n"
    "🌑 Сколько времени готов уделять в день?"
)
STEP6_TEXT = (
    "❤️ <b>Шаг 6 из 6</b>\n\n"
    "🔮 Откуда узнал о нас?\n\n"
    "Напиши одним сообщением ниже 👇"
)


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(START_TEXT, reply_markup=main_menu())


@dp.callback_query(F.data == "home")
async def home(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(START_TEXT, reply_markup=main_menu())
    await call.answer()


@dp.callback_query(F.data == "about")
async def about(call: CallbackQuery):
    await call.message.edit_text(
        " <b>О проекте Poison Team</b>\n\n"
        "Хочешь попробовать себя в новом направлении и получить первый опыт?\n\n"
        "<b>Poison Team</b> — сплоченная команда. "
        "Здесь помогают сделать первые шаги и разобраться во всём с нуля. "
        "На старте тебя поддержат кураторы — подскажут, что делать, помогут быстрее "
        "освоиться и выйти на первые результаты.\n\n"
        "Экспертом быть не нужно. Главное — желание развиваться.\n\n"
        "❤️ Жми «Подать заявку» и войди в Poison Team.",
        reply_markup=main_menu(),
    )
    await call.answer()


@dp.callback_query(F.data == "how")
async def how(call: CallbackQuery):
    await call.message.edit_text(
        "👁️ <b>Как начать?</b>\n\n"
        "1. Подай заявку и вступи в рабочие группы Telegram и Discord.\n"
        "2. Пройди краткое обучение.\n"
        "Задача — находить игроков RUST/CS2/DOTA 2 с инвентарём от 50-150$.\n"
        "3. Нашёл подходящего человека и установил контакт? "
        "Пригласи его в Discord сыграть вместе.\n"
        "4. Дальше — дело за кураторами.\n\n"
        " Просто как 1-2-3.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📜 FAQ", callback_data="faq"),
                InlineKeyboardButton(text="◀️ Назад", callback_data="home"),
            ]
        ]),
    )
    await call.answer()


@dp.callback_query(F.data == "faq")
async def faq(call: CallbackQuery):
    await call.message.edit_text(
        "📜 <b>FAQ</b>\n\n"
        "1.Дружелюбное комьюнити\n"
        "2.Полная поддержка новичков от кураторов\n"
        "3.Быстрые выплаты в любой криптовалюте\n"
        "4.Возможность карьерного роста для каждого\n"
        "Это и еще многое другое есть в нашей команде!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="how")]
        ]),
    )
    await call.answer()


@dp.callback_query(F.data == "apply")
async def apply(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Form.direction)
    await call.message.edit_text(STEP1_TEXT, reply_markup=direction_menu())
    await call.answer()


@dp.callback_query(Form.direction, F.data.in_({"dir_cs2", "dir_rust", "dir_dota"}))
async def direction(call: CallbackQuery, state: FSMContext):
    values = {"dir_cs2": "CS2", "dir_rust": "Rust", "dir_dota": "Dota 2"}
    await state.update_data(direction=values[call.data])
    await state.set_state(Form.steam_discord)
    await call.message.edit_text(STEP2_TEXT, reply_markup=yes_no_menu())
    await call.answer()


@dp.callback_query(Form.steam_discord, F.data.in_({"yn_yes", "yn_no"}))
async def steam_discord(call: CallbackQuery, state: FSMContext):
    await state.update_data(steam_discord="Да" if call.data == "yn_yes" else "Нет")
    await state.set_state(Form.mafile)
    await call.message.edit_text(STEP3_TEXT, reply_markup=yes_no_menu())
    await call.answer()


@dp.callback_query(Form.mafile, F.data.in_({"yn_yes", "yn_no"}))
async def mafile(call: CallbackQuery, state: FSMContext):
    await state.update_data(mafile="Да" if call.data == "yn_yes" else "Нет")
    await state.set_state(Form.english)
    await call.message.edit_text(STEP4_TEXT, reply_markup=english_menu())
    await call.answer()


@dp.callback_query(Form.english, F.data.in_({"eng_good", "eng_mid", "eng_no"}))
async def english(call: CallbackQuery, state: FSMContext):
    values = {"eng_good": "Да", "eng_mid": "Так себе", "eng_no": "Нет"}
    await state.update_data(english=values[call.data])
    await state.set_state(Form.time)
    await call.message.edit_text(STEP5_TEXT, reply_markup=time_menu())
    await call.answer()


@dp.callback_query(Form.time, F.data.in_({"time_1_2", "time_4_6", "time_8_plus"}))
async def daily_time(call: CallbackQuery, state: FSMContext):
    values = {
        "time_1_2": "1-2 часа",
        "time_4_6": "4-6 часов",
        "time_8_plus": "8+ часов",
    }
    await state.update_data(daily_time=values[call.data])
    await state.set_state(Form.source)
    await call.message.edit_text(STEP6_TEXT, reply_markup=back_menu())
    await call.answer()


@dp.message(Form.source, F.text)
async def source(message: Message, state: FSMContext):
    data = await state.get_data()
    data["source"] = message.text.strip()

    username = f"@{message.from_user.username}" if message.from_user.username else "нет username"

    con = sqlite3.connect(DB)
    cur = con.execute(
        "INSERT INTO applications "
        "(user_id, username, direction, steam_discord, mafile, english, daily_time, source, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            message.from_user.id,
            username,
            data.get("direction", "—"),
            data.get("steam_discord", "—"),
            data.get("mafile", "—"),
            data.get("english", "—"),
            data.get("daily_time", "—"),
            data["source"],
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ),
    )
    app_id = cur.lastrowid
    con.commit()
    con.close()

    admin_text = (
        f"📩 <b>Новая заявка #{app_id}</b>\n\n"
        f"👤 Пользователь: {username}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
        f"⚔️ Направление: <b>{data.get('direction', '—')}</b>\n"
        f"🎧 Steam + Discord: <b>{data.get('steam_discord', '—')}</b>\n"
        f"🕯️ Опыт в mafile: <b>{data.get('mafile', '—')}</b>\n"
        f"🗣 Английский: <b>{data.get('english', '—')}</b>\n"
        f"🌑 Время в день: <b>{data.get('daily_time', '—')}</b>\n"
        f"🔮 Откуда узнал: <b>{data['source']}</b>"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=admin_menu(app_id))
        except Exception:
            pass

    await message.answer(
        "✅ <b>Заявка отправлена!</b>\n\n"
        "Куратор рассмотрит её и свяжется с тобой.",
        reply_markup=main_menu(),
    )
    await state.clear()


BACK_MAP = {
    Form.steam_discord.state: (Form.direction, STEP1_TEXT, direction_menu),
    Form.mafile.state: (Form.steam_discord, STEP2_TEXT, yes_no_menu),
    Form.english.state: (Form.mafile, STEP3_TEXT, yes_no_menu),
    Form.time.state: (Form.english, STEP4_TEXT, english_menu),
    Form.source.state: (Form.time, STEP5_TEXT, time_menu),
}


@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery, state: FSMContext):
    current = await state.get_state()

    if current is None or current not in BACK_MAP:
        await state.clear()
        await call.message.edit_text(START_TEXT, reply_markup=main_menu())
        await call.answer()
        return

    prev_state, text, menu = BACK_MAP[current]
    await state.set_state(prev_state)
    await call.message.edit_text(text, reply_markup=menu)
    await call.answer()


@dp.callback_query(F.data.startswith("approve:"))
async def approve(call: CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Нет доступа", show_alert=True)
        return

    app_id = int(call.data.split(":")[1])
    con = sqlite3.connect(DB)
    row = con.execute("SELECT user_id FROM applications WHERE id=?", (app_id,)).fetchone()
    con.execute("UPDATE applications SET status='approved' WHERE id=?", (app_id,))
    con.commit()
    con.close()

    if row:
        try:
            await bot.send_message(
                row[0],
                "✅ <b>Твоя заявка принята!</b>\n\n"
                "Добро пожаловать в <b>Poison Team</b> 🖤\n\n"
                "🔗 Юзернеймы кураторов для связи:\n"
                "@fow1erts\n"
                "@cyanidts",
                disable_web_page_preview=False,
            )
        except Exception:
            pass

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(f"✅ Заявка #{app_id} принята.")
    await call.answer("Заявка принята")


@dp.callback_query(F.data.startswith("reject:"))
async def reject(call: CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Нет доступа", show_alert=True)
        return

    app_id = int(call.data.split(":")[1])
    con = sqlite3.connect(DB)
    row = con.execute("SELECT user_id FROM applications WHERE id=?", (app_id,)).fetchone()
    con.execute("UPDATE applications SET status='rejected' WHERE id=?", (app_id,))
    con.commit()
    con.close()

    if row:
        try:
            await bot.send_message(
                row[0],
                "❌ <b>Заявка не прошла отбор.</b>\n\n"
                "Спасибо за интерес к проекту.",
            )
        except Exception:
            pass

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(f"❌ Заявка #{app_id} отклонена.")
    await call.answer("Заявка отклонена")


async def main():
    db_init()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
