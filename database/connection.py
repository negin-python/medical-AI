from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from hospital_api.config import settings

engine = create_engine(settings.DATABASE_URL)

sessionlocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

Base = declarative_base()



def get_database():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()