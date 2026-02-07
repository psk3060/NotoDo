from pydantic import BaseModel

class Todo(BaseModel):
    id:int
    title: str
    status: str
    registDate:str
    deadline:str
    description: str

    def __init__(self, id, title, status, registDate, deadline, description) -> None:
        super().__init__(id = id, title = title, status = status, registDate = registDate, deadline = deadline, description = description)
        
        self.id = id
        self.title = title
        self.status = status
        self.registDate = registDate
        self.deadline = deadline
        self.description = description