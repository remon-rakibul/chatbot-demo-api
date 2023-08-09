from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import embedding

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

4/ Don't make up information. If you don't know something, admit you don't know

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
    best_practice = embedding.retrieve_info(message)
    response = chain.run(message=message, best_practice=best_practice)
    return response


def generate_response_from_pdf_file(text, message):
    best_practice = embedding.retrieve_info_from_pdf_file(text, message)
    response = chain.run(message=message, best_practice=best_practice)
    return response


# query = input("enter your message: ")
# print(f'Response: {generate_response(query)}')
