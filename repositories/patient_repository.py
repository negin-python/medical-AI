from sqlalchemy.orm import Session 
from database.models import Patientsql
from sqlalchemy import select,func
from math import ceil

#this file has just one task that direct connection with database things like select,add,delete,commit,scalars

def create_patient(db: Session,
                   name: str,
                   age: int, 
                   disease: str,
                   city:str):
    new_patient = Patientsql(name=name,
                             age=age,
                             disease=disease,
                             city=city)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


def get_patients(db: Session,
                 page: int,
                 limit: int,
                 disease:str | None=None,
                 city:str|None=None,
                 min_age:int | None = None,
                 max_age:int | None = None,
                 search:str | None = None,
                 sort:str | None=None,
                 order:str ="asc"):
    
    query = select(Patientsql)
    
    if disease is not None:
        query=query.where(Patientsql.disease == disease)

    if min_age is not None:
        query=query.where(Patientsql.age >= min_age)

    if max_age is not None:
        query=query.where(Patientsql.age <= max_age)

    if search is not None:
        query =query.where(Patientsql.name.ilike(f"%{search}%"))

    if city is not None:
        query = query.where(Patientsql.city.ilike(f"%{city}%"))

    sort_fields = {
        "name":Patientsql.name,
        "age":Patientsql.age,
        "disease":Patientsql.disease
    }
    if sort in sort_fields:
        column = sort_fields[sort]

        if order == "desc":
           query= query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query)

    offset = (page-1)*limit

    stmt = query.offset(offset).limit(limit)
    patients = db.scalars(stmt).all()

    total_pages =ceil(total/limit)

    return {
        "items":patients,
        "page":page,
        "limit":limit,
        "total":total,
        "total_pages":total_pages,
        "has_next":page < total_pages,
        "has_previous":page>1
    }

def put_patients(db: Session,
                 patient_id: int,
                 name: str,
                 age: int,
                 disease: str,
                 city:str):

    stmt = select(Patientsql).where(Patientsql.id == patient_id).with_for_update()
    patient =db.scalars(stmt).one_or_none()

    if patient is None:
        return None

    patient.name = name
    patient.age = age
    patient.disease = disease
    patient.city = city

    db.commit()
    db.refresh(patient)
    return patient



def patch_patients(db: Session,
                   patient_id: int,
                   name: str | None,
                   age: int | None, 
                   disease: str | None,
                   city:str|None=None):
    
    stmt = select(Patientsql).where(Patientsql.id == patient_id)
    patient = db.scalars(stmt).one_or_none()
    
    if patient is None:
        return None
    
    if name is not None:
        patient.name = name
    if age is not None:
        patient.age = age
    if disease is not None:
        patient.disease = disease
    if city is not None:
        patient.city = city


    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(
    db: Session,
    patient_id: int):
    
    patient = db.query(Patientsql).filter(
        Patientsql.id == patient_id
    ).first()

    if not patient:
        return None

    db.delete(patient)
    db.commit()

    return patient