from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import Docx2txtLoader
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from pydantic import BaseModel
from typing import Annotated
import embedding
import tempfile
import uvicorn
import prompt
import os


class Prompt(BaseModel):
    prompt: str

app = FastAPI()

# origins = [
#     "http://localhost:8000",
#     "http://5.189.160.223:8054",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.ast = True
app.db = None

@app.get("/health")
async def health():
    return {"Message": "Up and Running"}


@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()]):
    app.ast = False
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    if (file.filename.endswith(".pdf")):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        app.db = embedding.load_file_to_db(pages)

    elif (file.filename.endswith(".docx") or file.filename.endswith(".doc")):
        loader = Docx2txtLoader(file_path)
        data = loader.load()
        app.db = embedding.load_file_to_db(data)

    elif (file.filename.endswith(".ppt") or file.filename.endswith(".pptx")):
        loader = UnstructuredPowerPointLoader(file_path)
        data = loader.load()
        app.db = embedding.load_file_to_db(data)

    elif (file.filename.endswith(".txt")):
        loader = TextLoader(file_path)
        data = loader.load()
        app.db = embedding.load_file_to_db(data)

    return {"response": f"{file.filename} uploaded successfully"}


@app.post("/chat")
async def chat(query: Annotated[str, Form()]):
    if app.ast:
        response = prompt.generate_response(query)
        return {"response": response}
    else:
        response = prompt.generate_response_from_file(app.db, query)
        return {"response": response}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)