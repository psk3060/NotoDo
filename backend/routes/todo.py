# backend/routes/todo.py
from fastapi import APIRouter, Request

from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from service.ServiceFactory import get_todo_service
from service.impl import AuthServiceImpl

import os, json

# .env 파일 로드
router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

# 환경변수 읽기
ENVIRONMENT = os.getenv("TODO_ENV", "local")
todo_service = get_todo_service(ENVIRONMENT)

@router.get("")
def read_todos(request: Request):
    # Request Header 
    authService = AuthServiceImpl()
    
    user_id = request.headers.get("userId")
    
    access_token = request.cookies.get("access_token")
    
    # 1. Token 검증(만료, 유효성, 기타 에러만 검증)
    json_data = json.loads(authService.decodeToken(access_token))
    
    token_type = json_data["type"]
    
    if token_type != "access":
        raise Exception(json_data)
    
    token_user_id = json_data["user_id"]
    
    # 2. Token의 userId와 Header의 userId 비교 : 일치할 경우, 정상. 일치하지 않을 경우 블랙리스트 처리(TODO)
    if user_id != token_user_id:
        raise Exception("유효하지 않은 접근입니다[ID 불일치]")
    
    # Token Refresh 호출은 클라이언트에 일임
    
    return todo_service.read_todos(user_id)

@router.get("/{todo_id}")
def read_todo_detail(todo_id: int, request: Request):
    return todo_service.read_todo_detail(todo_id)
    
@router.post("")
def create_todo(todo : Todo, request: Request):
    todo_service.create_todo(todo) 
    return True

@router.delete("/{todo_id}")
def delete_todo(todo_id : int, request: Request) :
    todo_service.delete_todo(todo_id)
    
@router.put("/{todo_id}")
def update_todo(todo_id : int, todo_update: TodoUpdate, request: Request) :
    user_id = request.headers.get("userId")
    
    todo_update.userId = user_id
    
    todo_service.update_todo(todo_id, todo_update)