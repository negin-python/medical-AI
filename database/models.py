from database.connection import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Table
from sqlalchemy.orm import relationship


#patents table
class Patientsql(Base):
    __tablename__ = "patients"

    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    age = Column(Integer,nullable=False)
    disease = Column(String,nullable=False)
    city = Column(String,nullable=False)

    files = relationship("PatientFile",back_populates="patient",
                         cascade="all,delete-orphan")

    doctors = relationship("Doctors",
                           secondary="patient_doctor",
                           back_populates="patients")

#users table
class Regisration(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True)
    role = Column(String,nullable=False)
    username = Column(String,unique=True,nullable=False)
    password = Column(String,nullable=False)

#refresh token table 
class RefreshToken(Base):
    __tablename__ = "tokens"

    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False)
    token = Column(String,nullable=False,unique=True)
    revoked = Column(Boolean,default=False)

#table for reseting password that token will reset
class RestToken(Base):
    __tablename__ = "RestTokens"

    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False)
    token = Column(String,nullable=False,unique=True)
    expried_at = Column(DateTime,nullable=False)
    used = Column(Boolean,default=False)

#table for save patients file like MRI
class PatientFile(Base):
    __tablename__ = "patient_file"

    id = Column(Integer,primary_key=True)
    filename = Column(String,nullable=False,unique=True)
    patient_id = Column(Integer,
                        ForeignKey("patients.id"),
                        nullable=False)

    patient = relationship("Patientsql",back_populates="files")

#table for save doctor's info
class Doctors(Base):
    __tablename__ = "doctors"

    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    specialty = Column(String,nullable=False)

    patients = relationship("Patientsql",
                            secondary="patient_doctor",
                            back_populates="doctors")

#junction table for many to many ralationship between doctor and patient
patient_doctor = Table(
    "patient_doctor",
    Base.metadata,
    Column("patient_id",
           ForeignKey("patients.id"),
           primary_key=True),

    Column("doctor_id",
           ForeignKey("doctors.id"),
           primary_key=True)
    )
