from service.TodoService import TodoService
from service.impl.local_todo_service_impl import LocalTodoServiceImpl
from service.impl.notion_todo_service_impl import NotionTodoServiceImpl

def get_todo_service(environment: str = "local") -> TodoService:
    if environment == "local":
        return LocalTodoServiceImpl()
    elif environment == "op":
        return NotionTodoServiceImpl()
    else:
        raise ValueError(f"Unknown environment: {environment}")