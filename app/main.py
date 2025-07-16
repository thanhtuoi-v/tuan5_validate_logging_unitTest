from fastapi import FastAPI
from app.api.v1.endpoints.vod import router as vod_router

from app.core.logging import setup_logging
from app.core.exception_handles import http_exception_handler, validation_exception_handler

from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException



app = FastAPI(title="VOD Service API")
# setup_logging()

# app.add_exception_handler(HTTPException, http_exception_handler)
# app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(vod_router, prefix="/api/v1", tags=["VOD"])