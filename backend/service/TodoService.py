from abc import ABC, abstractmethod
from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from typing import List

class TodoService(ABC):
    @abstractmethod
    def read_todos(user_id : str) -> List[Todo]:
        pass

    @abstractmethod
    def read_todo_detail(todo_id: int, user_id : str):
        pass
        
    @abstractmethod
    def create_todo(todo : Todo, user_id : str):
        pass

    @abstractmethod
    def delete_todo(todo_id : int, user_id : str) :
        pass
    
    @abstractmethod
    def update_todo(todo_id : int, todo_update: TodoUpdate, user_id : str) :
        pass