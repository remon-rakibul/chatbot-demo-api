from sqlalchemy import Column, Integer, String
from db import Base

class Files(Base):
    __tablename__ = "files"

    id = Column (Integer, primary_key = True, index = True, autoincrement = True)
    name = Column(String)
    path = Column(String)
    size = Column(String)