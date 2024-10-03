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


# Функція для отримання планів з JSON файлу
def get_plan(file_path: str = "plans.json", plan_id: int | None = None) -> list[dict] | dict:
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            plans = json.load(fp)
            if plan_id is not None and plan_id < len(plans):
                return plans[plan_id]
            else:
                return plans
    except json.JSONDecodeError:
        print("Помилка декодування JSON. Перевірте формат файлу.")
        return


# Функція для отримання силових показників з JSON файлу
def get_power(file_path: str = "power.json", power_id: int | None = None) -> list[dict] | dict:
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            powers = json.load(fp)
            if power_id is not None and power_id < len(powers):
                return powers[power_id]
            else:
                return powers
    except json.JSONDecodeError:
        logging.error(f"Помилка декодування JSON з файлу: {file_path}")
        return


# Функція для зміни силових показників у JSON файлі
def change_power(power: dict, user_id: int, file_path: str = "power.json"):
    with open(file_path, "r+", encoding="utf-8") as fp:
        powers = json.load(fp)

        for user in powers:
            if user['id'] == user_id:
                user['strengths'] = power
                break
        else:
            new_user = {"id": user_id, "strengths": power}
            powers.append(new_user)

        fp.seek(0)
        json.dump(powers, fp, indent=4, ensure_ascii=False)
        fp.truncate()


# Функція для перевірки та реєстрації id користувача
def add_user_if_not_exists(user_id: int, user_name: str, file_path: str = "power.json") -> None:
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            powers = json.load(fp)

        if any(user['id'] == user_id for user in powers):
            print(f"Користувач з ID {user_id} вже існує.")
        else:
            new_user = {"id": user_id, "name": user_name}
            powers.append(new_user)

            with open(file_path, "w", encoding="utf-8") as fp:
                json.dump(powers, fp, indent=4, ensure_ascii=False)
            print(f"Користувач {user_name} з ID {user_id} успішно доданий.")
    except FileNotFoundError:
        print(f"Файл не знайдено")
    except json.JSONDecodeError:
        logging.error(f"Помилка декодування JSON з файлу: {file_path}")


# Функція для перевірки наявності користувача
def user_exists(user_id: int, file_path: str = "power.json") -> bool:
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            powers = json.load(fp)
            return any(user['id'] == user_id for user in powers)
    except FileNotFoundError:
        print(f"Файл не знайдено")
        return False
    except json.JSONDecodeError:
        logging.error(f"Помилка декодування JSON з файлу: {file_path}")
        return False
