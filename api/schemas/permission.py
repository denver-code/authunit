from pydantic import BaseModel


class NewPermission(BaseModel):
    user_id: str
    service: str
    value: str


class BulkPromote(BaseModel):
    user_id: str
    service: str
    values: list[str]
