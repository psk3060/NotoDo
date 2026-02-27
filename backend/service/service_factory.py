from service.todo_service import TodoService
from service import ProdTodoServiceImpl, get_notion_service, LocalTodoServiceImpl

def get_todo_service(environment: str = "local") -> TodoService:
    if environment == "local":
        return LocalTodoServiceImpl()
    elif environment == "prod":
        notion_service = get_notion_service()
        return ProdTodoServiceImpl(notion_service)
    else:
        raise ValueError(f"Unknown environment: {environment}")