from fastapi import APIRouter

from .azure import azure_router

__all__ = ["v1_router"]

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(azure_router)
