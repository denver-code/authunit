from fastapi import APIRouter, HTTPException

from api.schemas.user import AuthUser
from api.models.user import UserModel
from app.core.password import hash_password
from app.core.email_fixer import EmailFixer
from app.core.fastjwt import FastJWT

auth_router = APIRouter()


@auth_router.post("/signup")
async def signup(payload: AuthUser):
    payload.email = EmailFixer.fix(payload.email)
    payload.password = hash_password(payload.password)

    if await UserModel.find(UserModel.email == payload.email).count() > 0:
        raise HTTPException(status_code=400, detail="Email already registered")

    await UserModel(
        email=payload.email,
        password=payload.password,
    ).save()

    return {"message": "User created"}


@auth_router.post("/signin")
async def signin(payload: AuthUser):
    payload.email = EmailFixer.fix(payload.email)
    payload.password = hash_password(payload.password)

    user = await UserModel.find_one(
        UserModel.email == payload.email,
        UserModel.password == payload.password,
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials or user not exist")

    jwt_token = await FastJWT().encode({"user_id": str(user.id), "email": user.email})

    return {"token": jwt_token}
