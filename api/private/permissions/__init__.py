from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Request
from api.models.permission import PermissionModel
from api.models.service import ServiceModel
from api.schemas.permission import NewPermission, BulkPromote
from app.core.fastjwt import FastJWT
from app.core.permission import check_permission, promote


permissions_router = APIRouter()


@permissions_router.get("/")
async def get_permission(
    request: Request, user_id: str = None, service: str = None, value: str = None
):
    jwt_token = await FastJWT().decode(request.headers.get("Authorisation"))

    if user_id and service and value:
        if user_id != jwt_token["user_id"]:
            await check_permission(request, service, "get_user_permission")
        else:
            await check_permission(request, service, "read_permission")
        permission = await PermissionModel.find_one(
            {"user_id": PydanticObjectId(user_id), "service": service, "value": value}
        )
        if not permission:
            raise HTTPException(status_code=403, detail="Permission denied")

        return {"message": "Permission granted"}

    await check_permission(request, "internal", "my_permissions")

    permissions = await PermissionModel.find(
        {"user_id": PydanticObjectId(jwt_token["user_id"])}
    ).to_list()
    _p = {}

    for p in permissions:
        if not p.service in _p:
            _p[p.service] = {}
        _p[p.service][p.value] = True

    return _p


@permissions_router.post("/")
async def create_permission(request: Request, payload: NewPermission):
    await check_permission(request, payload.service, "create_permission")

    if await ServiceModel.find_one({"name": payload.service}) is None:
        raise HTTPException(status_code=404, detail="Service not found")

    await promote(request, payload.service, payload.value)

    return payload


@permissions_router.post("/bulk")
async def bulk_promote(request: Request, payload: BulkPromote):
    await check_permission(request, payload.service, "bulk_promote")

    if await ServiceModel.find_one({"name": payload.service}) is None:
        raise HTTPException(status_code=404, detail="Service not found")

    _values = []

    for permission in payload.values:
        if not await PermissionModel.find_one(
            {
                "user_id": PydanticObjectId(payload.user_id),
                "service": payload.service,
                "value": permission,
            }
        ):
            _values.append(permission)

    if len(_values) == 0:
        raise HTTPException(status_code=400, detail="All permissions already exists")

    _ps = []
    for value in _values:
        _ps.append(
            PermissionModel(
                user_id=payload.user_id,
                service=payload.service,
                value=value,
            )
        )

    await PermissionModel.insert_many(_ps)

    return {"message": "Permissions created"}


@permissions_router.delete("/{service}/delete/{value}")
async def delete_permission(request: Request, service: str, value: str):
    if not service or not value:
        raise HTTPException(status_code=404, detail="Service or permission not found")

    await check_permission(request, service, "delete_permissions")

    _permissions = PermissionModel.find({"service": service, "value": value})

    if not await _permissions.to_list():
        raise HTTPException(status_code=404, detail="Permissions not found")

    await _permissions.delete()

    return {"message": "deleted"}


@permissions_router.delete("/{service}/demote/{user_id}/value")
async def demote_user(request: Request, service: str, user_id: str, value: str):
    if not service or not user_id or not value:
        raise HTTPException(
            status_code=404, detail="Service or permission or user_id arg not found"
        )

    await check_permission(request, service, "demote")

    _permission = await PermissionModel.find_one(
        {"service": service, "value": value, "user_id": PydanticObjectId(user_id)}
    )

    if not _permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    await _permission.delete()

    return {"Message": "demoted"}


@permissions_router.delete("/bulkDemote")
async def bulk_demote(request: Request, payload: BulkPromote):
    if await ServiceModel.find_one({"name": payload.service}) is None:
        raise HTTPException(status_code=404, detail="Service not found")

    await check_permission(request, payload.service, "bulk_demote")

    _permissions = await PermissionModel.find(
        {
            "service": payload.service,
            "user_id": PydanticObjectId(payload.user_id),
            "value": {"$in": payload.values},
        }
    ).delete()

    return {"message": "demoted"}
