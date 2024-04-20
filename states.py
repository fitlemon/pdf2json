from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    initial_state = State()
    sending_files = State()
    types_pick = State()
    wait_doc = State()
    compare_docs = State()
    wait_2nd_doc = State()
