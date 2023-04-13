"""
Этот модуль отвечает за отправку запросов
и обработку ответов.
"""
from typing import Tuple

import requests

from src.parser.exceptions import UpdateTokenError

REQUEST_MAP = {
    'GET': requests.get,
    'POST': requests.post,
}

API_ENDPOINTS = {
    'RESUMES': 'https://api.hh.ru/resumes',
    'TOKEN': 'https://hh.ru/oauth/token',
}

TYPES_OF_AUTH_ERRORS = (
    'bad_authorization',
    'token_expired',
    'token_revoked',
)



def get_response(method: str, endpoint: str, **kwargs: dict) -> Tuple[int, dict]:
    """
    :param method: Тип запроса 'GET' или 'POST'.
    :param endpoint: Конечная точка api из API_ENDPOINTS.
    Возможные варианты: 'RESUMES', 'TOKEN'.
    :param kwargs:
    params: Тело запроса 'GET' или,
    data: Тело запроса 'POST',
    headers: Заголовки запросов.
    :return: (Статус-код ответа, Тело ответа)
    """

    res = REQUEST_MAP[method](API_ENDPOINTS[endpoint], **kwargs)
    return res.status_code, res.json()


def check_status_code(status_code: int, res: dict) -> None:
    """
    :param status_code: Статус код ответа.
    :param res: Тело ответа.

    Проверяет успешность запроса.
    Вызывает ошибку при ошибках связанных
    с авторизацией (токенами).
    """

    if status_code == 403:
        value = res.get('value')
        if value in TYPES_OF_AUTH_ERRORS:
            raise UpdateTokenError(value)
        else:
            raise ConnectionError(value)
