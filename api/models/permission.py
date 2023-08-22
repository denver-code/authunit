from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

class PermissionModel(Document):
    user_id: PydanticObjectId
    service: str
    value: str
    created_at: datetime = datetime.now()

    class Settings:
        name = "permissions"

        unique_together = ("user_id", "service", "value")

