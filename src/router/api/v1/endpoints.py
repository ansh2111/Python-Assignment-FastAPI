from fastapi import APIRouter

from src.products import endpoints as products_endpoints

api_router = APIRouter()

api_router.include_router(products_endpoints.router, prefix="/products", tags=["Products"])