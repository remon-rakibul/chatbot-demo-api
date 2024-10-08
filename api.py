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
from pathlib import Path
from datetime import datetime
from bson.objectid import ObjectId 
from bson.json_util import dumps
from fastapi.responses import JSONResponse, FileResponse
from pymongo import MongoClient
import tempfile


class Prompt(BaseModel):
    prompt: str

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
# db = client("file_storage") 
db = client.file_storage
file_collection = db["files"]

class FileUpload(BaseModel):
    name: str
    content: bytes
    time: str

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


@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):

    current_datetime = datetime.now()
    
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    content = await file.read()
    file_data = {
        "name": file.filename,
        "content": content,
        "time": formatted_datetime
    }

    file_collection.insert_one(file_data)
    # DIR = "temp"
    if not os.path.exists("temp"):
        os.makedirs("temp")

    print(file_data["time"])


    with open(os.path.join("temp", file_data["time"]), "wb") as f:
        f.write(content)

    return {"Message": "File upload successful"}


@app.get("/all")
async def get_files():
    files = list (file_collection.find())
    serialized_files = dumps(files)
    return JSONResponse(content=serialized_files)

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    
    file_data = file_collection.find_one({"_id": ObjectId(file_id)})

    if not file_data:
        return JSONResponse(content={"message": "File not found"}, status_code=404)
    
    file_content = file_data["content"]
    file_name = file_data["name"] 
    file_time = file_data["time"]

    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    file_path = Path("temp") / file_time
    print(file_path)
    # return FileResponse(file_path, file_name)
    return FileResponse(file_path, media_type='application/octet-stream',filename=file_name)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)