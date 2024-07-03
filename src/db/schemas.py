from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, HttpUrl

class ProductDetails(BaseModel):
    pid: str
    title: str 
    image_url: str
    price: float
    image_path_local: Optional[str] = ""

    class Config:
        orm_mode = True

class TaskDetails(BaseModel):
    task_uuid: UUID
    status: str = "Pending"
    result_count: int = 0

    class Config:
        orm_mode = True