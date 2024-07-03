from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from . import models, schemas

def get_product(db: Session, product_id: int):
    return db.query(models.Products).filter(models.Products.pid == product_id).first()

def create_product(db: Session, product: schemas.ProductDetails):
    prd = models.Products(pid=product.pid, title=product.title,
     image_path=product.image_path_local, price=product.price)
    db.add(prd)
    db.commit()
    db.refresh(prd)
    return prd

def update_product(db: Session, product_id: int, product: schemas.ProductDetails):
    prd = get_product(product_id)
    prd.title = product.title 
    prd.image_path = product.image_path
    prd.price = product.price 
    db.commit()
    db.refresh(prd)
    return prd

def create_task(db: Session, task_uuid: UUID):
    task = models.Tasks(task_uuid=task_uuid, status="Pending")
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task(db: Session, task_uuid: UUID):
    return db.query(models.Tasks).filter(models.Tasks.task_uuid == task_uuid).first()

def update_task(db: Session, task_uuid:UUID, task: schemas.TaskDetails):
    task_db = get_task(db, task_uuid) 
    task_db.status=task.status
    task_db.result_count=task.result_count
    db.commit()
    db.refresh(task_db)
    return task_db