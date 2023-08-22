from fastapi import APIRouter
from api.public.auth import auth_router

public_router = APIRouter()

public_router.include_router(auth_router, prefix="/auth", tags=["auth"])