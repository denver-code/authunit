from pydantic import BaseModel


class AuthUser(BaseModel):
    email: str
    password: str


class ServiceAuthUser(BaseModel):
    email: str
    password: str
    service_token: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
