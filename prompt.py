from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from logger_config import setup_chat_logger
from langchain.chains import LLMChain
import embedding

local_logger = setup_chat_logger(__name__)

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

with open('api.log', 'r') as f:
    context = f.read()
    words = context[-1600:].split()
    tokens = ' '.join(words[-200:])
    # print(tokens)


template = """
You are a world class representative chatbot of AriSaf Tech Ltd. 
you will share a user's message with you and you will give me the best answer based on past best practies, 
and you will follow ALL of the rules below:

1/ Response should be very similar or even identical to the past best practies, 
in terms of length, ton of voice, logical arguments and other details

2/ If the best practice are irrelevant, then try to mimic the style of the best practice to user's message

3/ Avoid any html tags and newline character like '/n' in your response. Response should only be in text

4/ Don't make up information. If you don't know something, admit you don't know

It was previous conversation:
{tokens}

Below is a message I received from the user:
{message}

Here is a list of best practies of how we normally respond to user in similar scenarios:
{best_practice}

Please write the best response that will impress the user to work with the company:
"""

template_for_file = """
You are a document reader chatbot 
you will share a user's message with you and you will give me the best answer based on past best practies, 
and you will follow ALL of the rules below:

1/ Response should be very similar or even identical to the past best practies, 
in terms of length, ton of voice, logical arguments and other details

2/ If the best practice are irrelevant, then try to mimic the style of the best practice to user's message

3/ If needed break down the answer to give a proper response step by step

4/ When user wants to know more about a topic then don't give the same answer, try to give different answer with proper examples and if any reference need then try to add that reference.

5/ Avoid any types of special characters like '/n' in your response. Response should only be in text

6/ Don't hallucinate if don't understand any topic or if you don't have any data on a topic, at that time just admit you don't know the answer.


Below is a message I received from the user:
{message}

Here is a list of best practies of how we normally respond to user in similar scenarios:
{best_practice}

Please write the best relevant response to send to the user:
"""

prompt = PromptTemplate(
    input_variables=["tokens", "message", "best_practice"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)

prompt_for_file = PromptTemplate(
    input_variables=["message", "best_practice"],
    template=template_for_file
)

chain_for_file = LLMChain(llm=llm, prompt=prompt_for_file)


def generate_response(message):
    best_practice = embedding.retrieve_info(message)
    response = chain.run(tokens=tokens, message=message, best_practice=best_practice)
    local_logger.info(response)
    return response

def generate_response_from_file(db, query):
    best_practice = embedding.retrieve_info_from_file(db, query)
    response = chain_for_file.run(message=query, best_practice=best_practice)
    return response