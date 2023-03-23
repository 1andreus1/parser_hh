"""
Этот модуль отвечает за логику работы всего парсера.
"""
import time
from math import ceil
from typing import Optional, Union, List

from src.parser.exceptions import UpdateTokenError
from src.parser.logger import log
from src.parser.schemas import ResumeFilter, NotRecursiveResume
from src.parser.users import Users
from src.parser.utils import check_status_code, get_response


class Parser:
    """
    Основной класс отвечает за логику работы всего парсера.
    """

    def __init__(self):
        # self.db = DataBase()
        # self.__init_db()

        self.users = Users()

        self.time_interval = 3600 * 24 * 30

    def run(self, start_time: int, end_time: int) -> None:

        """
        :param start_time: Начало временного отрезка.
        :param end_time: Конец временного отрезка.
        """

        if start_time >= end_time:
            raise ValueError('end_time должно быть больше start_time')

        log.info('Начало сбора резюме')

        found = self.waiting_get_resumes('found', start_time, end_time)
        log.info(f'Ожидаемое кол-во резюме: {found}')

        self.parse(start_time, end_time)

        log.info('Парсер успешно закончил работу')

    def parse(self, start_time: int, end_time: int) -> None:

        """
        :param start_time: Начало временного отрезка.
        :param end_time: Конец временного отрезка.

        Деление на временные отрезки не превышающие
        длинны self.time_interval секунд.
        """

        for _start_time in range(int(start_time), int(end_time), self.time_interval):
            _end_time = _start_time + self.time_interval
            if _end_time > end_time:
                _end_time = end_time
            self.recursive_div(_start_time, _end_time)

    def recursive_div(self, start_time: int, end_time: int) -> None:

        """
        :param start_time: Начало временного отрезка.
        :param end_time: Конец временного отрезка.

        Основная рекурсивная функция.
        Делит временной отрезок на части с кол-вом резюме < 2000.
        Для последующего сбора.
        """

        found = self.waiting_get_resumes('found', start_time, end_time)

        if found <= 2000:
            self.save_all_resumes(start_time, end_time, found)
        elif end_time - start_time < 0.5:
            self.save_all_resumes(start_time, end_time, 1999)
        else:
            mid = (start_time + end_time) // 2
            self.recursive_div(start_time, mid)
            self.recursive_div(mid, end_time)

    def save_all_resumes(self, start_time: int, end_time: int, found: int) -> None:

        """
        :param start_time: Начало временного отрезка.
        :param end_time: Конец временного отрезка.
        :param found: Кол-во найденных резюме.

        Получает резюме пачками размера не более 100шт.
        """

        count_pages = ceil(found / 100)
        for page in range(count_pages):
            items = self.waiting_get_resumes('items', start_time, end_time, page)
            self.save_resumes(items)

    def waiting_get_resumes(
            self,
            key: str,
            start_time: int,
            end_time: int,
            page: Optional[int] = None
    ) -> Union[List[dict], int]:

        """
        :param key: Тип ожидаемых данных
        'items' (для получения резюме) или
        'found' (для полуения кол-ва резюме).
        :param start_time: Начало временного отрезка.
        :param end_time: Конец временного отрезка.
        :param page: Номер страницы.
        :return: Ожидаемые резюме.
        """

        delay = 0
        while True:
            try:
                time.sleep(delay)
                res = self.get_resumes(start_time, end_time, page)
                res = res[key]
                return res
            except UpdateTokenError:
                log.exception('Токены просрочены. Попытка обновления.')
                self.users.update_active_user()
            except (Exception,):
                log.exception(f'Ожидание ответа {delay} секунд')
                if delay == 0:
                    delay += 1
                else:
                    delay *= 2

    def get_resumes(self, start_time: int, end_time: int, page: Optional[int] = None) -> dict:

        """
        :param start_time: Начало временного отрезка.
        :param end_time: Конец временного отрезка.
        :param page: Номер страницы.
        :return: Словарь резюме.

        Формирует и отправляет запрос к hh
        на получение не более 100 резюме.
        """

        params = {
            'date_from': self.time_str(start_time),
            'date_to': self.time_str(end_time),
            'per_page': 100,
        }
        if page is not None:
            params['page'] = page

        headers = self.get_headers()
        status_code, res = get_response('GET',
                                        'RESUMES',
                                        headers=headers,
                                        params=params)

        check_status_code(status_code, res)

        return res

    def get_headers(self) -> dict:

        """
        :return: Заголовки запроса к hh.

        Формирует заголовки запроса к hh
        с использованием авторизационных токенов.
        """

        token, mail = self.users.get_auth()
        headers = {
            'User-Agent': f'Vakansii {mail}',
            'Authorization': f'Bearer {token}',
        }
        return headers

    def save_resumes(self, resumes: List[dict]) -> None:

        """
        :param resumes: Список необработанных резюме.

        Обрабатывает резюме и сохраняет в БД.
        """

        try:
            resumes = self.filter_resumes(resumes)
            print(resumes)
            # self.db.add_to_database(resumes)
        except (Exception,):
            log.exception('Не удалось сохранить резюме')

    @staticmethod
    def filter_resumes(resumes: List[dict]) -> List[NotRecursiveResume]:

        """
        :param resumes: Список необработанных резюме.
        :return: Список экземпляров класса NotRecursiveResume
        с данными резюме прошедшими валидацию.

        Валидирует и фильтрует данные с помощью pydantic.
        """

        _resumes = []
        for resume in resumes:
            _resumes.append(ResumeFilter.filter(resume))
        return _resumes

    # def __init_db(self):
    #     if input('Нажмите (y) если нужно создать бд.') == 'y':
    #         self.db.delete_database()
    #         self.db.create_db()
    #         print('База данных создана')
    #     else:
    #         if input('Нажмите (y) если нужно очистить бд.') == 'y':
    #             self.db.clear_database()
    #             print('База данных очищена')

    @staticmethod
    def time_str(seconds: int) -> str:

        """
        :param seconds: Время в секундах.
        :return: Представление даты и времени
        в формате поддерживаемом hh.

        Конвертирует время в секундах в
        строковое представление даты и времени,
        которое поддерживает hh.ru.
        """

        return time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.localtime(seconds))
