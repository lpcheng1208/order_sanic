# coding=utf-8


_LEVEL = 'DEBUG'


def _file_handler(log_fname, formatter='simple'):
    return {
        'level': 'DEBUG',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'formatter': formatter,
        'filename': 'log/%s.log' % log_fname,
        'when': 'midnight', 'backupCount': 7,
        'encoding': 'utf-8'
    }


def _log_dict(handler, level="DEBUG"):
    return {'handlers': [handler], 'level': level, 'propagate': False}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] %(message)s',
        },
        'print': {
            'format': '%(asctime)s %(message)s',
        }
    },
    'handlers': {
        'null': {'level': 'DEBUG', 'class': 'logging.NullHandler'},
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'simple'}
    },
    'loggers': {
        # 'root': _log_dict('null', level=_LEVEL),
    }
}


def _add(*names, formatter='simple'):
    for name in names:
        LOGGING.get("handlers")[name] = _file_handler(name, formatter=formatter)
        LOGGING.get("loggers")[name] = _log_dict(name, level=_LEVEL)


_add("root", "actor_list")
