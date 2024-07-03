from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Products(Base):
    __tablename__ = "products"
    __allow_unmapped__ = True

    pid = Column(String, primary_key=True)
    title = Column(String)
    image_path = Column(String)
    price = Column(Float)

class Tasks(Base):
    __tablename__ = "tasks"
    __allow_unmapped__ = True

    task_uuid = Column(UUID, primary_key=True)
    status = Column(String)
    result_count = Column(Integer)