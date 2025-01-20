from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix="/task", tags=["task"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/")
async def all_tasks(db: DbSession):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get("/task_id")
async def task_by_id(db: DbSession, task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if task:
        return task
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")


@router.post("/create")
async def create_task(db: DbSession, create_t: CreateTask, user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user was not found')

    db.execute(insert(Task).values(title=create_t.title,
                                   content=create_t.content,
                                   priority=create_t.priority,
                                   user_id=user_id,
                                   slug=slugify(create_t.title)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/update")
async def update_task(db: DbSession, task_id: int, update_t: UpdateTask):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    db.execute(update(Task).where(Task.id == task_id).values(title=update_t.title,
                                                             content=update_t.content,
                                                             priority=update_t.priority))
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'The task has been updated!'
    }


@router.delete("/delete")
async def delete_task(db: DbSession, task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': "task deleted"
    }
