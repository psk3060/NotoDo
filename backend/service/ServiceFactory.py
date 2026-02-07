from service.TodoService import TodoService
from service.impl.LocalTodoServiceImpl import LocalTodoServiceImpl

def get_todo_service(environment: str = "local") -> TodoService:
    if environment == "local":
        return LocalTodoServiceImpl()
    else:
        raise ValueError(f"Unknown environment: {environment}")