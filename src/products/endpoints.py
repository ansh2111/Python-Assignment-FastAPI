from fastapi import APIRouter, Depends, BackgroundTasks
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from src.products.scraper import get_products, get_task
from src.products.schemas import ListQuery, ListResponse, TaskResponse
from src.db import crud, models, schemas
from src.db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/list/", response_model=TaskResponse)
async def list(data: ListQuery, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_uuid = uuid4()
    background_tasks.add_task(get_products, data=data, db=db, task_uuid=task_uuid)
    return TaskResponse(task_uuid=task_uuid)

@router.get("/tasks/{task_uuid}", response_model=ListResponse)
def get_task_info(task_uuid: UUID, db: Session = Depends(get_db)):
    data = get_task(db=db, task_uuid=task_uuid)
    if data == None:
        return ListResponse(status="No such task")
    return ListResponse(status=data.status, count=data.result_count or 0)