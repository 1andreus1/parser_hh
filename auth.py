import os
import time
from typing import List, Tuple

import requests
import env
from logger import log


class App:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = f'https://hh.ru/oauth/authorize?response_type=code&client_id={client_id}'


class User:
    def __init__(self, mail: str, password: str):
        self.mail = mail
        self.password = password

        self.access_token = None
        self.refresh_token = None
        self.expires_in = None  # Время действия access_token
        self.last_update = None  # Время последнего обновления access_token

        self.authorization_code = None  # Код получаемый при редиректе

    def __repr__(self):
        return f'{self.mail} {self.access_token}'

    def set_access_tokens(self, access_token: str, refresh_token: str, expires_in: str) -> None:
        self.last_update = time.time()
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in


class Authorization:
    def __init__(self):
        self.app = App(
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret"),
        )

    def get_token_for_users(self, users: List[User]) -> None:
        for user in users:
            self.get_token_for_user(user)

    def update_token_for_users(self, users: List[User]) -> None:
        for user in users:
            self.update_token_for_user(user)

    def update_token_for_user(self, user: User) -> None:
        try:
            self.__update_access_token(user)
        except:
            log.exception(f'Не удалось обновить токен автоматически {user}')
            self.get_token_for_user(user)

    def get_token_for_user(self, user: User) -> None:
        while True:
            try:
                log.info('Ссылка для получения authorization_code:\n'
                         f'{self.app.auth_url}\n'
                         f'Введите ссылку с authorization_code для:\n'
                         f'{user.mail}\n{user.password}\n->')

                link = input()
                user.authorization_code = link.split('=')[1]
                self.__get_access_token(user)

                log.info(f'Токены успешно получены {user}')
                break
            except:
                log.exception(f'Повторная попытка авторизации вручную {user}')

    def __get_access_token(self, user: User) -> None:
        res = requests.post('https://hh.ru/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': self.app.client_id,
            'client_secret': self.app.client_secret,
            'code': user.authorization_code,
        })

        res = res.json()
        user.set_access_tokens(res['access_token'], res['refresh_token'], res['expires_in'])

    @staticmethod
    def __update_access_token(user: User) -> None:
        res = requests.post('https://hh.ru/oauth/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': user.refresh_token,
        })
        res = res.json()

        log.info(f'Данные ответа при автоматическом обновлении токенов:\n{res}')
        user.set_access_tokens(res['access_token'], res['refresh_token'], res['expires_in'])


class Users(object):
    def __init__(self):
        self.auth = Authorization()
        self.users = self.__get_users_from_txt()
        self.auth.get_token_for_users(self.users)

        self.active_user_idx = 0
        self.active_user = self.users[0]

    @staticmethod
    def __get_users_from_txt() -> List[User]:
        with open('users.txt', 'r', encoding='utf-8') as f:
            text = f.read()
        _users = text.split('\n')
        users = []
        for _user in _users:
            user = User(*_user.split(':'))
            users.append(user)
        return users

    def update_all_users(self) -> None:
        self.auth.update_token_for_users(self.users)

    def update_active_user(self) -> None:
        self.auth.update_token_for_user(self.active_user)

    def __change_active_user(self) -> None:
        self.active_user_idx += 1
        if len(self.users) == self.active_user_idx:
            self.active_user_idx = 0
        self.active_user = self.users[self.active_user_idx]

    def __check_update_time(self, user: User) -> None:
        if time.time() - user.last_update > user.expires_in:
            self.auth.update_token_for_user(user)

    def get_auth(self) -> Tuple[str, str]:
        self.__change_active_user()
        self.__check_update_time(self.active_user)
        token = self.active_user.access_token
        mail = self.active_user.mail
        return token, mail


if __name__ == '__main__':
    users = Users()
    print(users.get_auth())
