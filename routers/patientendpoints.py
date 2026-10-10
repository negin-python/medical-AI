from fastapi import APIRouter, Depends, HTTPException, Query, Response
from schemas.patient import (
    Patient,
    PatientUpdate,
    PatientPatch,
    PatientFilter,
    PatientResponseWrapper,
    PatientListResponseWrapper,
    PatientPatchWrapper,
    DeletePatient
)
from database.connection import get_database
from dependencies.auth import require_permission
from services import patient_service
from enum import Enum
from sqlalchemy.orm import Session, selectinload
from database.models import Patientsql, Doctors, patient_doctor
from sqlalchemy import select, exists
from repositories import patient_repository

from exceptions.custom_exceptions import AppException


router = APIRouter(prefix="/api/v1")


class Sortfield(str, Enum):
    name = "name"
    age = "age"
    disease = "disease"


class Sortorder(str, Enum):
    asc = "asc"
    desc = "desc"


# =========================
# PATIENTS
# =========================

@router.post(
    "/patients",
    response_model=PatientResponseWrapper,
    status_code=201
)
def create_patients(
    patient: Patient,
    db=Depends(get_database),
    user=Depends(require_permission("patient:create"))
):
    patient = patient_repository.create_patient(
        db=db,
        name=patient.name,
        age=patient.age,
        disease=patient.disease,
        city=patient.city
    )

    return {
        "success": True,
        "message": "patient created successfully",
        "data": patient
    }


@router.get(
    "/patients",
    response_model=PatientListResponseWrapper
)
def get_patients(
    response: Response,
    db=Depends(get_database),
    user=Depends(require_permission("patient:read")),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100, ge=2),
    filter: PatientFilter = Depends(),
    sort: Sortfield | None = None,
    order: Sortorder = Sortorder.asc
):
    patient = patient_repository.get_patients(
        db=db,
        page=page,
        limit=limit,
        disease=filter.disease,
        min_age=filter.min_age,
        max_age=filter.max_age,
        search=filter.search,
        sort=sort,
        order=order
    )

    response.headers["X-API-Version"] = "1"

    return {
        "success": True,
        "message": "patient retrived successfull",
        "data": patient
    }


@router.put(
    "/patients/{patient_id}",
    response_model=PatientResponseWrapper
)
def update_patients(
    patient_id: int,
    patient: PatientUpdate,
    db=Depends(get_database),
    user=Depends(require_permission("patient:update"))
):
    updated = patient_repository.put_patients(
        db=db,
        patient_id=patient_id,
        name=patient.name,
        age=patient.age,
        disease=patient.disease,
        city=patient.city
    )

    if updated is None:
        raise AppException(
            status_code=404,
            message="Patient not found",
            error_code="PATIENT NOT FOUND"
        )

    return {
        "success": True,
        "message": "patient updated",
        "data": updated
    }


@router.patch(
    "/patients/{patient_id}",
    response_model=PatientPatchWrapper
)
def partial_update_patients(
    patient_id: int,
    patient: PatientPatch,
    db=Depends(get_database),
    user=Depends(require_permission("patient:update"))
):
    updated = patient_repository.patch_patients(
        db=db,
        patient_id=patient_id,
        name=patient.name,
        age=patient.age,
        disease=patient.disease,
        city=patient.city
    )

    if updated is None:
        raise AppException(
            status_code=404,
            message="Patient not found",
            error_code="PATIENT NOT FOUND"
        )

    return {
        "success": True,
        "message": "patient updated",
        "data": updated
    }


@router.delete(
    "/patients/{patient_id}",
    response_model=DeletePatient
)
def delete_patients(
    patient_id: int,
    db=Depends(get_database),
    user=Depends(require_permission("patient:delete"))
):
    deleted = patient_repository.delete_patient(
        db=db,
        patient_id=patient_id
    )

    if deleted is None:
        raise AppException(
            status_code=404,
            message="Patient not found",
            error_code="PATIENT NOT FOUND"
        )

    return {
        "success": True,
        "message": "Patient deleted successfully",
        "data": None
    }


# =========================
# ASSIGN DOCTOR TO PATIENT
# =========================

@router.post(
    "/patients/{patient_id}/doctors/{doctor_id}"
)
def assign_doctor(
    patient_id: int,
    doctor_id: int,
    db: Session = Depends(get_database)
):
    query1 = select(Patientsql).where(
        Patientsql.id == patient_id
    )

    patient = db.execute(query1).scalar_one_or_none()

    if patient is None:
        raise AppException(
            status_code=404,
            message="patient not found",
            error_code="PATIENT NOT FOUND"
        )

    query2 = select(Doctors).where(
        Doctors.id == doctor_id
    )

    doctor = db.execute(query2).scalar_one_or_none()

    if doctor is None:
        raise AppException(
            status_code=404,
            message="doctor not found",
            error_code="DOCTOR NOT FOUND"
        )

    patient.doctors.append(doctor)

    db.commit()

    return {
        "message": "doctor assigned to patient",
        "patient_id": patient_id,
        "doctor_id": doctor_id
    }


# =========================
# GET PATIENTS OF A DOCTOR
# =========================

@router.get(
    "/doctors/{doctor_id}/patients"
)
def get_doctor_patients(
    doctor_id: int,
    db: Session = Depends(get_database)
):
    query = (
        select(Doctors)
        .options(selectinload(Doctors.patients))
        .where(Doctors.id == doctor_id)
    )

    doctor = db.scalars(query).one_or_none()

    if doctor is None:
        raise AppException(
            status_code=404,
            message="Doctor not found",
            error_code="DOCTOR NOT FOUND"
        )

    return [
        {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "disease": patient.disease
        }
        for patient in doctor.patients
    ]


# =========================
# DELETE DOCTOR
# =========================

@router.delete(
    "/doctors/{doctor_id}"
)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_database)
):
    stmt = select(Doctors).where(
        Doctors.id == doctor_id
    )

    doctor = db.scalars(stmt).one_or_none()

    if doctor is None:
        raise AppException(
            status_code=404,
            message="Doctor not found",
            error_code="DOCTOR NOT FOUND"
        )

    check_stmt = select(
        exists().where(
            patient_doctor.c.doctor_id == doctor_id
        )
    )

    has_patients = db.scalar(check_stmt)

    if has_patients:
        raise HTTPException(
            status_code=400,
            detail="Doctor still has patients"
        )

    db.delete(doctor)

    db.commit()

    return {
        "message": "Doctor deleted successfully"
    }


# =========================
# GET PATIENTS OF DOCTOR
# USING SERVICE
# =========================

@router.post(
    "/doctors/{doctor_id}/patients"
)
def get_patients_for_doctor(
    doctor_id: int,
    db: Session = Depends(get_database)
):
    patients = patient_service.get_patient_by_doctor(
        db=db,
        doctor_id=doctor_id
    )

    return [
        {
            "id": patient.id,
            "name": patient.name,
            "disease": patient.disease,
            "city": patient.city
        }
        for patient in patients
    ]

