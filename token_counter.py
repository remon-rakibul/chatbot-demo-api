import tiktoken

def count_tokens(text: str):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-16k-0613")
    num_tokens = len(encoding.encode(text))
    return num_tokens