import streamlit as st
from langchain.document_loaders import UnstructuredURLLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
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


# 2. Function for similarity search

def retrieve_info(query):
    similar_response = db.similarity_search(query, k=3)

    page_contents_array = [doc.page_content for doc in similar_response]

    # print(page_contents_array)

    return page_contents_array

# 3. Setup LLMChain and prompts

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

template = """
You are a world class representative chatbot of AriSaf Tech Ltd. 
you will share a user's message with you and you will give me the best answer based on past best practies, 
and you will follow ALL of the rules below:

1/ Response should be very similar or even identical to the past best practies, 
in terms of length, ton of voice, logical arguments and other details

2/ If the best practice are irrelevant, then try to mimic the style of the best practice to user's message

3/ Avoid any html tags in your response. Response should only be in text

Below is a message I received from the user:
{message}

Here is a list of best practies of how we normally respond to user in similar scenarios:
{best_practice}

Please write the best response that will impress the user to work with the company:
"""

prompt = PromptTemplate(
    input_variables=["message", "best_practice"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)

# 4. Retrieval augmented generation

def generate_response(message):
    best_practice = retrieve_info(message)
    response = chain.run(message=message, best_practice=best_practice)
    return response


# 5. Build an app with streamlit

def main():
    st.set_page_config(
        page_title="AriSaf chatbot", page_icon=":bird:")

    st.header("AriSaf chatbot :bird:")
    message = st.text_area("write your message")

    if message:
        st.write("Generating answer...")

        result = generate_response(message)

        st.info(result)


if __name__ == '__main__':
    main()