from fastapi import FastAPI

from src.config import config
from src.router.api.v1.endpoints import api_router

app = FastAPI(title=config.APP_NAME,
              openapi_url=f"{config.API_PREFIX}/openapi.json",
              version=config.VERSION,
              debug=config.DEBUG)

app.include_router(api_router, prefix=config.API_PREFIX)


@app.get("/", tags=["Health check"])
async def health_check():
    return {"name": "Products scraping API",
            "type": "scraper-api",
            "description": "The software that scrapes products on request",
            "documentation": "/docs",
            "version": config.VERSION}