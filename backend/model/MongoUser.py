from beanie import Document

class User(Document):
    userId : str
    userName : str
    password : str

    class Settings:
        name = "user"
    

def selectById(userId:str) -> User:
    findresult = User.find(userId)
    return findresult