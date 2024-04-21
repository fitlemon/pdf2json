import pdfplumber
import os
from langchain.chat_models.gigachat import GigaChat
from langchain.text_splitter import CharacterTextSplitter

# import SystemMessage, HumanMessage
from langchain_core.messages import SystemMessage, HumanMessage
from environs import Env
from langchain.vectorstores.faiss import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

env = Env()
env.read_env()  #'../.env', recurse=False)

item_type = "unknown_device"
tes_path = env("TES_PATH")
user_vectorstores = {}

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
    llm = GigaChat(credentials=env.str("GIGA_TOKEN"), verify_ssl_certs=False)
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
    system_query = """Сравни и выпиши отличия Значений в виде json в формате: {"параметры для сравнения": [названия параметров в виде python list], "json1": [значения параметров в json1 в виде python list], "json2": [значения параметров в json2 в виде python list]}:"""
    json_query = f'{{"json1": {json1}, "json2": {json2}}}'
    messages = [
        SystemMessage(content=system_query),
        HumanMessage(content=json_query),
    ]
    answer = await llm.ainvoke(messages)
    return answer.content


async def compare_jsons_conclusion(json1, json2, llm):
    """
    Compare two jsons
    """
    system_query = (
        """Сравни два json файла и напиши, в чем их различия в выводах по пунктам."""
    )
    json_query = f'{{"json1": {json1}, "json2": {json2}}}'
    messages = [
        SystemMessage(content=system_query),
        HumanMessage(content=json_query),
    ]
    answer = await llm.ainvoke(messages)
    return answer.content


async def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


async def get_vectorstore(text_chunks, user_id):
    # sembeddings = OpenAIEmbeddings()
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=env.str("HUGGINGFACEHUB_API_TOKEN"),
        model_name="intfloat/multilingual-e5-large",
    )
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    user_vectorstores[user_id] = vectorstore
    return vectorstore


async def get_conversation_chain(vectorstore):
    # llm = ChatOpenAI(api_key=env.str("OPENAI_API_KEY"))
    llm = GigaChat(credentials=env.str("GIGA_TOKEN"), verify_ssl_certs=False)
    # llm = HuggingFaceHub(
    #     repo_id="google/flan-t5-xxl",
    #     model_kwargs={"temperature": 0.5, "max_length": 512},
    # )
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retriever(), memory=memory
    )
    return conversation_chain


async def get_response(conversation_chain, user_query):
    response = conversation_chain({"question": user_query})
    return response
