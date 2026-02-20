# backend/routes/todo.py
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from model import Todo
from model import TodoUpdate
from service.service_factory import get_todo_service


import os

# .env 파일 로드
router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

# 환경변수 읽기
ENVIRONMENT = os.getenv("TODO_ENV", "local")
todo_service = get_todo_service(ENVIRONMENT)

@router.get("")
async def read_todos(request: Request):
    return await todo_service.read_todos(request.state.user)

@router.get("/create")
async def create_todo(request: Request):
    return None

@router.get("/{todo_id}")
async def read_todo_detail(todo_id: str, request: Request):
    todo = await todo_service.read_todo_detail(todo_id, request.state.user)

    if todo is None:
        return RedirectResponse("/todo/create", 307)

    return todo
    
@router.post("")
async def create_todo(todo : Todo, request: Request):
    await todo_service.create_todo(todo, request.state.user) 

@router.delete("/{todo_id}")
async def delete_todo(todo_id : str, request: Request) :
    await todo_service.delete_todo(todo_id, request.state.user)
    
@router.put("/{todo_id}")
async def update_todo(todo_id : str, todo_update: TodoUpdate, request: Request) :
    await todo_service.update_todo(todo_id, todo_update, request.state.user)