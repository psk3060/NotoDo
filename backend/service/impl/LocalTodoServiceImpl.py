from service.TodoService import TodoService
from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from typing import List

class LocalTodoServiceImpl(TodoService):
    def __init__(self):
        self.todo_list = []
        self.todo_list.append(Todo(1, "Sample Todo", "Pending", "2025-02-06 17:30", "2025-02-10", "This is a sample"))
        self.todo_list.append(Todo(2, "Another Todo", "Pending", "2025-02-06 18:00", "2025-02-14", "This is another sample"))
        self.todo_list.append(Todo(3, "Yet Another Todo", "Pending", "2025-02-06 21:35", "2025-02-10", "This is yet another sample"))
        
    def read_todos(self) -> List[Todo]:
        return self.todo_list

    def read_todo_detail(self, todo_id: int) -> Todo: 
        return [x for x in self.todo_list if x.id == todo_id][0]
    
    def create_todo(self, todo : Todo):
        maxId = 0
    
        if len(self.todo_list) > 0:
            for x in self.todo_list:
                if x.id > maxId:
                    maxId = x.id
        
        maxId = maxId + 1
        todo.id = maxId
        self.todo_list.append(todo)    
        
    def delete_todo(self, todo_id :int) :
        self.todo_list.remove([x for x in self.todo_list if x.id == todo_id][0])

    def update_todo(self, todo_id : int, todo_update: TodoUpdate) :
        for index, todo in enumerate(self.todo_list):
            
            if todo.id == todo_id:
                # 기존 todo를 직접 수정 (순서 유지)
                updated_data = todo.dict()
            
                if todo_update.title is not None:
                    updated_data['title'] = todo_update.title
            
                if todo_update.status is not None:
                    updated_data['status'] = todo_update.status
                
                if todo_update.deadline is not None:
                    updated_data['deadline'] = todo_update.deadline
                
                if todo_update.description is not None:
                    updated_data['description'] = todo_update.description

                self.todo_list[index] = Todo(**updated_data)
    