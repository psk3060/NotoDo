from beanie import init_beanie, Document
from pymongo import AsyncMongoClient

class User(Document):
    userId : str
    userName : str
    password : str

    class Settings:
        name = "user"
    

def selectById(userId:str) -> User:
    findresult = User.find(userId)
    return findresult