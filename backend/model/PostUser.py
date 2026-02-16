from sqlalchemy import Column,  String
from db.postgre_engine import Base

class User(Base):
    __tablename__ = "users"

    userId = Column("user_id", String, primary_key=True)
    userName = Column("user_name", String, nullable=False)
    password = Column("password", String, unique=True)