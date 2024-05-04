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
from langchain_community.llms import HuggingFaceHub

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
    # llm = GigaChat(credentials=env.str("GIGA_TOKEN"), verify_ssl_certs=False)
    # Open ai llm
    # llm = HuggingFaceHub(
    #     repo_id="IlyaGusev/saiga_llama3_8b",
    #     task="text-generation",
    #     model_kwargs={
    #         "max_new_tokens": 1024,
    #         "top_k": 30,
    #         "temperature": 0.1,
    #         "repetition_penalty": 1.03,
    #     },
    #     huggingfacehub_api_token=env.str("HUGGINGFACEHUB_API_TOKEN"),
    # )
    llm = ChatOpenAI(api_key=env.str("OPENAI_API_KEY"))
    return llm


async def pdf2json_llm(text, item_type, llm):
    """
    Send text to LLM and get json
    """
    print(text[:1000])
    if item_type == "unknown_device":
        input_query = f"""Ты профессиональный frontend-разработчик. 
Контекст: Я отправлю тебе технический паспорт изделия. 
Твоя задача: найти в техническом паспорте основные технические характеристики изделия и их значения.
Формат: 
1) выведи ответ в формате json. 
2) Все ключи и значения пиши только на русском языке. Названия параметров содержат единицы измерения. 
3)Все значения параметров обернуты в кавычки, даже числовые, например: "100", "200-300" и т.д.
Вот технический паспорт:
{text}"""
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


async def compare_docs(text1, text2, llm):
    """
    Compare two jsons
    """
    system_query = f"""Ты профессиональный технический писатель. 
Контекст: Я отправлю тебе два технических паспорта. 
Твоя задача: найти в каждом техническом паспорте основные технические характеристики изделия и их значения, сравнить найденные характеристики между собой и выписать результат в виде сравнительной таблицы.
Формат: выведи ответ в виде таблицы markdown. После таблицы коротко и емко опиши, по каким характеристикам изделия отличаются друг от друга. Выписывай только различия. Стиль речи сухой, технический. Пиши только на русском языке.
Важные замечания: 
1) переведи все параметры в одинаковую систему измерения, если это необходимо. 
2) Все значения в таблице выдели кавычками, например:
| Характеристика                  | Паспорт 1               | Паспорт 2               |
|----------------------------------|-------------------------|-------------------------|
| Мощность двигателя, л.с.         | "59,0"                   | "не менее 40"             |
3) Исключи из сравнения параметры, которые не влияют на работу устройства или которые одинаковы в жвух паспортах. Не забудь про единицы измерения. Проверь свой ответ. За хорошую и точную работу тебя ждет бонус.
"""
    user_query = f"""
Вот первый паспорт:
{text1}
Вот второй паспорт:
{text2}
"""
    messages = [
        SystemMessage(content=system_query),
        HumanMessage(content=user_query),
    ]
    answer = await llm.ainvoke(messages)
    return answer.content


async def compare_docs_conclusion(text1, text2, llm):
    """
    Compare two jsons
    """
    query = f"""Ты профессиональный технический писатель. 
Контекст: Я отправлю тебе два технических паспорта. 
Твоя задача: найти в каждом техническом паспорте основные технические характеристики изделия и их значения, сравнить найденные характеристики между собой и выписать результат в виде короткого вывода.
Формат: выведи ответ в виде текстового вывода. Коротко и емко опиши, по каким характеристикам изделия отличаются друг от друга. Выписывай только различия. Стиль речи сухой, технический.
Вот первый паспорт:
{text1}
Вот второй паспорт:
{text2}
"""
    messages = [
        HumanMessage(content=query),
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
    llm = ChatOpenAI(api_key=env.str("OPENAI_API_KEY"))
    # llm = GigaChat(credentials=env.str("GIGA_TOKEN"), verify_ssl_certs=False)
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
