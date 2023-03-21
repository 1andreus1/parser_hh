from loguru import logger as log

log.add('logs.log',
           format='{time} | {level} | {message}',
           rotation='10 MB',
           compression='zip')

