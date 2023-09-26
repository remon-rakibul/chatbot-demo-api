from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
# from logger_config import setup_chat_logger
from langchain.chains import LLMChain
from logger_config import ChatLogger
import embedding
import os

# local_logger = setup_chat_logger(__name__)

llm = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0, model="gpt-3.5-turbo-16k-0613")

# with open('api.log', 'r') as f:
#     context = f.read()
#     words = context[-1600:].split()
#     tokens = ' '.join(words[-200:])
    # print(tokens)

log_directory = "chat_logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

chat_logger = ChatLogger(log_directory)


template = """
You are a world class representative chatbot of AriSaf Tech Ltd. 
I will share a user's message and previous chat history with you and you will give me the best answer based on past best practies, 
and you will follow ALL of the rules below:

1/ Response should be very similar or even identical to the past best practies, 
in terms of length, ton of voice, logical arguments and other details

2/ If the best practice are irrelevant, then try to mimic the style of the best practice to user's message

3/ Avoid any html tags in your response

4/ Don't hallucinate if don't understand any topic or if you don't have any data on a topic, at that time just admit you don't know the answer.

5/ Keep the response short and concise

6/ Include important informations in a structured way

7/ Format the response with newlines and bullet points to if necessary

8/ Behave politely and professionally in your response

9/ Perform basic arithmetic operations with step by step explanations

10/ If needed break down the answer to give a proper response step by step

11/ When user wants to know about a topic, try to give answer with proper examples and references.

This is the previous chat history of the user:
{history}

Below is a message I received from the user:
{message}

Here is a list of documents that is similar to user's question:
{documents}

Please write the best response that will impress the user to work with the company:
"""

template_for_file = """
You are a document reader chatbot 
I will share a user's message and previous chat history with you and you will give me the best answer based on past best practies, 
and you will follow ALL of the rules below:

1/ Response should be very similar or even identical to the past best practies, 
in terms of length, ton of voice, logical arguments and other details

2/ If the best practice are irrelevant, then try to mimic the style of the best practice to user's message

3/ Don't hallucinate if don't understand any topic or if you don't have any data on a topic, at that time just admit you don't know the answer.

4/ Keep the response short and concise

5/ Include important informations in a structured way

6/ Format the response with newlines and bullet points to if necessary

7/ Behave politely and professionally in your response

8/ Perform basic arithmetic operations with step by step explanations

9/ If needed break down the answer to give a proper response step by step

10/ When user wants to know about a topic, try to give answer with proper examples and references.

This is the previous chat history of the user:
{history}

Below is a message I received from the user:
{message}

Here is a list of documents that is similar to user's question:
{documents}

Please write the best relevant response to send to the user:
"""

prompt = PromptTemplate(
    input_variables=["history", "message", "documents"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)

prompt_for_file = PromptTemplate(
    input_variables=["history", "message", "documents"],
    template=template_for_file
)

chain_for_file = LLMChain(llm=llm, prompt=prompt_for_file)


def generate_response(message, token):
    documents = embedding.retrieve_info(message)
    response = chain.run(message=message, documents=documents, history=token)
    # local_logger.info(response)
    try:
        # chat_logger.log_db(best_practice)
        chat_logger.log_message(message, response, documents, token)
    except Exception as e:
        print("Error logging message:", e)
    return response

def generate_response_from_file(db, query, token):
    documents = embedding.retrieve_info_from_file(db, query)
    response = chain_for_file.run(message=query, documents=documents, history=token)
    # chat_logger.log_db(best_practice)
    chat_logger.log_message(query, response, documents, token)
    return response