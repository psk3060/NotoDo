from beanie import init_beanie, Document
from pymongo import AsyncMongoClient

class User(Document):
    userId : str
    userName : str
    password : str

    class Settings:
        name = "user"
    
# async def save(userId : str, userName : str, password : str):
#    user = User(userId = userId, userName = userName, password = password)
#    await User.insert_one(user)
    
def selectById(userId:str) -> User:
    findresult = User.find(userId)
    return findresult