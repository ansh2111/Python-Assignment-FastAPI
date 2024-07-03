from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, HttpUrl

class Product(BaseModel):
    name: str
    price: float
    image_path: str 

class ListQuery(BaseModel):
    pages: Optional[int] = 1
    proxy_url: Optional[str] = ""

class TaskResponse(BaseModel):
    task_uuid: UUID 

class ListResponse(BaseModel):
    status: str = "Success"
    count: int = 0
    data: Optional[List[Product]] = []
