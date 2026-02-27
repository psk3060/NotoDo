from abc import ABC, abstractmethod
from model.todo.todo_model import TodoComment
from model import Todo
from typing import List

class TodoService(ABC):
    @abstractmethod
    def read_todos(user_id : str) -> List[Todo]:
        pass

    @abstractmethod
    def read_todo_detail(todo_id: str, user_id : str):
        pass
        
    @abstractmethod
    def create_todo(todo : Todo, user_id : str):
        pass

    @abstractmethod
    def delete_todo(todo_id : str, user_id : str) :
        pass
    
    @abstractmethod
    def update_todo(todo_id : str, todo_update: Todo, user_id : str) :
        pass
    
    @abstractmethod
    def create_comment(comment : TodoComment) :
        pass