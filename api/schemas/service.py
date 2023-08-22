from pydantic import BaseModel

class NewService(BaseModel):
    name: str
    description: str