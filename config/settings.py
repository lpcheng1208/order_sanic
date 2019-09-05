
# mysql
import logging
from logging.config import dictConfig

mysql_db = {
    # 'host':'rm-bp19sxe4z64k392y7go.mysql.rds.aliyuncs.com',
    'host':'127.0.0.1',
    'port':3306,
    'user':'root',
    'password':'abcd1234',
    'extends':'test',
    'minsize':1,
    'maxsize':20,
    'charset':'utf8mb4',
}

redis_config = {
    'address': ('127.0.0.1', 6380),
    'extends': 0,
    'password':'',
    'minsize': 1,
    'maxsize': 10,
}

'''
python自带日志
'''
logging_config = dict(
    version=1,
    formatters={
        'default': {
            'format': "[%(asctime)s]: %(filename)s:%(lineno)d %(levelname)s %(message)s "
        }
    },
    filter={
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': logging.INFO
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'log/all.log',
            'formatter': 'default',
            'level': logging.INFO
        },
    },
    loggers={
        'sanic': {
            'handlers': ['file'],
            'level': logging.INFO,
            "encoding": "utf8"
        },
        'extends': {
            'handlers': ['file'],
            'level': logging.INFO,
            "encoding": "utf8"
        },
        'view': {
            'handlers': ['file'],
            'level': logging.INFO,
            "encoding": "utf8"
        },
        'user': {
            'handlers': ['file'],
            'level': logging.INFO,
            "encoding": "utf8"
        },
    }
)

dictConfig(logging_config)

try:
    from .local_settings import *
except ImportError:
    pass



