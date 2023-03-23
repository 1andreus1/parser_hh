"""
Этот модуль отвечает за фильтрацию данных резюме
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from codetiming import Timer
from pydantic import BaseModel, Field, AnyUrl, validator


class Area(BaseModel):
    area_id: Optional[str] = Field(alias='id', default=None)
    area_name: Optional[str] = Field(alias='name', default=None)


class Gender(BaseModel):
    gender_id: Optional[str] = Field(alias='id', default=None)


class Salary(BaseModel):
    salary_amount: Optional[int] = Field(alias='amount', default=None)
    salary_currency: Optional[str] = Field(alias='currency', default=None)


class Photo(BaseModel):
    photo_medium: Optional[AnyUrl] = Field(alias='medium', default=None)


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
    area: Area = Field(default=Area())
    gender: Gender = Field(default=Gender())
    salary: Salary = Field(default=Salary())
    photo: Photo = Field(default=Photo())

    @validator('area', 'gender', 'salary', 'photo', pre=True)
    def none_must_be_default(cls, v: Any, field: Field) -> Any:
        """
        :param v: Значение которое нужно валидировать.
        :param field: Объект поля модели
        с атрибутами и настройками для валидации.
        :return: Значение которое не является None.

        Преобразует None в значение по умолчанию.
        """
        if v is None:
            return field.default
        return v


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
        path = r'C:\Users\Andrey\PycharmProjects\MyWork\parsers\hh_gitlab\parser\tests\fields.txt'
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        resume = ResumeFilter.filter(data)
