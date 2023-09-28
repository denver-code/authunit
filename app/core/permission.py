from beanie import PydanticObjectId
from fastapi import HTTPException, Request
from api.models.permission import PermissionModel
from app.core.fastjwt import FastJWT


async def check_permission(request: Request, service: str, value: str):
    permission = await PermissionModel.find_one(
        {
            "user_id": PydanticObjectId(
                (await FastJWT().decode(request.headers.get("Authorisation")))[
                    "user_id"
                ]
            ),
            "service": service,
            "value": value,
        }
    )

    if not permission:
        raise HTTPException(
            status_code=403,
            detail="Permission denied for this action, please contact your administrator if you think this is a mistake.",
        )


async def promote(request: Request, service: str, value: str):
    user_id = PydanticObjectId(
        (await FastJWT().decode(request.headers.get("Authorisation"))).get("user_id")
    )
    if await PermissionModel.find_one(
        {
            "user_id": user_id,
            "service": service,
            "value": value,
        }
    ):
        raise HTTPException(status_code=400, detail="Permission already exists")

    _perm = await PermissionModel(
        user_id=user_id,
        service=service,
        value=value,
    ).save()

    return _perm
