from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
# from dotenv import load_dotenv
# load_dotenv()

# db_user = os.getenv("db_user")
# db_pass = os.getenv("db_pass")
DATABASE_URL = "postgresql://postgres:1234@localhost/chatbot"  

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()