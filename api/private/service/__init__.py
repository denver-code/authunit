from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Request
from random import randint
from api.models.permission import PermissionModel
from api.models.service import ServiceModel
from api.schemas.service import NewService
from app.core.fastjwt import FastJWT
from datetime import datetime

from app.core.permission import check_permission

service_router = APIRouter()


@service_router.post("/")
async def create_service(payload: NewService, request: Request):
    await check_permission(request, "internal", "create_service")
    # name should be lowercase string withouth spaces and special characters
    payload.name = payload.name.lower().replace(" ", "_")

    if await ServiceModel.find_one({"name": payload.name}):
        raise HTTPException(status_code=400, detail="Service already exists")

    access_code = randint(1000000, 9999999)

    _service = ServiceModel(
        name=payload.name,
        description=payload.description,
        access_code=access_code,
    )

    await _service.save()

    token = await FastJWT().encode(
        {
            "service_name": payload.name,
            "access_code": access_code,
        }
    )

    return {
        "name": payload.name,
        "token": token,
    }


@service_router.get("/{service_name}/token")
async def get_service_token(service_name: str, request: Request):
    await check_permission(request, "internal", "generate_service_token")

    service = await ServiceModel.find_one({"name": service_name})

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    access_code = randint(1000000, 9999999)

    service.access_code = access_code
    service.updated_at = datetime.now()
    await service.save()

    token = await FastJWT().encode(
        {
            "service_name": service.name,
            "access_code": service.access_code,
        }
    )

    return {
        "name": service.name,
        "token": token,
    }


@service_router.get("/checkUser")
async def check_user_permission(
    request: Request, user_id: str = None, value: str = None
):
    jwt_token = await FastJWT().decode(request.headers["Authorisation"])

    service = await ServiceModel.find_one(
        {
            "name": jwt_token.get("service_name"),
            "access_code": jwt_token.get("access_code"),
        }
    )

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found, keep in mind that this service is only for service's use.",
        )

    permission = await PermissionModel.find_one(
        {
            "user_id": PydanticObjectId(user_id),
            "service": service.name,
            "value": value,
        }
    )
    if not permission:
        raise HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Permission granted"}
