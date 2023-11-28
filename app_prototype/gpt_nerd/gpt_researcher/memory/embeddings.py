from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()


class Memory:
    def __init__(self, **kwargs):
        self._embeddings = OpenAIEmbeddings(openai_api_key = os.getenv("OPENAI_API_KEY"))

    def get_embeddings(self):
        return self._embeddings
