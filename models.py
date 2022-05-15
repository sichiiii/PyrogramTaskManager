from sqlalchemy import Column, Integer, String
from database import Base, engine

class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    info = Column(String)
