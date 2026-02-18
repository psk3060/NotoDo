from beanie import Document

class MongoUser(Document):
    userId : str
    userName : str
    password : str

    class Settings:
        name = "users"
    

def selectById(userId:str) -> MongoUser:
    findresult = MongoUser.find(userId)
    return findresult