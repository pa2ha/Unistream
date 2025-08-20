from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Tasks.router import task_router
from JWT.router import router as jwt_router
from Users.router import router as users_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(task_router, prefix="/api/tasks", tags=["Менеджер задач"])
app.include_router(jwt_router, prefix="/api/JWT", tags=["JWT"])
app.include_router(users_router, prefix="/api/users", tags=["Пользователи"])