from abc import ABC, abstractmethod
from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from typing import List

class TodoService(ABC):
    @abstractmethod
    def read_todos() -> List[Todo]:
        pass

    @abstractmethod
    def read_todo_detail(todo_id: int):
        pass
        
    @abstractmethod
    def create_todo(todo : Todo):
        pass

    @abstractmethod
    def delete_todo(todo_id : int) :
        pass
    
    @abstractmethod
    def update_todo(todo_id : int, todo_update: TodoUpdate) :
        pass