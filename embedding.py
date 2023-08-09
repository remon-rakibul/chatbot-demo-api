from langchain.document_loaders import UnstructuredURLLoader
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

from dotenv import load_dotenv

load_dotenv()

# 1. Vectorize the data

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

## For uploaded files

def retrieve_info_from_pdf_file(pages, query):
    db = FAISS.from_documents(pages, embeddings)
    similar_response = db.similarity_search(query, k=3)

    page_contents_array = [doc.page_content for doc in similar_response]

    # print(page_contents_array)

    return page_contents_array


# 2. Function for similarity search

def retrieve_info(query):
    similar_response = db.similarity_search(query, k=3)

    page_contents_array = [doc.page_content for doc in similar_response]

    # print(page_contents_array)

    return page_contents_array