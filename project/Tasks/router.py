from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_factory
from typing import List, Annotated
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from JWT.router import check_access_token

from . import schemas, models

http_bearer = HTTPBearer()


async def get_session_local():
    async with async_session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session_local)]


async def check_token(creds: HTTPAuthorizationCredentials = Depends(http_bearer)):
    token = creds.credentials
    if not await check_access_token(token):
        raise HTTPException(status_code=403, detail="Invalid or expired token")

task_router = APIRouter()

# Можно раскоментировать следующую строчку и получить защиту по JWT на урлах. (Тесты отвалятся)
# task_router = APIRouter(dependencies=[Depends(check_token)],)


@task_router.get("/", response_model=List[schemas.TaskOut])
async def get_tasks(db: SessionDep):
    result = await db.execute(select(models.Task))
    tasks = result.scalars().all()
    return tasks


@task_router.get("/{task_id}", response_model=schemas.TaskOut)
async def get_task(task_id: str, db: SessionDep):
    result = await db.execute(select(models.Task).where(models.Task.uuid == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@task_router.post("/", response_model=schemas.TaskOut)
async def create_task(task: schemas.TaskCreate, db: SessionDep):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


@task_router.put("/{task_id}", response_model=schemas.TaskOut)
async def update_task(task_id: str, task_update: schemas.TaskUpdate, db: SessionDep):
    result = await db.execute(select(models.Task).where(models.Task.uuid == task_id))
    db_task = result.scalar_one_or_none()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    await db.commit()
    await db.refresh(db_task)
    return db_task


@task_router.delete("/{task_id}")
async def delete_task(task_id: str, db: SessionDep):
    result = await db.execute(select(models.Task).where(models.Task.uuid == task_id))
    db_task = result.scalar_one_or_none()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(db_task)
    await db.commit()
    return {"message": "Task deleted successfully"}


@task_router.delete("all", summary="Удалить ВСЕ задачи")
async def delete_task_all(db: SessionDep):
    result = await db.execute(select(models.Task))
    db_task = result.scalars().all()
    if not db_task:
        return {"message": "Tasks deleted successfully"}
    for i in db_task:
        await db.delete(i)
    await db.commit()
    return {"message": "Tasks deleted successfully"}
