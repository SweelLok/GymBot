from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class PlanCallBack(CallbackData, prefix="plan", sep=";"):
    id: int
    name: str


def plan_keyboard_markup(plans_list: list[dict]):
    builder = InlineKeyboardBuilder()

    for index, plan_data in enumerate(plans_list):
        callback_data = PlanCallBack(id=index, **plan_data)
        builder.button(
            text=f"{callback_data.name}",
            callback_data=callback_data.pack()
        )
        builder.adjust(1, repeat=True)
    return builder.as_markup()
