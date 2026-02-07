from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.Todo import Todo
from model.TodoUpdate import TodoUpdate
from service.ServiceFactory import get_todo_service

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

ENVIRONMENT = "local"  # "local" 또는 "dev"
todo_service = get_todo_service(ENVIRONMENT)

@app.get("/todos")
def read_todos():
    return todo_service.read_todos()

@app.get("/todos/{todo_id}")
def read_todo_detail(todo_id: int):
    return todo_service.read_todo_detail(todo_id)
    
@app.post("/todos")
def create_todo(todo : Todo):
    todo_service.create_todo(todo) 
    return True

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id : int) :
    todo_service.delete_todo(todo_id)
    
@app.put("/todos/{todo_id}")
def update_todo(todo_id : int, todo_update: TodoUpdate) :
    todo_service.update_todo(todo_id, todo_update)