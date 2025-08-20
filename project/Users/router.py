# users_router.py
from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .schemas import UsersAdd, UsersGet
from .models import Users
from sqlalchemy import select
from database import async_session_factory
import bcrypt
from JWT.router import check_access_token


router = APIRouter()


http_bearer = HTTPBearer()


async def get_user(username: str):
    async with async_session_factory() as session:
        stmt = select(Users).where(Users.username == username)
        result = await session.execute(stmt)
        return result.scalars().first()


async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


@router.post("/register", summary='Регистрация пользователя')
async def register_user(user: UsersAdd, response: Response):
    async with async_session_factory() as session:
        result = await session.execute(select(Users).filter(Users.username == user.username))
        db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    hashed_password = await hash_password(user.password)

    new_user = Users(username=user.username, hashed_password=hashed_password)

    async with async_session_factory() as session:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

    pydant_return = UsersGet.model_validate(new_user, from_attributes=True)

    return pydant_return

