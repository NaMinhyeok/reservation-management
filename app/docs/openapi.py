from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.docs.description import API_DESCRIPTION, TAGS_METADATA


def custom_openapi(app: FastAPI):
    def custom_openapi_func():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=API_DESCRIPTION,
            routes=app.routes,
        )

        openapi_schema["tags"] = TAGS_METADATA

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi_func