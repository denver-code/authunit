from datetime import datetime
from beanie import Document
from pydantic import BaseModel

class ServiceModel(Document):
    name: str
    description: str
    access_code: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "services"