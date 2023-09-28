from fastapi import APIRouter, HTTPException, Request
from beanie import PydanticObjectId
from app.core.fastjwt import FastJWT
from api.models.user import UserModel
from api.schemas.user import ChangePassword
from app.core.password import hash_password
from app.core.permission import check_permission

user_router = APIRouter()


@user_router.get("/me")
async def my_profile(request: Request):
    jwt_token = await FastJWT().decode(request.headers["Authorisation"])
    user = await UserModel.find_one({"_id": PydanticObjectId(jwt_token.get("user_id"))})
    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid credentials or user not exist"
        )
    user = user.model_dump(exclude={"password", "revision_id"})

    return user


@user_router.patch("/password")
async def change_password(request: Request, payload: ChangePassword):
    payload.new_password = hash_password(payload.new_password)
    payload.old_password = hash_password(payload.old_password)

    if payload.new_password == payload.old_password:
        raise HTTPException(
            status_code=400, detail="New password can't be same as old."
        )

    jwt_token = await FastJWT().decode(request.headers["Authorisation"])
    user = await UserModel.find_one(
        {
            "_id": PydanticObjectId(
                jwt_token.get("user_id"),
            ),
            "password": payload.old_password,
        }
    )

    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid credentials or user not exist"
        )

    user.password = payload.new_password
    await user.save()

    return {"message": "Password Updated."}


@user_router.get("/all")
async def all_users(request: Request):
    await check_permission(request, "internal", "users_list")

    _users = await UserModel.find().to_list()

    users = []
    for user in _users:
        user = user.model_dump(exclude={"password", "revision_id"})
        users.append(user)

    return users
