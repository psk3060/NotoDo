from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Todo import Todo
import logging

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,         # Allow cookies to be sent cross-origin
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],            # Allow all headers
)

todo_list = []

todo_list.append(Todo(1, "Sample Todo", "Pending", "2025-02-06 17:30", "2025-02-10", "This is a sample"))
todo_list.append(Todo(2, "Another Todo", "Pending", "2025-02-06 18:00", "2025-02-14", "This is another sample"))
todo_list.append(Todo(3, "Yet Another Todo", "Pending", "2025-02-06 21:35", "2025-02-10", "This is yet another sample"))

@app.get("/todos")
def read_todos():
    return todo_list

@app.get("/todos/{todo_id}")
def read_todo_detail(todo_id: int):
    return [x for x in todo_list if x.id == todo_id][0]

@app.post("/todos")
def create_todo(todo : Todo):
    
    maxId = 0
    
    if len(todo_list) > 0:
        for x in todo_list:
            if x.id > maxId:
                maxId = x.id
    
    maxId = maxId + 1
    todo.id = maxId
    todo_list.append(todo)    
    return True

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id : int) :
    todo_list.remove([x for x in todo_list if x.id == todo_id][0])
    
    