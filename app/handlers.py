import asyncio

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states import StatusFSM
from app import texts
from app.sheets import find_by_iin

router = Router()


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.START)


@router.message(F.text.lower() == "статус")
async def status_cmd(message: Message, state: FSMContext):
    await state.set_state(StatusFSM.waiting_iin)
    await state.update_data(not_found_count=0)
    await message.answer(texts.ASK_IIN)


@router.message(StatusFSM.waiting_iin)
async def handle_iin(message: Message, state: FSMContext):
    value = message.text.strip()

    # Если пользователь снова написал «статус» — сбросить счётчик
    if value.lower() == "статус":
        await state.update_data(not_found_count=0)
        await message.answer(texts.ASK_IIN)
        return

    if not value.isdigit():
        await message.answer(texts.ONLY_DIGITS)
        return

    if len(value) != 12:
        await message.answer(texts.WRONG_LENGTH)
        return

    result = await asyncio.to_thread(find_by_iin, value)

    if result:
        await state.update_data(not_found_count=0)
        await message.answer(
            texts.FOUND_TEMPLATE.format(
                project=result.get("Название кинопроекта (название сценария)", "—"),
            )
        )
    else:
        data = await state.get_data()
        count = data.get("not_found_count", 0) + 1
        await state.update_data(not_found_count=count)

        if count >= 2:
            await message.answer(texts.NOT_FOUND_SECOND)
        else:
            await message.answer(texts.NOT_FOUND_FIRST)

    # Остаёмся в состоянии waiting_iin — пользователь может ввести новый ИИН


@router.message()
async def unknown(message: Message):
    await message.answer(texts.UNKNOWN_COMMAND)