from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from logger_config import setup_logger
from dotenv import load_dotenv

load_dotenv()

local_logger = setup_logger(__name__)

urls = [
    "https://arisaftech.com/",
    "https://arisaftech.com/services/",
    "https://arisaftech.com/about/",
    "https://arisaftech.com/career/",
]

loader = UnstructuredURLLoader(urls=urls)
data = loader.load()

embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(data, embeddings)

def load_file_to_db(pages):
    db = FAISS.from_documents(pages, embeddings)
    return db

def retrieve_info_from_file(db, query):
    similar_response = db.similarity_search(query, k=3)
    # local_logger.info(f'query: {query}')
    # local_logger.info(f'similarity search: {similar_response}')
    page_contents_array = [doc.page_content for doc in similar_response]
    return page_contents_array


def retrieve_info(query):
    similar_response = db.similarity_search(query, k=3)
    # local_logger.info(f'query: {query}')
    # local_logger.info(f'similarity search: {similar_response}')
    page_contents_array = [doc.page_content for doc in similar_response]
    return page_contents_array