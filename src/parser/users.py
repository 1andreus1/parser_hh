"""
Этот модуль отвечает за хранение информации о менеджерах
и взаимодествие с ними.
Менеджер == User.
"""

import time
from typing import List, Tuple

from src.parser.auth import Authorization
from src.settings import settings


class User:
    """
    Класс для хранения данных менеджера.
    """

    def __init__(self, mail: str, password: str):
        """
        :param mail: Адрес электронной почты менеджера.
        :param password: Пароль менеджера.

        access_token - Токен доступа.
        refresh_token - Токен обновления access_token.
        expires_in - Время действия access_token и refresh_token.
        last_update - Время последнего обновления access_token.

        authorization_code - Код получаемый при редиректе.
        """

        self.mail = mail
        self.password = password

        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.last_update = None

        self.authorization_code = None

    def __repr__(self) -> str:
        return f'{self.mail} {self.access_token}'

    def set_access_tokens(self, access_token: str, refresh_token: str, expires_in: str) -> None:
        """
        :param access_token: Токен доступа.
        :param refresh_token: Токен обновления.
        :param expires_in: Время действия токена доступа в секундах.
        """

        self.last_update = time.time()
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in


class Users:
    """
    Класс для работы с экземплярами класса User (менеджерами).
    """

    def __init__(self):
        self.auth = Authorization()
        self.users = self.__get_users_from_txt()
        self.auth.get_token_for_users(self.users)

        self.active_user_idx = 0
        self.active_user = self.users[0]

    @staticmethod
    def __get_users_from_txt() -> List[User]:

        """
        :return: Список менеджеров.

        Получает из файла логин и пароль менеджеров и инициализирует
        ими список экземпляров класса User.
        """

        with open(settings.USERS_PATH, 'r', encoding='utf-8') as f:
            text = f.read()
        _users = text.split('\n')
        users = []
        for _user in _users:
            user = User(*_user.split(':'))
            users.append(user)
        return users

    def __change_active_user(self) -> None:

        """
        Меняет активного менеджера на следующего по списку.
        """

        self.active_user_idx += 1
        if len(self.users) == self.active_user_idx:
            self.active_user_idx = 0
        self.active_user = self.users[self.active_user_idx]

    def __check_update_time(self, user: User) -> None:

        """
        :param user: Менеджер для проверки токенов.

        Вызывает функцию для обновления токенов,
        если у полученного менеджера они устарели.
        """

        if time.time() - user.last_update > user.expires_in:
            self.auth.update_token_for_user(user)

    def update_active_user(self) -> None:

        """
        Вызывает функцию для обновления токенов,
        у текущего менеджера.
        """

        self.auth.update_token_for_user(self.active_user)

    def get_auth(self) -> Tuple[str, str]:

        """
        :return: Токен авторизации , почта.

        Меняет пользователя, затем проверяет актуальность
        токенов у активного менеджера. Возвращает данные для формирования
        запроса к hh.ru.
        """

        self.__change_active_user()
        self.__check_update_time(self.active_user)
        token = self.active_user.access_token
        mail = self.active_user.mail
        return token, mail
