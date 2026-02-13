from service.TodoService import TodoService
from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from typing import List

class LocalTodoServiceImpl(TodoService):
    def __init__(self):
        self.todo_list = []
        self.todo_list.append(Todo(id = 1, title = "Sample Todo", status = "Pending", registDate = "2025-02-06 17:30", deadline = "2025-02-10", description = "This is a sample", userId = "demo"))
        self.todo_list.append(Todo(id = 2, title = "Another Todo", status = "Pending", registDate = "2025-02-06 18:00", deadline = "2025-02-14", description = "This is another sample", userId = "demo"))
        self.todo_list.append(Todo(id = 3, title = "Yet Another Todo", status = "Pending", registDate = "2025-02-06 21:35", deadline = "2025-02-10", description = "This is yet another sample", userId = "demo"))
        
    def read_todos(self, user_id : str) -> List[Todo]:
        return [x for x in self.todo_list if x.userId == user_id]

    def read_todo_detail(self, todo_id: int, user_id : str) -> Todo: 
        return [x for x in self.todo_list if x.id == todo_id and x.userId == user_id][0]
    
    def create_todo(self, todo : Todo, user_id:str):
        maxId = 0

        todo.userId = user_id
        
        if len(self.todo_list) > 0:
            for x in self.todo_list:
                if x.id > maxId:
                    maxId = x.id
        
        maxId = maxId + 1
        todo.id = maxId
        self.todo_list.append(todo)    
        
    def delete_todo(self, todo_id :int, user_id : str) :
        self.todo_list.remove([x for x in self.todo_list if x.id == todo_id and x.userId == user_id][0])

    def update_todo(self, todo_id : int, todo_update: TodoUpdate, user_id:str) :
        
        todo_update.userId = user_id
        
        for index, todo in enumerate(self.todo_list):
            
            if todo.id == todo_id and todo.userId == todo_update.userId:
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