from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class PowerForm(StatesGroup):
    benchpress = State()
    pushups = State()
    pullingup = State()
    squatting = State()
    frechpress = State()
    onbiceps = State()
