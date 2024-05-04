from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import json
import re
import logging
import tabulate
import kb
import texts
import utils
import json_repair
import markdown
import pandas as pd

import dataframe_image as dfi
from aiogram import flags
from aiogram.fsm.context import FSMContext
import os
import ocr
from aiogram.types import ContentType, FSInputFile


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
    await msg.answer(texts.start, reply_markup=kb.main_kb)


@router.callback_query(F.data.contains("main_menu"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for main_menu
    """

    await state.set_state(Gen.initial_state)  # set state to initial
    await clbck.message.answer(texts.start, reply_markup=kb.main_kb)


@router.callback_query(F.data.contains("sending_files"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for sending_files
    """
    await state.set_state(Gen.wait_doc)
    await clbck.message.answer(texts.types_pick, reply_markup=kb.types_kb)


@router.callback_query(F.data.contains("gas_analyser"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for gas_analyser
    """
    state = await state.get_state()
    if state == Gen.wait_doc:
        reply = texts.wait_doc
    else:
        reply = texts.compare_docs
    utils.item_type = "gas_analyser"
    await clbck.message.answer(reply, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("gas_detector"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for gas_detector
    """
    state = await state.get_state()
    if state == Gen.wait_doc:
        reply = texts.wait_doc
    else:
        reply = texts.compare_docs
    utils.item_type = "gas_detector"
    await clbck.message.answer(reply, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("gas_flowmeter"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for gas_flowmeter
    """
    state = await state.get_state()
    if state == Gen.wait_doc:
        reply = texts.wait_doc
    else:
        reply = texts.compare_docs
    utils.item_type = "gas_flowmeter"
    await clbck.message.answer(reply, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("level_indicator"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for level_indicator
    """
    state = await state.get_state()
    if state == Gen.wait_doc:
        reply = texts.wait_doc
    else:
        reply = texts.compare_docs
    utils.item_type = "level_indicator"
    await clbck.message.answer(reply, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("level_switch"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for level_switch
    """
    state = await state.get_state()
    if state == Gen.wait_doc:
        reply = texts.wait_doc
    else:
        reply = texts.compare_docs
    utils.item_type = "level_switch"
    await clbck.message.answer(reply, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("unknown_device"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for unknown_device
    """
    state = await state.get_state()
    if state == Gen.wait_doc:
        reply = texts.wait_doc
    else:
        reply = texts.compare_docs
    utils.item_type = "unknown_device"
    await clbck.message.answer(reply, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("parse_all"))
async def events_by_spec_genre(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for parse_all
    """
    state = await state.get_state()
    if state == Gen.wait_doc:
        reply = texts.wait_doc
    else:
        reply = texts.compare_docs
    utils.item_type = "unknown_device"
    await clbck.message.answer(reply, reply_markup=kb.menu_kb)


@router.message(
    (F.content_type == ContentType.DOCUMENT) | (F.content_type == ContentType.PHOTO)
)
async def handle_files(msg: Message, state: FSMContext, bot):
    """
    Bot actions for loading files
    """
    print("handle_files")
    state_ = await state.get_state()
    if state_ not in [Gen.wait_doc, Gen.compare_docs, Gen.wait_2nd_doc, Gen.chat_pdf]:
        await msg.reply(
            "Выберите сначала раздел....",
            reply_markup=kb.menu_kb,
        )
        return None
    else:
        if msg.content_type == "document":
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

            # extract text from pdf
            # check if file is pdf
            if file_name.endswith(".pdf"):
                text = utils.extract_text_from_pdf(file_name)
                if len(text) < 2000:
                    await msg.reply(
                        "Файл принят. Это PDF с НЕраспознанным текстом. Попробуем распознать текст с помощью магии 🎇. Пожалуйста, подождите ответа нейронной сети ✨...Если текст не распознается, попробуйте отправить фото документа в формате jpg, png...Например, сделав скриншот.",
                        reply_markup=kb.menu_kb,
                    )
                    print("its PDF not recognized")
                    imgs = ocr.pdf_to_img(file_name)
                    text = ""
                    for img in imgs:
                        text += ocr.detect_text(img)
                else:
                    await msg.reply(
                        "Файл принят. Это PDF с распознанным текстом. Пожалуйста, подождите ответа нейронной сети ✨...",
                        reply_markup=kb.menu_kb,
                    )
            elif file_name.endswith(".jpg") or file_name.endswith(".png"):
                print("its IMG not recognized")
                await msg.reply(
                    "Файл принят. Это картинка с НЕраспознанным текстом. Попробуем распознать текст с помощью магии 🎇. Пожалуйста, подождите ответа нейронной сети ✨...",
                    reply_markup=kb.menu_kb,
                )
                text = ocr.detect_text(file_name)
            else:
                await msg.reply(
                    "Я принимаю только магические документы c текстом в формате pdf, jpg, png...",
                    reply_markup=kb.menu_kb,
                )
                return None
        elif msg.content_type == "photo":
            file_name = os.path.join("docs", f"{msg.photo[-1].file_id}.jpg")
            await bot.download(msg.photo[-1], destination=file_name)
            print("its IMG not recognized")
            await msg.reply(
                "Файл принят. Это картинка с НЕраспознанным текстом. Попробуем распознать текст с помощью магии 🎇. Пожалуйста, подождите ответа нейронной сети ✨...",
                reply_markup=kb.menu_kb,
            )
            text = ocr.detect_text(file_name)
        else:
            await msg.reply(
                "Я принимаю только магические документы в формате pdf, jpg, png....",
                reply_markup=kb.menu_kb,
            )
            return None
        if state_ == Gen.chat_pdf:
            chunks = await utils.get_text_chunks(text)
            await msg.reply(
                "Текст распознан. Подождите пока текст загрузится в векторную базу...⌚"
            )
            vectorstore = await utils.get_vectorstore(chunks, str(msg.from_user.id))
            await msg.reply(texts.wait_chat_pdf, reply_markup=kb.menu_kb)
            await state.set_state(Gen.wait_chat_pdf)
            return None
        if state_ == Gen.wait_doc:
            llm = utils.get_llm_chat()
            # send text to llm
            item_type = utils.item_type
            json_text = await utils.pdf2json_llm(text, item_type, llm)
            print(f"JSON FROM LLM:\n\n{json_text}")
            json_dict = json_repair.loads(json_text)
            json_text = json_repair.repair_json(json_text, return_objects=True)
            json_text = json.dumps(json_text, ensure_ascii=False, indent=4)
            # save json to file
            # convert str json to dict
            # json_text = json_text.strip().lstrip("```json").rstrip("```").strip()
            # json_dict = eval(json_text)
            with open(
                f"docs/jsonfile_{msg.from_user.id}.json", "w", encoding="utf-8"
            ) as f:
                json.dump(json_dict, f, ensure_ascii=False, indent=4)
            # send json file to user
            json_from_pc = FSInputFile(f"docs/jsonfile_{msg.from_user.id}.json")
            await msg.reply_document(json_from_pc, reply_markup=kb.menu_kb)
            # send json to user
            print(f"JSON FROM JSONREPAIR:\n\n{json_text}")
            await msg.reply(
                "```json\n" + json_text + "\n```",
                parse_mode="Markdown",
                reply_markup=kb.menu_kb,
            )
            if utils.item_type != "unknown_device":
                json_table = tabulate.tabulate(json_dict.items(), tablefmt="grid")
                await msg.reply(
                    f"```markdown\n{json_table}\n```",
                    parse_mode="Markdown",
                    reply_markup=kb.menu_kb,
                )

        if state_ == Gen.compare_docs:
            with open(f"docs/{msg.from_user.id}_1.txt", "w", encoding="utf-8") as f:
                f.write(text)
            await msg.reply(
                texts.wait_2nd_doc,
                reply_markup=kb.menu_kb,
            )
            await state.set_state(Gen.wait_2nd_doc)

        elif state_ == Gen.wait_2nd_doc:
            with open(f"docs/{msg.from_user.id}_2.txt", "w", encoding="utf-8") as f:
                f.write(text)
            await msg.reply(
                texts.wait_to_compare,
                reply_markup=kb.menu_kb,
            )
            # compare jsons
            with open(f"docs/{msg.from_user.id}_1.txt", "r", encoding="utf-8") as f:
                text1 = f.read()
            with open(f"docs/{msg.from_user.id}_2.txt", "r", encoding="utf-8") as f:
                text2 = f.read()
            llm = utils.get_llm_chat()
            llm_answer = await utils.compare_docs(text1, text2, llm)
            print(llm_answer)
            table_start = llm_answer.find("|")
            table_end = llm_answer.rfind("|")
            diff_table = llm_answer[table_start : table_end + 1]
            conclusion = llm_answer[table_end + 1 :]
            table_html = markdown.markdown(
                diff_table, extensions=["markdown.extensions.tables"]
            )
            table_df = pd.read_html(table_html)[0]
            # table_df = table_df.style.background_gradient()
            png_file_name = f"docs/{msg.from_user.id}_compare.png"
            dfi.export(table_df, png_file_name)
            png_from_pc = FSInputFile(png_file_name)
            table_df.to_excel(f"docs/{msg.from_user.id}_compare.xlsx")
            table_df.to_json(f"docs/{msg.from_user.id}_compare.json")
            await msg.reply_photo(png_from_pc, reply_markup=kb.compare_menu_kb)

            # final_table = tabulate.tabulate(table_df, tablefmt="grid")

            # conclusion = await utils.compare_docs_conclusion(text1, text2, llm)
            # read diff json
            # await msg.reply(
            #     f"```markdown\n{final_table}\n```",
            #     parse_mode="Markdown",
            #     reply_markup=kb.compare_menu_kb,
            # )
            await msg.reply(
                f"```\n{conclusion}\n```",
                parse_mode="Markdown",
                reply_markup=kb.menu_kb,
            )


@router.callback_query(F.data.contains("bot_info"))
async def bot_info(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for bot_info
    """
    await clbck.message.answer(texts.bot_info, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("compare_docs"))
async def compare_docs(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for compare_docs
    """
    await state.set_state(Gen.compare_docs)
    await clbck.message.answer(texts.types_pick, reply_markup=kb.types_kb)


# @router.callback_query(F.data.contains("compare_again"))
# async def compare_again(clbck: CallbackQuery, state: FSMContext):
#     """
#     Bot actions for compare_again
#     """
#     llm = utils.get_llm_chat()
#     print(f"clbck.message.chat.id: {clbck.message.chat.id}")
#     with open(f"docs/{clbck.message.chat.id}_1.json", "r", encoding="utf-8") as f:
#         json1 = json.load(f)
#     with open(f"docs/{clbck.message.chat.id}_2.json", "r", encoding="utf-8") as f:
#         json2 = json.load(f)
#     diff_json = await utils.compare_(str(json1), str(json2), llm)
#     conclusion = await utils.compare_jsons_conclusion(str(json1), str(json2), llm)
#     # read diff json
#     diff = json_repair.repair_json(diff_json, return_objects=True)
#     diff = json.dumps(diff, ensure_ascii=False, indent=4)
#     diff_dict = json_repair.loads(diff)
#     await clbck.message.reply(
#         f"```json\n{diff}\n```",
#         parse_mode="Markdown",
#         reply_markup=kb.menu_kb,
#     )
#     diff_table = tabulate.tabulate(diff_dict, headers="keys", tablefmt="grid")
#     print(diff_table)
#     await clbck.message.reply(
#         f"```markdown\n{diff_table}\n```",
#         parse_mode="Markdown",
#         reply_markup=kb.compare_menu_kb,
#     )
#     await clbck.message.reply(
#         f"```\n{conclusion}\n```",
#         parse_mode="Markdown",
#         reply_markup=kb.compare_menu_kb,
#     )


@router.callback_query(F.data.contains("chat_pdf"))
async def chat_with_pdf(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for chat_pdf
    """
    await state.set_state(Gen.chat_pdf)
    await clbck.message.answer(texts.chat_pdf, reply_markup=kb.menu_kb)


@router.message(F.content_type == ContentType.TEXT)
async def handle_text_messages(msg: Message, state: FSMContext, bot):
    """
    Bot actions for text messages
    """
    state_ = await state.get_state()
    if state_ == Gen.wait_chat_pdf:
        vectorstore = utils.user_vectorstores.get(str(msg.from_user.id))
        if vectorstore is None:
            await msg.reply(
                "Вы не отправляли документ для обработки. Пожалуйста, отправьте документ для обработки, чтобы продолжить...",
                reply_markup=kb.menu_kb,
            )
            return None
        llm = await utils.get_conversation_chain(vectorstore)
        answer = await llm.ainvoke(msg.text)
        await msg.reply(answer.get("answer"), reply_markup=kb.menu_kb)
    else:
        await msg.reply(
            "Выберите сначала раздел....",
            reply_markup=kb.menu_kb,
        )


@router.callback_query(F.data.contains("download_json"))
async def download_json(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for download_json
    """
    # await clbck.message.answer("Скачивание JSON файла...", reply_markup=kb.menu_kb)
    json_from_pc = FSInputFile(f"docs/{clbck.message.chat.id}_compare.json")
    await clbck.message.reply_document(json_from_pc, reply_markup=kb.menu_kb)


@router.callback_query(F.data.contains("download_xls"))
async def download_xls(clbck: CallbackQuery, state: FSMContext):
    """
    Bot actions for download_xls
    """
    xlsx_from_pc = FSInputFile(f"docs/{clbck.message.chat.id}_compare.xlsx")
    await clbck.message.reply_document(xlsx_from_pc, reply_markup=kb.menu_kb)
