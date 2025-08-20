# users_router.py
from fastapi import APIRouter, Response, HTTPException, status, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from database import async_session_factory
import bcrypt
import jwt
import pytz
from config import settings
from datetime import datetime, timedelta
from aioredis import from_url
from fastapi.responses import JSONResponse
from Users.schemas import UsersAdd
from Users.models import Users


router = APIRouter()

redis = from_url(settings.CELERY_BROKER_URL, decode_responses=True)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_DAYS = settings.ACCESS_TOKEN_EXPIRE_DAYS
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

http_bearer = HTTPBearer()


async def get_user(username: str):
    async with async_session_factory() as session:
        stmt = select(Users).where(Users.username == username)
        result = await session.execute(stmt)
        return result.scalars().first()


async def add_tokens_to_blacklist(access_token: str, refresh_token: str):
    await redis.setex(f"blacklist:{refresh_token}", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "1")
    await redis.setex(f"blacklist:{access_token}", timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS), "1")


async def check_access_token(creds):
    access_token = creds

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found in authorization header"
        )

    blacklist_token = await redis.get(f"blacklist:{access_token}")
    if blacklist_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is blacklisted"
        )

    payload = await verify_token(access_token)
    if not payload["username"] or not payload['id'] or not payload['exp']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not belong to the correct user"
        )

    return payload


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    expire = datetime.now(pytz.UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    expire = datetime.now(pytz.UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token", summary='Получение токена')
async def login_for_access_token(user: UsersAdd, response: Response):
    user_data = await get_user(user.username)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нет пользователя с такими данными",
            headers={"WWW-Authenticate": "Bearer"})

    if not bcrypt.checkpw(user.password.encode('utf-8'), user_data.hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"})

    user_info = {
        "username": user_data.username,
        "id": user_data.id
    }

    access_token = await create_access_token(data=user_info)
    refresh_token = await create_refresh_token(data=user_info)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=3600 * 24 * 2,
        expires=3600 * 24 * 2,
    )

    return {"access_token": access_token}


@router.post("/refresh-token", summary="Обновление токенов")
async def refresh_tokens(request: Request, response: Response, access_token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies"
        )
    payload = await verify_token(refresh_token)
    refresh_token_blacklist = await redis.get(f"blacklist:{refresh_token}")
    if refresh_token_blacklist or not await verify_token(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or blacklisted refresh token"
        )

    await check_access_token(access_token.credentials)

    user_info = {
        "username": payload["username"],
        "id": payload["id"]
    }

    await add_tokens_to_blacklist(access_token.credentials, refresh_token)

    access_token = await create_access_token(data=user_info)
    refresh_token = await create_refresh_token(data=user_info)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=3600 * 24 * 2,
        expires=3600 * 24 * 2,
    )

    return {"access_token": access_token}


@router.post("/logout")
async def logout(request: Request, access_token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    access_token = access_token.credentials
    await check_access_token(access_token)
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies"
        )

    await add_tokens_to_blacklist(access_token, refresh_token)

    return JSONResponse(content={"msg": "Успешный логаут"}, status_code=status.HTTP_200_OK)
