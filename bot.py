from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

TOKEN = '7869459968:AAH5BXAl-K_jNzjNu0daYGS-Ph9Kq58z82M'

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_lang = {}
pending_data = {}  # хранит данные до подтверждения

class OrderForm(StatesGroup):
    language = State()
    action = State()
    category = State()
    name = State()
    phone = State()
    manager = State()
    service = State()
    total = State()
    payment = State()
    cost = State()
    log_type = State()
    log_note = State()

langs = {
    "ru": {
        "select_language": "Пожалуйста, выберите язык / Iltimos, tilni tanlang",
        "select_action": "Выберите действие:",
        "select_category": "Выберите категорию:",
        "enter_name": "Введите имя клиента:",
        "enter_phone": "Укажите номер клиента:",
        "enter_manager": "Кто принял заказ:",
        "enter_service": "Введите услугу:",
        "enter_total": "Введите общую сумму:",
        "enter_payment": "Введите сумму Аванса:",
        "enter_cost": "Введите себестоимость:",
        "success": "Данные успешно сохранены. Спасибо!",
        "rejected": "Приём был отклонён ответственным.",
        "main_menu": "Главное меню",
        "back": "Назад",
        "new_order": "Новый заказ",
        "warranty": "Гарантия",
        "sale": "Продажа",
        "logistics": "Логистика"
    }
}

def get_text(user_id, key):
    lang = user_lang.get(user_id, "ru")
    return langs[lang].get(key, key)

def lang_kb():
    return ReplyKeyboardMarkup(resize_keyboard=True).add("Русский", "Узбекский")

def main_kb(user_id):
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        langs[user_lang[user_id]]["new_order"],
        langs[user_lang[user_id]]["main_menu"]
    )

def category_kb(user_id):
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        langs[user_lang[user_id]]["warranty"],
        langs[user_lang[user_id]]["sale"],
        langs[user_lang[user_id]]["logistics"],
        langs[user_lang[user_id]]["back"]
    )

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(langs["ru"]["select_language"], reply_markup=lang_kb())
    await OrderForm.language.set()

@dp.message_handler(commands=["id"])
async def get_id(message: types.Message):
    await message.reply(f"Ваш Telegram ID: {message.from_user.id}")

@dp.message_handler(state=OrderForm.language)
async def set_language(message: types.Message, state: FSMContext):
    lang = "uz" if "узбе" in message.text.lower() or "uzb" in message.text.lower() else "ru"
    user_lang[message.from_user.id] = lang
    await message.answer(get_text(message.from_user.id, "select_action"), reply_markup=main_kb(message.from_user.id))
    await OrderForm.action.set()

@dp.message_handler(state=OrderForm.action)
async def choose_action(message: types.Message, state: FSMContext):
    await message.answer(get_text(message.from_user.id, "select_category"), reply_markup=category_kb(message.from_user.id))
    await OrderForm.category.set()

@dp.message_handler(state=OrderForm.category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer(get_text(message.from_user.id, "enter_name"))
    await OrderForm.name.set()

@dp.message_handler(state=OrderForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(get_text(message.from_user.id, "enter_phone"))
    await OrderForm.phone.set()

@dp.message_handler(state=OrderForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(get_text(message.from_user.id, "enter_manager"))
    await OrderForm.manager.set()

@dp.message_handler(state=OrderForm.manager)
async def process_manager(message: types.Message, state: FSMContext):
    await state.update_data(manager=message.text)
    await message.answer(get_text(message.from_user.id, "enter_service"))
    await OrderForm.service.set()

@dp.message_handler(state=OrderForm.service)
async def process_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer(get_text(message.from_user.id, "enter_total"))
    await OrderForm.total.set()

@dp.message_handler(state=OrderForm.total)
async def process_total(message: types.Message, state: FSMContext):
    await state.update_data(total=message.text)
    await message.answer(get_text(message.from_user.id, "enter_payment"))
    await OrderForm.payment.set()

@dp.message_handler(state=OrderForm.payment)
async def process_payment(message: types.Message, state: FSMContext):
    await state.update_data(payment=message.text)
    await message.answer(get_text(message.from_user.id, "enter_cost"))
    await OrderForm.cost.set()

@dp.message_handler(state=OrderForm.cost)
async def process_cost(message: types.Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await message.answer("Сколько сдано в кассу?")
    await OrderForm.log_type.set()

@dp.message_handler(state=OrderForm.log_type)
async def process_kassa_sum(message: types.Message, state: FSMContext):
    await state.update_data(kassa_amount=message.text)
    buttons = ReplyKeyboardMarkup(resize_keyboard=True).add("Мухаммадзаби Ахтамович", "Азизжон Гайбулаевич")
    await message.answer("Кому сдано?", reply_markup=buttons)
    await OrderForm.log_note.set()

@dp.message_handler(state=OrderForm.log_note)
async def process_kassa_person(message: types.Message, state: FSMContext):
    data = await state.get_data()
    receiver = message.text
    data["receiver"] = receiver
    data["user_id"] = message.from_user.id
    data["message_id"] = message.message_id

    receiver_ids = {
        "Мухаммадзаби Ахтамович": 57540864,
        "Азизжон Гайбулаевич": 1133682490
    }

    if receiver in receiver_ids:
        inline_kb = InlineKeyboardMarkup(row_width=2)
        inline_kb.add(
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{message.from_user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{message.from_user.id}")
        )

        text = f"💰 Вам сдано: {data['kassa_amount']} сум\nКлиент: {data['name']}\nПринял: {data['manager']}"
        pending_data[str(message.from_user.id)] = data

        await bot.send_message(chat_id=receiver_ids[receiver], text=text, reply_markup=inline_kb)

@dp.callback_query_handler(lambda c: c.data.startswith("accept_") or c.data.startswith("reject_"))
async def handle_confirmation(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("_")[1]
    action = callback_query.data.split("_")[0]
    data = pending_data.get(user_id)

    if data:
        if action == "accept":
            sheet_name = "Продажа" if data.get("category", "").lower() == "продажа" else "Гарантия"
            sheet = client.open("Сервис").worksheet(sheet_name)
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get("name", ""),
                data.get("phone", ""),
                data.get("category", ""),
                data.get("manager", ""),
                data.get("service", ""),
                data.get("total", ""),
                data.get("payment", ""),
                data.get("cost", ""),
                data.get("kassa_amount", ""),
                data.get("receiver", "")
            ])
            await bot.send_message(chat_id=int(user_id), text=langs["ru"]["success"])
            await callback_query.message.answer("✅ Приём подтверждён")
        else:
            await bot.send_message(chat_id=int(user_id), text=langs["ru"]["rejected"])
            await callback_query.message.answer("❌ Вы отклонили приём")
        del pending_data[user_id]

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)



    














