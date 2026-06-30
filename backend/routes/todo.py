import os

from repository import TodoBaseRepository, OutboxDocumentRepository, ConditionBaseRepository

from service import SearchConditionService, SearchConditionClientServiceImpl
from service import get_notion_service
from service import OutboxRegistServiceImpl

from db.postgres.client_config import get_pg_session

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse

from service import TodoService, LocalTodoServiceImpl, NotionTodoServiceImpl, DbTodoServiceImpl, HybridTodoServiceImpl

from model import Todo, TodoComment, TodoListRequest

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

def get_condition_service (
    session : AsyncSession = Depends(get_pg_session)    
) -> SearchConditionService: 
    return SearchConditionClientServiceImpl(ConditionBaseRepository(session), OutboxRegistServiceImpl(OutboxDocumentRepository))

def get_outbox_service() -> OutboxRegistServiceImpl :
    return OutboxRegistServiceImpl(OutboxDocumentRepository)

# 환경변수 읽기
def get_todo_service(
    session : AsyncSession = Depends(get_pg_session)    
) -> TodoService:
    
    ENVIRONMENT = os.getenv("TODO_ENV", "local")
    
    if ENVIRONMENT == "local":
        return LocalTodoServiceImpl()
    elif ENVIRONMENT == "prod":
        return HybridTodoServiceImpl(
            notion_service = get_notion_service()
            , todo_repository=TodoBaseRepository(session)
            , outbox_service = get_outbox_service()
            , condition_service=get_condition_service(session)
        )
    elif ENVIRONMENT == "db_prod":
        return DbTodoServiceImpl(TodoBaseRepository(session))
    elif ENVIRONMENT == "notion_prod":
        return NotionTodoServiceImpl(get_notion_service())
    else :
        raise ValueError(f"Unknown environment: {ENVIRONMENT}")
    

@router.get("")
async def read_todos(
                currentPage: int = Query(default=0),
                pageSize: int = Query(default=10),
                title : str = Query(default = ""),
                priority : str = Query(default = ""),
                status : str = Query(default = ""),
                request: Request = None,
                todo_service : TodoService = Depends(get_todo_service)):
    
        return await todo_service.read_todos(
            TodoListRequest(currentPage=currentPage, pageSize=pageSize, userId = request.state.user, title = title, priority=priority, status = status, isPaging=True)
        )
    

@router.get("/create")
async def create_todo(_: Request):
    '''추가 버튼 클릭 시'''
    return None

@router.get("/{todo_id}")
async def read_todo_detail(todo_id: str, request: Request, todo_service : TodoService = Depends(get_todo_service)):
    
    todo = await todo_service.read_todo_detail(todo_id, request.state.user)

    if todo is None:
        return RedirectResponse("/todo/create", 307)

    return todo
    
@router.post("")
async def create_todo(todo : Todo, request: Request, todo_service : TodoService = Depends(get_todo_service)):
    todo.userId = request.state.user
    
    await todo_service.create_todo(todo, request.cookies.get("access_token")) 

@router.delete("/{todo_id}")
async def delete_todo(todo_id : str, request: Request, todo_service : TodoService = Depends(get_todo_service)) :
    await todo_service.delete_todo(todo_id, request.state.user, request.cookies.get("access_token"))
    
@router.put("/{todo_id}")
async def update_todo(todo_id : str, todo_update: Todo, request: Request, todo_service : TodoService = Depends(get_todo_service)) :
    todo_update.userId = request.state.user
    await todo_service.update_todo(todo_id, todo_update, request.cookies.get("access_token"))
    
@router.post("/{todo_id}/comments")
async def create_todo_comment(todo_id : str, comment : TodoComment, request: Request, todo_service : TodoService = Depends(get_todo_service)) :
    comment.todoId = todo_id
    await todo_service.create_comment(comment, request.cookies.get("access_token"))
    

