from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, UploadFile,BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from PIL import Image

from database.connection import get_database
from database.models import Patientsql, PatientFile
from dependencies.auth import require_permission
from sqlalchemy import select

from exceptions.custom_exceptions import AppException
from io import BytesIO



router = APIRouter(prefix="/api/v1")

UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf"
}


def file_stream(file_path):
    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            yield chunk

def process_uploaded_file(filename:str):
    print(f"processing file:{filename}")

@router.post("/files/upload/{patient_id}")
def upload_file(
    patient_id: int,
    background_task: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_database),
    user=Depends(require_permission("patient:update"))
):
    query = select(Patientsql).where(
        Patientsql.id == patient_id
    )
    patient = db.execute(query).scalar_one_or_none()

    if patient is None:
        raise AppException(
            status_code=404,
            message="Patient not found",
            error_code="PATIENT_NOT_FOUND"
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise AppException(
            status_code=400,
            message="File type not allowed",
            error_code="FILE_TYPE_NOT_ALLOWED"
        )

    file_data = file.file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise AppException(
            status_code=400,
            message="File is too large",
            error_code="FILE_IS_TOO_LARGE"
        )


    if file.content_type == "application/pdf":
        if not file_data.startswith(b"%PDF-"):
            raise AppException(
                status_code=400,
                message="Invalid PDF file",
                error_code="INVALID_PDF_FILE"
            )

    elif file.content_type in {"image/jpeg", "image/png"}:
        try:
            image = Image.open(BytesIO(file_data))

            expected_format = {
                "image/jpeg": "JPEG",
                "image/png": "PNG"
            }[file.content_type]

            if image.format != expected_format:
                raise ValueError("File format mismatch")

            image.verify()

        except Exception:
            raise AppException(
                status_code=400,
                message="Invalid image file",
                error_code="INVALID_IMAGE_FILE"
            )

    extension = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png"
    }[file.content_type]

    filename = f"{uuid.uuid4()}{extension}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / filename

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_data)

        patient_file = PatientFile(
            filename=filename,
            patient_id=patient_id
        )

        db.add(patient_file)
        db.commit()
        db.refresh(patient_file)

    except Exception as exc:
        db.rollback()
        file_path.unlink(missing_ok=True)

        raise AppException(
            status_code=500,
            message="File upload failed",
            error_code="FILE_UPLOAD_FAILED"
        ) from exc

    background_task.add_task(
        process_uploaded_file,
        filename
    )

    return {
        "message": "File uploaded successfully",
        "filename": filename,
        "patient_id": patient_id
    }

@router.get("/patients/{patient_id}/files/{filename}")
def download_patient_file(
    patient_id: int,
    filename: str,
    db: Session = Depends(get_database),
    user=Depends(require_permission("patient:read"))
):
    patient = select(PatientFile).where(
        PatientFile.filename == filename,
        PatientFile.patient_id == patient_id
    )
    patient_file = db.execute(patient).scalar_one_or_none()


    if patient_file is None:
        raise AppException(
            status_code=404,
            message="File not found for this patient",
            error_code="FILE_NOT_FOUND_FOR_THIS_PATIENT"
        )

    file_path = UPLOAD_DIR / filename

    if not file_path.is_file():
        raise AppException(
            status_code=404,
            message="File not found",
            error_code="FILE_NOT_FOUND"
        )

    return FileResponse(
        path=file_path
    )

@router.get("/patients/{patient_id}/files/{filename}/stream")
def stream_file(
    patient_id :int,
    filename: str,
    db:Session =Depends(get_database),
    user=Depends(require_permission("patient:read"))
    ):
    patient = select(PatientFile).where(PatientFile.filename == filename ,
                                                PatientFile.patient_id == patient_id)
    patient_file = db.execute(patient).scalar_one_or_none()

    if patient_file is None:
        raise AppException(
            status_code=404,
            message="File Not Found For this patient",
            error_code="FILE_NOT_FOUND_FOR_THIS_PATIENT"
        )
    
    file_path = UPLOAD_DIR / filename

    if not file_path.is_file():
        raise AppException(
            status_code=404,
            message="File not found",
            error_code="FILE_NOT_FOUND"
        )

    return StreamingResponse(
        file_stream(file_path),
        media_type="application/octet-stream"
    )


@router.get("/patients/{patient_id}/files")
def get_patient_files(
    patient_id: int,
    db: Session = Depends(get_database),
    user=Depends(require_permission("patient:read"))
):

    query = select(Patientsql).where(
        Patientsql.id == patient_id
    )
    patient = db.execute(query).scalar_one_or_none()

    if patient is None:
        raise AppException(
            status_code=404,
            message="Patient not found",
            error_code="PATIENT NOT FOUND"
        )

    query2 = select(PatientFile).where(
        PatientFile.patient_id == patient_id
    )
    files = db.execute(query2).scalars().all()

    return {
        "patient_id": patient_id,
        "files": [
            {
                "id": file.id,
                "filename": file.filename
            }
            for file in files
        ]
    }

@router.delete("/patients/{patient_id}/files/{filename}")
def delete_patient_file(
    patient_id: int,
    filename: str,
    db: Session = Depends(get_database),
    user=Depends(require_permission("patient:update"))
):

    query = select(PatientFile).where(
        PatientFile.filename == filename,
        PatientFile.patient_id == patient_id
    )
    patient_file = db.execute(query).scalar_one_or_none()

    if patient_file is None:
        raise AppException(
            status_code=404,
            message="File not found for this patient",
            error_code="FILE_NOT_FOUND_FOR_THIS_PATIENT"
        )


    file_path = UPLOAD_DIR / filename


    if file_path.is_file():
        file_path.unlink()


    db.delete(patient_file)
    db.commit()

    return {
        "message": "File deleted successfully",
        "filename": filename,
        "patient_id": patient_id
    }
