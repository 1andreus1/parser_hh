"""
Этот модуль отвечает за фильтрацию данных резюме
"""
from __future__ import annotations

import json
from typing import Any, Optional
from datetime import datetime

from codetiming import Timer
from pydantic import BaseModel, Field, AnyUrl


class Area(BaseModel):
    area_id: Optional[str] = Field(alias='id')
    area_name: Optional[str] = Field(alias='name')


class Gender(BaseModel):
    gender_id: Optional[str] = Field(alias='id')


class Salary(BaseModel):
    salary_amount: Optional[int] = Field(alias='amount')
    salary_currency: Optional[str] = Field(alias='currency')


class Photo(BaseModel):
    photo_medium: Optional[AnyUrl] = Field(alias='medium')


class BaseResume(BaseModel):
    id: str
    alternate_url: AnyUrl
    created_at: datetime
    updated_at: datetime
    age: Optional[int]
    title: Optional[str]
    education: Optional[Any]
    experience: Optional[Any]


class RecursiveResume(BaseResume):
    """
    Валидирует данные резюме и
    сохраняет в себе только необходимые поля.
    """
    area: Area
    gender: Gender
    salary: Salary
    photo: Photo


class NotRecursiveResume(BaseResume, Area, Gender, Salary, Photo):
    """
    Более удобное представление данных
    из класса RecursiveResume.
    """
    pass


class ResumeFilter:
    @staticmethod
    def filter(resume: dict) -> NotRecursiveResume:
        """
        :param resume: Словарь с данными резюме.
        :return: Экземпляр модели pydantic с
        только необходимыми данными прошедшими валидацию.
        """

        _resume = RecursiveResume.parse_obj(resume)
        resume = NotRecursiveResume.construct(
            id=_resume.id,
            title=_resume.title,
            age=_resume.age,
            alternate_url=_resume.alternate_url,
            created_at=_resume.created_at,
            updated_at=_resume.updated_at,
            area_id=_resume.area.area_id,
            area_name=_resume.area.area_name,
            education=_resume.education,
            experience=_resume.experience,
            gender_id=_resume.gender.gender_id,
            salary_amount=_resume.salary.salary_amount,
            salary_currency=_resume.salary.salary_currency,
            photo_medium=_resume.photo.photo_medium,
        )
        return resume


if __name__ == '__main__':
    with Timer("Времени: {{:.4f}}"):
        with open('fields.txt', 'r', encoding='utf-8') as file:
            data = json.load(file)

        resume = ResumeFilter.filter(data)
        print(resume)
