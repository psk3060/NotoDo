from service.TodoService import TodoService
from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from typing import List

class NotionTodoServiceImpl(TodoService):
    
    # 모두 조회 TODO
    def read_todos(self) -> List[Todo]:
        pass

    # 상세 조회 TODO
    def read_todo_detail(self, todo_id: int) -> Todo: 
        pass

    # 작업 추가 TODO
    def create_todo(self, todo : Todo):
        pass
        
    # 작업 삭제 TODO
    def delete_todo(self, todo_id :int) :
        pass

    # 작업 수정 TODO
    def update_todo(self, todo_id : int, todo_update: TodoUpdate) :
        pass