from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix="/user", tags=["user"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/")
async def all_users(db: DbSession):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id")
async def user_by_id(db: DbSession, user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail='User was not found')


@router.get("/user_id/tasks")
async def tasks_by_user_id(db: DbSession, user_id: int):
    task = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not have such tasks")
    else:
        return task


@router.post("/create")
async def create_user(db: DbSession, create_u: CreateUser):
    user = db.scalars(select(User).where(User.username == create_u.username)).first()
    if user:
        raise HTTPException(status_code=404, detail='The user exists')
    db.execute(insert(User).values(username=create_u.username,
                                   firstname=create_u.firstname,
                                   lastname=create_u.lastname,
                                   age=create_u.age,
                                   slug=slugify(create_u.username)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/update")
async def update_user(db: DbSession, user_id: int, update_u: UpdateUser):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')

    db.execute(update(User).where(User.id == user_id).values(firstname=update_u.firstname,
                                                             lastname=update_u.lastname,
                                                             age=update_u.age))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }


@router.delete("/delete")
async def delete_user(db: DbSession, user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')

    db.execute(delete(User).where(User.id == user_id))
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': "the user has been deleted"
    }
