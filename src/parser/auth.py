"""
Этот модуль отвечает за получение авторизационных токенов
для менеджеров.
Менеджер == User.
"""
from typing import List

from src.parser.users import User
from src.parser.utils import get_response
from src.settings import settings
from .logger import log


class App:
    """
    Класс для хранения данных приложения.
    """

    def __init__(self, client_id: str, client_secret: str):
        """
        :param client_id: Идентификатор приложения.
        :param client_secret: Секретный ключ приложения.

        auth_url - ссылка для редиректа.
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = f'https://hh.ru/oauth/authorize?response_type=code&client_id={client_id}'


class Authorization:
    """
    Класс содержит методы получения токенов для
    экземпляров класса User (менеджеров).
    """

    def __init__(self):
        self.app = App(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
        )

    def get_token_for_users(self, users: List[User]) -> None:

        """
        :param users: Cписок менеджеров,
        для которых нужно получить токены.

        Получает токены для каждого менеджера из списка users.
        """

        for user in users:
            self.get_token_for_user(user)

    def update_token_for_user(self, user: User) -> None:

        """
        :param user: Менеджер, для которого нужно обновить токены.

        Делает попытку `автоматического` обновления токенов для
        менежера и при неудачной попытке запускает обновление
        `вручную`.
        """

        try:
            self.__update_access_token(user)
        except:
            log.exception(f'Не удалось обновить токен автоматически {user}')
            self.get_token_for_user(user)

    def get_token_for_user(self, user: User) -> None:

        """
        :param user: Менеджер,
        для которого нужно получить токен.

        Вызывает функцию получения токенов `вручную`
        до тех пор пока токены не будут получены.
        """

        no_authorization = True

        while no_authorization:
            no_authorization = self.__get_token_for_user(user)

        log.info(f'Токены успешно получены {user}')

    def __get_token_for_user(self, user: User) -> bool:

        """
        :param user: Менеджер, для которого нужно получить токены.
        :return: Состояение получения
        False - успешно получены,
        True - не получены(возникла ошибка).

        Получает токены `вручную`:
        Выводит ссылку и данные авторизации для получения url.

        *Пользователю необходимо перейти по ссылке и авторизоваться,
        затем скопировать url страницы после редиректа и ввести его*

        Данные полученные из ссылки сохраняются в user, затем
        вызывается __get_access_token(user) для последующего
        получения токенов доступа.
        """

        try:
            log.info(
                'Ссылка для получения authorization_code:\n'
                f'{self.app.auth_url}\n'
                f'Введите ссылку с authorization_code для:\n'
                f'{user.mail}\n{user.password}\n->'
            )

            link = input()
            user.authorization_code = link.split('=')[1]
            self.__get_access_token(user)

            return False
        except:
            log.exception(f'Повторная попытка авторизации вручную {user}')
            return True

    def __get_access_token(self, user: User) -> None:

        """
        :param user: Менеджер, для которого нужно получить токены.

        Формирует тело запроса к hh.ru на получение токенов.
        """

        data = {
            'grant_type': 'authorization_code',
            'client_id': self.app.client_id,
            'client_secret': self.app.client_secret,
            'code': user.authorization_code,
        }
        self.__get_and_set_tokens(user, data)

    def __update_access_token(self, user: User) -> None:

        """
        :param user: Менеджер, для которого нужно обновить токены.

        Функция для `автоматического` обновления токенов.
        Формирует тело запроса к hh.ru на обновление токенов.
        """

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': user.refresh_token,
        }
        self.__get_and_set_tokens(user, data)

    @staticmethod
    def __get_and_set_tokens(user: User, data: dict) -> None:

        """
        :param user: Менеджер, для которого нужно получить или
        обновить токены.
        :param data: Тело запроса  на получение или обновление
        токенов.

        Отправляет запрос на получение или обновление токенов
        для менеджера, полученные токены сохраняет в user.
        """

        _, res = get_response('POST', 'TOKEN', data=data)

        log.info(
            f'Тип запроса:{data["grant_type"]}\n'
            f'Данные ответа при обновлении токенов:\n{res}'
        )

        user.set_access_tokens(
            res['access_token'],
            res['refresh_token'],
            res['expires_in']
        )
