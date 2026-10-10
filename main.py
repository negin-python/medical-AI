from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.patientendpoints import router as patient_router
from uploads.uploads import router as uploads_router
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
import traceback
from exceptions.custom_exceptions import AppException
from exceptions.handler import exception_handler,validation_error_handler,database_exception_handler

from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

import time

from core.logger import logger


app = FastAPI(
    title="medical API",
    debug=False
)


app.add_exception_handler(
    AppException,
    exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler

)

app.add_exception_handler(
    IntegrityError,
    database_exception_handler
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    traceback.print_exc()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request:Request,exc:Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "success":False,
            "message": "Internal Server Error",
            "data":None
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)


@app.middleware("http")
async def my_middleware(request:Request,call_next):
    start_time = time.time()

    logger.info(f"Request recived|"
                f"{request.method}{request.url.path}")

    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"Response sent|"
        f"{request.method} {request.url.path}|"
        f"status={response.status_code}|"
        f"time={process_time:.3f}s"
    )
   
    return response


app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(uploads_router)