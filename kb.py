from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    FSInputFile,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


main_kb = [
    [
        InlineKeyboardButton(
            text="🔎Спарсить паспорт изделия", callback_data="sending_files"
        )
    ],
    [
        InlineKeyboardButton(
            text="↔️ Сравнить два паспорта", callback_data="compare_docs"
        )
    ],
    [InlineKeyboardButton(text="💬 Чат с документом", callback_data="chat_pdf")],
    [InlineKeyboardButton(text="💡 Инфо о боте", callback_data="bot_info")],
]
main_kb = InlineKeyboardMarkup(inline_keyboard=main_kb)


sending_files_kb = [
    [InlineKeyboardButton(text="🔩 Выбрать тип изделия", callback_data="types_pick")],
    [InlineKeyboardButton(text="📃Спарсить весь документ", callback_data="parse_all")],
]

sending_files_kb = InlineKeyboardMarkup(inline_keyboard=sending_files_kb)


types_kb = [
    [InlineKeyboardButton(text="🔬Газоанализатор", callback_data="gas_analyser")],
    [InlineKeyboardButton(text="♨️Детектор газов", callback_data="gas_detector")],
    [
        InlineKeyboardButton(
            text="📉 Расходомер/счётчик газа", callback_data="gas_flowmeter"
        )
    ],
    [InlineKeyboardButton(text="🛀Указатель уровня", callback_data="level_indicator")],
    [InlineKeyboardButton(text="🛁Сигнализатор уровня", callback_data="level_switch")],
    [InlineKeyboardButton(text="❓Я не знаю тип", callback_data="unknown_device")],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    ],
]

types_kb = InlineKeyboardMarkup(inline_keyboard=types_kb, resize_keyboard=True)


menu_kb = [
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    ]
]

menu_kb = InlineKeyboardMarkup(inline_keyboard=menu_kb)


compare_menu_kb = [
    [
        InlineKeyboardButton(text="📅 Скачать в Excel", callback_data="download_xls"),
        InlineKeyboardButton(text="〰️ Скачать в Json", callback_data="download_json"),
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    ],
]

compare_menu_kb = InlineKeyboardMarkup(inline_keyboard=compare_menu_kb)
