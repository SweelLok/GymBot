# Імпорт глобальних бібліотек
import asyncio
import logging
import sys
import json

# Імпорт під-бібліотек
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.client.session.aiohttp import AiohttpSession

# Імпорт файлів з ПК
from models import Plan, Power
from config import BOT_TOKEN as TOKEN
from keyboards import (PlanCallBack, plan_keyboard_markup)
from functions import get_plan, get_power, change_power, user_exists, add_user_if_not_exists
from commands import (
    PLAN_COMMAND,
    POWER_COMMAND,
    CHANGE_POWER,
    START_BOT_COMMAND,
    SHOW_PLAN_COMMAND,
    SHOW_POWER_COMMAND,
    CHANGE_POWER_COMMAND,
)
from state import PowerForm

# Ініціалізація диспетчера
dp = Dispatcher()

# Ініціалізація проксі-сервера
session = AiohttpSession(proxy='http://proxy.server:3128')


# Обробка команди для отримання плану тренування
@dp.message(PLAN_COMMAND)
async def plan(message: Message) -> None:
    user_id = message.from_user.id
    if not user_exists(user_id):
        await message.answer("Ваш обліковий запис не знайдено. Будь ласка, спочатку запустіть команду /start.")
        return
    data = get_plan()
    markup = plan_keyboard_markup(plans_list=data)
    await message.answer(f"Ось ваш план тренування:", reply_markup=markup)


# Обробка натискання на кнопку з планом
@dp.callback_query(PlanCallBack.filter())
async def calb_plans(callback: CallbackQuery, callback_data: PlanCallBack) -> None:
    plan_id = callback_data.id
    try:
        user_id = callback.from_user.id
        if not user_exists(user_id):
            await callback.answer("Ваш обліковий запис не знайдено. Будь ласка, спочатку запустіть команду /start.")
            return

        plan_data = get_plan(plan_id=plan_id)
        if not plan_data:
            await callback.answer("Не вдалося знайти план.", show_alert=True)
            return

        plan = Plan(**plan_data)
        text = (
            f"День: {plan.name}\n"
            f"Спліт: {plan.split}\n"
            f"Вправи: {plan.exercise}"
        )

        reply_markup = callback.message.reply_markup
        await callback.message.edit_text(text, reply_markup=reply_markup)
        await callback.answer()

    except TypeError as e:
        await callback.answer("Помилка в даних плану.", show_alert=True)
        print(f"Помилка TypeError: {e}")
    except Exception as e:
        await callback.answer("Виникла непередбачувана помилка.", show_alert=True)
        print(f"Виникла помилка: {e}")


# Обробка команди для відображення силових показників
@dp.message(POWER_COMMAND)
async def show_power(message: Message) -> None:
    user_id = message.from_user.id
    powers = get_power()
    user_power_data = None
    for power in powers:
        if power["id"] == user_id:
            user_power_data = power
            break
    if not user_power_data:
        await message.answer("Ваш обліковий запис не знайдено. Будь ласка, спочатку запустіть команду /start.")
        return

    strengths = user_power_data.get("strengths", {})
    keys = {
        "жим лежачи": "benchpress",
        "віджимання": "pushups",
        "підтягування": "pullingup",
        "присідання": "squatting",
        "французький жим": "frechpress",
        "штанга на біцепс": "onbiceps"
    }

    # Діагностичний вивід
    print("Сили:", strengths)  # Виводить вміст strengths

    if strengths:
        response_text = "Ваші силові показники:\n\n"

        for display_key, actual_key in keys.items():
            if actual_key in strengths:
                value = strengths[actual_key]
                response_text += f"{display_key}: {value}\n"

        await message.answer(response_text)
    else:
        await message.answer("Не вдалося отримати силові показники.")


# Обробка команди для зміни силових показників
@dp.message(CHANGE_POWER)
async def power_change(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if not user_exists(user_id):
        await message.answer("Ваш обліковий запис не знайдено. Будь ласка, спочатку запустіть команду /start.")
        return

    await state.set_state(PowerForm.benchpress)
    await message.answer(f"Введіть вагу, яку ви жмете (жим лежачи)", reply_markup=ReplyKeyboardRemove())


# Обробка введення ваги для жиму лежачи
@dp.message(PowerForm.benchpress)
async def power_benchpress(message: Message, state: FSMContext) -> None:
    await state.update_data(benchpress=message.text)
    await message.answer(f"Введіть кількість віджимань", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PowerForm.pushups)


# Обробка введення кількості віджимань
@dp.message(PowerForm.pushups)
async def power_pushups(message: Message, state: FSMContext) -> None:
    await state.update_data(pushups=message.text)
    await message.answer(f"Введіть кількість підтягувань", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PowerForm.pullingup)


# Обробка введення кількості підтягувань
@dp.message(PowerForm.pullingup)
async def power_pullingup(message: Message, state: FSMContext) -> None:
    await state.update_data(pullingup=message.text)
    await message.answer(f"Введіть кількість присідань", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PowerForm.squatting)


# Обробка введення кількості присідань
@dp.message(PowerForm.squatting)
async def power_squatting(message: Message, state: FSMContext) -> None:
    await state.update_data(squatting=message.text)
    await message.answer(f"Введіть вагу, яку ви жмете (французький жим)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PowerForm.frechpress)


# Обробка введення ваги для французького жиму
@dp.message(PowerForm.frechpress)
async def power_frechpress(message: Message, state: FSMContext) -> None:
    await state.update_data(frechpress=message.text)
    await message.answer(f"Введіть вагу, яку ви піднімаєте (штанга на біцепс)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PowerForm.onbiceps)


# Обробка введення ваги для підйому на біцепс
@dp.message(PowerForm.onbiceps)
async def power_onbiceps(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    data["onbiceps"] = message.text
    user_id = message.from_user.id
    power_data = Power(**data)
    change_power(power_data.model_dump(), user_id)
    await state.clear()
    await message.answer(f"Силові успішно змінені", reply_markup=ReplyKeyboardRemove())


# Обробка команди старту бота
@dp.message(CommandStart)
async def start(message: Message) -> None:
    add_user_if_not_exists(message.from_user.id, message.from_user.full_name)
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!👋\n"
        f"\n"
        f"Цей бот допоможе дізнатися твій план тренування\n"
        f"Також ти зможеш слідкувати за зміною твоїх силових💪"
    )


# Основна функція для запуску бота
async def main() -> None:
    bot = Bot(token=TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands([
        START_BOT_COMMAND,
        SHOW_PLAN_COMMAND,
        SHOW_POWER_COMMAND,
        CHANGE_POWER_COMMAND,
    ])

    await dp.start_polling(bot)


# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
