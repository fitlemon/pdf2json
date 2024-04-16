from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
import json
import re
import logging

import kb
import text
import utils

from aiogram import flags
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
import os

# import utils
from states import Gen


router = Router()

DOCS_PATH = "docs"


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    """
    Bot actions for start command
    """
    # send message to user
    await state.set_state(Gen.initial_state)  # set state to initial
    await msg.answer(text.start, reply_markup=kb.main_kb)


@router.callback_query(F.data.contains("main_menu"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.initial_state)  # set state to initial
    await clbck.message.answer(text.start, reply_markup=kb.main_kb)


@router.callback_query(F.data.contains("sending_files"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.sending_files)
    await clbck.message.answer(text.sending_files, reply_markup=kb.sending_files_kb)


@router.callback_query(F.data.contains("types_pick"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.types_pick)
    await clbck.message.answer(text.types_pick, reply_markup=kb.types_kb)


@router.callback_query(F.data.contains("gas_analyser"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    utils.item_type = "gas_analyser"
    await state.set_state(Gen.wait_doc)
    await clbck.message.answer(text.wait_doc, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("gas_detector"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    utils.item_type = "gas_detector"
    await state.set_state(Gen.wait_doc)
    await clbck.message.answer(text.wait_doc, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("gas_flowmeter"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    utils.item_type = "gas_flowmeter"
    await state.set_state(Gen.wait_doc)
    await clbck.message.answer(text.wait_doc, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("level_indicator"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    utils.item_type = "level_indicator"
    await state.set_state(Gen.wait_doc)
    await clbck.message.answer(text.wait_doc, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("level_switch"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    utils.item_type = "level_switch"
    await state.set_state(Gen.wait_doc)
    await clbck.message.answer(text.wait_doc, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("unknown_device"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    utils.item_type = "unknown_device"
    await state.set_state(Gen.wait_doc)
    await clbck.message.answer(text.wait_doc, reply_markup=kb.menu_kb)


@router.message(Gen.wait_doc)
@router.message(F.content_type == "document")
async def load_files(msg: Message, state: FSMContext, bot):
    if msg.document:
        file_id = msg.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_name = msg.document.file_name
        # Download the file
        file = await bot.download_file(file_path)
        print("Take file:", file_name)
        # Save the file
        if not os.path.exists(DOCS_PATH):
            os.makedirs(DOCS_PATH)
        file_name = os.path.join(DOCS_PATH, file_name)
        with open(file_name, "wb") as f:
            f.write(file.read())
        # send file to user
        await msg.reply("Файл принят. Пожалуйста, подождите...")
        # extract text from pdf
        text = utils.extract_text_from_pdf(file_name)
        # send text to user
        # await msg.reply(
        #     (
        #         f"```markdown\nКусок текста: \n{text[:1000]}\n```"
        #         if text
        #         else "Пустой файл"
        #     ),
        #     parse_mode="Markdown",
        # )
        # get llm chat
        llm = utils.get_llm_chat()
        # send text to llm
        item_type = utils.item_type
        json_text = await utils.pdf2json_llm(text, item_type, llm)
        # send json to user
        print(json_text)
        await msg.reply(
            "```json\n" + json_text + "\n```",
            parse_mode="Markdown",
            reply_markup=kb.menu_kb,
        )

    else:
        await msg.reply("Я принимаю только магические документы...")
