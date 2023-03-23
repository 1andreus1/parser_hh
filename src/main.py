"""
Запуск парсера.
"""
import time

from src.parser.parser_hh import Parser

if __name__ == '__main__':
    end_time = int(time.time())
    start_time = end_time - 30 * 24 * 3600

    '''Запуск!'''
    parser = Parser()
    parser.run(start_time, end_time)
