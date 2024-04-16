from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
from transformers import AutoConfig, AutoTokenizer
import torch
from transformers import BitsAndBytesConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline


# Load the model
def init_model():
    model_name = "intfloat/multilingual-e5-large"
    model = SentenceTransformer(model_name)
    return model


def init_embeddings():
    # Load the data
    embeddings_path = "docs/multi-e5-large-clickbot_uz.pkl"
    df = pd.read_pickle(embeddings_path)

    question_embeddings_matrix = np.vstack(
        df["question_embeddings"].apply(np.array).tolist()
    ).astype(np.float32)
    # Compute the embeddings
    index = faiss.IndexFlatL2(question_embeddings_matrix.shape[1])
    index.add(question_embeddings_matrix)
    return index


# compute the embeddings
async def get_embeddings(model, query):
    query_embedding = (
        model.encode(query, convert_to_tensor=True).cpu().numpy().reshape(1, 1024)
    )
    return query_embedding


def init_llm():
    # quantization_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_compute_dtype=torch.float16,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_use_double_quant=True,
    # )

    local_llm = HuggingFacePipeline.from_model_id(
        model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        task="text-generation",
        pipeline_kwargs={"max_new_tokens": 300},
    )
    return local_llm
