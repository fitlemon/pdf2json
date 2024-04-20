import pdfplumber
import os
from langchain.chat_models.gigachat import GigaChat

# import SystemMessage, HumanMessage
from langchain_core.messages import SystemMessage, HumanMessage
from environs import Env

env = Env()
env.read_env()  #'../.env', recurse=False)

item_type = "unknown_device"
tes_path = env("TES_PATH")

item_templates = {
    "gas_analyser": "Название устройства,\
        Тип сенсора,\
        Материал корпуса,\
        Контролируемый газ,\
        Диапазон рабочих температур,\
        Питание,\
        Потребляемая мощность (Вт),\
        Степень защиты,\
        Срок службы",
    "gas_detector": "Название устройства,\
        Энергопотребление,\
        Материал,\
        Отверстия для кабельных вводов ,\
        Диапазон рабочих температур,\
        Питание,\
        Относительная влажность ,\
        Степень защиты,\
        Срок службы",
    "gas_flowmeter": "Название устройства,\
        Тип сенсора,\
        Материал корпуса,\
        Расход газа,\
        Тип и поверхность фланцев,\
        Расчетная температура,\
        Питание,\
        Потребляемая мощность (Вт),\
        Отбор давления,\
        Степень защиты",
    "level_indicator": "Название устройства,\
        Среда,\
        Плотность среды,\
        Рабочее давление,\
        Расчетное давление,\
        Рабочая температура,\
        Расчетная температура,\
        Температура окр. среды",
    "level_switch": "Название устройства,\
        Материал корпуса,\
        Измеряемая среда,\
        Плотность среды ,\
        Позиция",
}


def extract_text_from_pdf(pdf_path: str):
    """
    Extract text from pdf
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


# extract tables
def extract_tables_from_pdf(pdf_path: str):
    """
    Extract tables from pdf
    """
    with pdfplumber.open(pdf_path) as pdf:
        tables = []
        for page in pdf.pages:
            tables += page.extract_tables()
    # delete file
    os.remove(pdf_path)
    return tables


def get_llm_chat():
    """
    Create a chat with LLM
    """
    llm = GigaChat(credentials=env("GIGA_TOKEN"), verify_ssl_certs=False)
    return llm


async def pdf2json_llm(text, item_type, llm):
    """
    Send text to LLM and get json
    """
    print(text[:1000])
    if item_type == "unknown_device":
        input_query = f"Тебе дан текст с техническими характеристиками изделия. Сформируй из него json file, максимально емко описывающий изделие. Выбери только самую важную информацию. примерно 50% от всех характеристик."
    # input_query = f'Из документа каждую характеристику отдельно: Технические характеристики {class_name}'
    else:
        input_query = (
            f"Cоставь json-файл технических характеристик: {item_templates[item_type]}"
        )
    messages = [
        SystemMessage(content=text),
        HumanMessage(content=input_query),
    ]
    answer = await llm.ainvoke(messages)
    return answer.content


async def compare_jsons(json1, json2, llm):
    """
    Compare two jsons
    """
    system_query = """Сравни и выпиши отличия Значений в виде json в формате: {"параметры для сравнения": [названия параметров], "json1": [значения в json1], "json2": [значения в json2]}. Внизу также приведи краткий вывод:"""
    json_query = f'{{"json1": {json1}, "json2": {json2}}}'
    messages = [
        SystemMessage(content=system_query),
        HumanMessage(content=json_query),
    ]
    answer = await llm.ainvoke(messages)
    return answer.content
