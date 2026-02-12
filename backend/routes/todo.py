# backend/routes/todo.py
from fastapi import APIRouter

from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from service.ServiceFactory import get_todo_service

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
def read_todos():
    return todo_service.read_todos()

@router.get("/{todo_id}")
def read_todo_detail(todo_id: int):
    return todo_service.read_todo_detail(todo_id)
    
@router.post("")
def create_todo(todo : Todo):
    todo_service.create_todo(todo) 
    return True

@router.delete("/{todo_id}")
def delete_todo(todo_id : int) :
    todo_service.delete_todo(todo_id)
    
@router.put("/{todo_id}")
def update_todo(todo_id : int, todo_update: TodoUpdate) :
    todo_service.update_todo(todo_id, todo_update)