from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import Docx2txtLoader
from fastapi import FastAPI, File, UploadFile, Form, WebSocket, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
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
from fastapi.responses import JSONResponse, FileResponse
from hurry.filesize import size
# from bson.objectid import ObjectId 
# from bson.json_util import dumps
# from fastapi.responses import JSONResponse, FileResponse
# from pymongo import MongoClient
import io
from db import SessionLocal
from db import engine
from models import Base
import models as model
Base.metadata.create_all(bind=engine)
# import tempfile




class Chat(BaseModel):
    query: str
    token: str | None = None

app = FastAPI()

# client = MongoClient("mongodb://5.189.160.223:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.9.1")
# client = MongoClient("mongodb://arisaftech:AST@#4321@arisaftech.ru6oaja.mongodb.net/", server_api=ServerApi('1'))
# mongo_uri = "mongodb://arisaftech:" + urllib.parse.quote("AST@#4321") + "@127.0.0.1:27017/"
# client = MongoClient(mongo_uri)
# uri = "mongodb+srv://arisaftech:AST@#4321@arisaftech.ru6oaja.mongodb.net/?retryWrites=true&w=majority"
# client = MongoClient(uri, server_api=ServerApi('1'))


# db = client("file_storage") 

# db = client.file_storage
# file_collection = db["files"]

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
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
app.ast = True
app.db = None

@app.get("/health")
async def health():
    return {"Message": "Up and Running"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    # print("Here")
    # current_datetime = datetime.now()
    
    # formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    # content = await file.read()
    # file_data = {
    #     "name": file.filename,
    #     "content": content,
    #     "time": formatted_datetime
    # }

    # file_collection.insert_one(file_data)
    # # DIR = "temp"
    # if not os.path.exists("temp"):
    #     os.makedirs("temp")

    # print(file_data["time"])


    # with open(os.path.join("temp", file_data["time"]), "wb") as f:
    #     f.write(content)

    


    app.ast = False

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())
    # print(f"This is the filename: {file.filename}")
    if (file.filename.endswith(".pdf")):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        app.db = embedding.load_file_to_db(pages)

    elif (file.filename.endswith(".docx") or file.filename.endswith(".doc")):
        # print(f"this is the file_path: {file_path}")
        loader = Docx2txtLoader(file_path)
        # print("working fine....")
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

    try:
        print("Here")
        current_datetime = datetime.now()
        
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        content = await file.read()
        file_data = {
            "name": file.filename,
            "content": content,
            "time": formatted_datetime
        }

        # file_collection.insert_one(file_data)
        # DIR = "temp"
        if not os.path.exists("temp"):
            os.makedirs("temp")

        print(file_data["time"])


        with open(os.path.join("temp", file_data["time"]), "wb") as f:
            pass
            # f.write(content)
    except Exception as e:
        print(f"This is the Exception: {e}")
    
    return {"response": f"{file.filename} uploaded successfully"}


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         # Process the received data and generate a response
#         # You can call your chatbot logic here
#         response = prompt.generate_response(data)
#         await websocket.send_text(response)

@app.post("/chat")
async def chat(chat: Chat):
    if app.ast:
        response = prompt.generate_response(chat.query, chat.token).encode("utf-8")
        stream = io.BytesIO(response)
        # return {"response": response}
        return StreamingResponse(stream)
    else:
        response = prompt.generate_response_from_file(app.db, chat.query, chat.token).encode("utf-8")
        stream = io.BytesIO(response)
        return StreamingResponse(stream)
        # return {"response": response}


@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...), db: Session = Depends((get_db))):

    current_datetime = datetime.now()
    
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    content = await file.read()
    file_data = {
        "name": file.filename,
        "content": content,
        "time": formatted_datetime,
        "size": file.size
    }

    # file_collection.insert_one(file_data)
    # DIR = "temp"
    if not os.path.exists("temp"):
        os.makedirs("temp")

    print(file_data["time"])


    with open(os.path.join("temp", (file_data["time"] + file_data["name"]) ) , "wb") as f:
        f.write(content)
        file_dict = {
            "name": formatted_datetime + file_data["name"] ,
            "path": os.path.join("temp/" + formatted_datetime + file_data["name"]),
            "size": size(file_data["size"])
        }
        file_item = model.Files(**file_dict)
        print(file_item)
        try:
            db.add(file_item)
            db.commit()
        except:
            return {"Message": "Something went wrong with the db"}
              

    return {"Message": "File upload successful"}


@app.get("/all")
async def get_files(db: Session = Depends((get_db))):
    try:
        files = db.query(model.Files).all()
        db.close()
        return files
    except: 
       return {"Message": "Something went wrong"}

@app.get("/download/{file_id}")
async def download_file(file_id: int, db: Session = Depends((get_db))):
    
    file_data =  db.query(model.Files).filter(model.Files.id == file_id).first()

    if not file_data:
        return JSONResponse(content={"message": "File not found"}, status_code=404)
    
    return FileResponse(file_data.path, media_type='application/octet-stream',filename=file_data.name, status_code = 200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)