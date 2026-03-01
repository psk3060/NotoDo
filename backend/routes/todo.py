# backend/routes/todo.py
from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse

from model import Todo, TodoComment
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
async def read_todos(
                currentPage: int = Query(default=0),
                pageSize: int = Query(default=10),
                request: Request = None):
    
    return await todo_service.read_todos_with_paging(request.state.user, currentPage, pageSize)
    
    

@router.get("/create")
async def create_todo(_: Request):
    '''추가 버튼 클릭 시'''
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
async def update_todo(todo_id : str, todo_update: Todo, request: Request) :
    await todo_service.update_todo(todo_id, todo_update, request.state.user)
    
@router.post("/{todo_id}/comments")
async def create_todo_comment(todo_id : str, comment : TodoComment, request: Request) :
    comment.todoId = todo_id
    await todo_service.create_comment(comment)