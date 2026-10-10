from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder

from core.logger import logger

async def exception_handler(request:Request,
                            exc:Exception):
    logger.error(
        f"{request.method}{request.url.path}|"
        f"{exc.error_code}|{exc.message}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success":False,
            "message":exc.message,
            "error_code":exc.error_code

        }
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "validation error",
            "error_code": "VALIDATION_ERROR",
            "detail": jsonable_encoder(exc.errors())
        }
    )
async def database_exception_handler(
        requset:Request,
        exc:IntegrityError
):
    return JSONResponse(
        status_code=409,
        content={
            "success":False,
            "message":"database validation content error",
            "error_code":"DATABASE_VALIDATION_ERROR" }

    )
