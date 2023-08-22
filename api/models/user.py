from datetime import datetime
from beanie import Document
from pydantic import BaseModel

class UserModel(Document):
    email: str
    password: str

    class Settings:
        name = "users"