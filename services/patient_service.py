from sqlalchemy.orm import Session 
from database.models import Patientsql
from sqlalchemy import select


def get_patient_by_doctor(db:Session,
                          doctor_id : int):

    stmt = select(Patientsql).where(Patientsql.doctors.any(id=doctor_id))
    return db.scalars(stmt).all()

def delete_patient(db: Session, patient_id: int):

    stmt = select(Patientsql).where(Patientsql.id == patient_id)
    patient = db.execute(stmt).scalar_one_or_none()

    if patient is None:
        return None

    db.delete(patient)
    db.commit()

    return patient
