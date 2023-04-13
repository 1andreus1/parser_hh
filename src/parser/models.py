from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True)
    updated_at = Column(String)
    area_id = Column(String)
    area_name = Column(String)
    age = Column(String)
    title = Column(String)
    gender_id = Column(String)
    salary_amount = Column(String)
    salary_currency = Column(String)
    photo_medium = Column(String)
    url = Column(String)
    education = Column(String)
    experience = Column(String)
    resume_id = Column(String, unique=True)