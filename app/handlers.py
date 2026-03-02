import asyncio

from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.states import StatusFSM
from app import texts
from app.sheets import find_by_iin, get_categories

router = Router()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="\U0001F3AC Статус заявки"), KeyboardButton(text="\u2139\ufe0f Информация")],
    ],
    resize_keyboard=True,
)


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.START, reply_markup=main_keyboard)


@router.message(Command("info"))
@router.message(F.text == "\u2139\ufe0f Информация")
async def info_cmd(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="\U0001F3AC Информация по конкурсу",
            url="https://kazakhcinema.kz/page111495056.html"
        )],
        [InlineKeyboardButton(
            text="\U0001F310 Официальный сайт Центра",
            url="https://kazakhcinema.kz/kz"
        )],
    ])
    await message.answer(texts.INFO_MENU, reply_markup=keyboard)


@router.message(F.text.lower() == "статус")
@router.message(F.text == "\U0001F3AC Статус заявки")
async def status_cmd(message: Message, state: FSMContext):
    # спрашиваем сначала категорию
    await state.set_state(StatusFSM.waiting_category)
    await state.update_data(not_found_count=0)

    # клавиатура с вариантами категорий
    cats = get_categories()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=c)] for c in cats],
        resize_keyboard=True,
    )
    await message.answer(texts.ASK_CATEGORY, reply_markup=keyboard)


@router.message(StatusFSM.waiting_category)
async def handle_category(message: Message, state: FSMContext):
    choice = message.text.strip()
    cats = get_categories()
    if choice not in cats:
        # повторим клавиатуру
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=c)] for c in cats],
            resize_keyboard=True,
        )
        await message.answer(texts.ASK_CATEGORY, reply_markup=keyboard)
        return

    # сохраним выбор и перейдём к вводу ИИН
    await state.update_data(category=choice, not_found_count=0)
    await state.set_state(StatusFSM.waiting_iin)
    # вернуть основную клавиатуру, чтобы пользователь мог снова выбрать.
    await message.answer(texts.ASK_IIN, reply_markup=main_keyboard)


@router.message(StatusFSM.waiting_iin)
async def handle_iin(message: Message, state: FSMContext):
    value = message.text.strip()

    # Если пользователь снова написал «статус» — сбросить счётчик
    if value.lower() == "статус":
        await state.update_data(not_found_count=0)
        # вернуться к выбору категории
        await state.set_state(StatusFSM.waiting_category)
        cats = get_categories()
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=c)] for c in cats],
            resize_keyboard=True,
        )
        await message.answer(texts.ASK_CATEGORY, reply_markup=keyboard)
        return

    if not value.isdigit():
        await message.answer(texts.ONLY_DIGITS)
        return

    if len(value) != 12:
        await message.answer(texts.WRONG_LENGTH)
        return

    data = await state.get_data()
    selected_cat = data.get("category")
    result = await asyncio.to_thread(find_by_iin, value, selected_cat)

    if result:
        await state.update_data(not_found_count=0)
        await message.answer(
            texts.FOUND_TEMPLATE.format(
                project=result.get("Название кинопроекта (название сценария)", "—"),
                category=result.get("_category", "—"),
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