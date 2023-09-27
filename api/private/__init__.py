from fastapi import APIRouter, Depends
from api.private.permissions import permissions_router
from api.private.user import user_router
from api.private.service import service_router
from app.core.fastjwt import FastJWT

private_router = APIRouter(
    dependencies=[Depends(FastJWT().login_required)],
)

private_router.include_router(
    permissions_router, prefix="/permissions", tags=["permissions"]
)
private_router.include_router(service_router, prefix="/service", tags=["service"])
private_router.include_router(user_router, prefix="/user", tags=["user"])
