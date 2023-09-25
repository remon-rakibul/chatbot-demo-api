import codecs
import pinecone
from langchain.vectorstores import Pinecone
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

index_name = "arisaf-chatbot"
embeddings = OpenAIEmbeddings()
pinecone.init(
    api_key="489f9d8c-eb70-4f3a-b71c-264d5d6810a0",
    environment="asia-southeast1-gcp-free"
)

db = Pinecone.from_documents(data, embeddings, index_name=index_name)

def load_file_to_db(pages):
    db = Pinecone.from_documents(pages, embeddings, index_name=index_name)
    return db

def retrieve_info_from_file(db, query):
    similar_response = db.similarity_search(query, k=3)
    # local_logger.info(f'query: {query}')
    # local_logger.info(f'similarity search: {similar_response}')
    page_contents_array = [codecs.decode(doc.page_content, 'unicode_escape') for doc in similar_response]
    return page_contents_array


def retrieve_info(query):
    similar_response = db.similarity_search(query, k=3)
    # local_logger.info(f'query: {query}')
    # local_logger.info(f'similarity search: {similar_response}')
    page_contents_array = [codecs.decode(doc.page_content, 'unicode_escape') for doc in similar_response]
    print(page_contents_array)
    return page_contents_array