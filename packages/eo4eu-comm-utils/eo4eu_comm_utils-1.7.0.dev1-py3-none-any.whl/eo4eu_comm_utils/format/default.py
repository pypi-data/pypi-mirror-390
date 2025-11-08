from .log import LogFormatter


def _get_kwargs_by_verbosity(verbosity: int = 0) -> dict:
    if verbosity == 1:
        return {
            "add_name": False,
            "add_path": True,
            "before_message": "\n",
        }
    elif verbosity == 2:
        return {
            "print_traceback": True,
        }
    elif verbosity == 3:
        return {
            "print_traceback": True,
            "add_name": False,
            "add_path": True,
            "before_message": "\n",
        }
    return {}

def get_default_logging_config(verbosity: int = 0, level: str = "INFO") -> dict:
    """Creates a dict to be consumed by logging.config.dictConfig. 
    The config uses a :class:`LogFormatter` and prints to the console

    :param verbosity: Integer 0-3, going from more to less verbose. It is recommended that you use 0 for production and 2 for testing
    :type verbosity: int
    :param level: The level of the logger. Default is INFO
    :type level: str
    :rtype: dict
    """
    kwargs = _get_kwargs_by_verbosity(verbosity)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "()": LogFormatter,
                **kwargs
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    }


def get_dual_logging_config(log_file: str, verbosity: int = 0, level: str = "INFO") -> dict:
    """Creates a dict to be consumed by logging.config.dictConfig. 
    The config uses a :class:`LogFormatter` and prints to the console and a 
    given file

    :param log_file: The log file to print logs to
    :type log_file: str
    :param verbosity: Integer 0-3, going from more to less verbose. It is recommended that you use 0 for production and 2 for testing
    :type verbosity: int
    :param level: The level of the logger. Default is INFO
    :type level: str
    :rtype: dict
    """
    kwargs = _get_kwargs_by_verbosity(verbosity)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "()": LogFormatter,
                **kwargs
            },
            "file": {
                "()": LogFormatter,
                **(kwargs | {"use_color": False})
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": str(log_file),
                "formatter": "file",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": level,
        },
    }


# Prints to the console and two log files with different levels of verbosity
def get_triple_logging_config(
    log_file_terse: str,
    log_file_verbose: str,
    low_verbosity: int = 0,
    high_verbosity: int = 2,
    level: str = "INFO"
) -> dict:
    """Creates a dict to be consumed by logging.config.dictConfig. 
    The config uses a :class:`LogFormatter` and prints to the console and TWO 
    files; one with low and one with high verbosity

    :param log_file_terse: The log file to print low verbosity logs to
    :type log_file_terse: str
    :param log_file_verbose: The log file to print high verbosity logs to
    :type log_file_verbose: str
    :param low_verbosity: Integer 0-3, going from more to less verbose. It is recommended that you use 0 for this
    :type low_verbosity: int
    :param high_verbosity: Integer 0-3, going from more to less verbose. It is recommended that you use 2 for this
    :type high_verbosity: int
    :param level: The level of the logger. Default is INFO
    :type level: str
    :rtype: dict
    """
    low_kwargs = _get_kwargs_by_verbosity(low_verbosity)
    high_kwargs = _get_kwargs_by_verbosity(high_verbosity)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "()": LogFormatter,
                **low_kwargs
            },
            "file_terse": {
                "()": LogFormatter,
                **(low_kwargs | {"use_color": False})
            },
            "file_verbose": {
                "()": LogFormatter,
                **(high_kwargs | {"use_color": False})
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "file_terse": {
                "class": "logging.FileHandler",
                "filename": str(log_file_terse),
                "formatter": "file_terse",
            },
            "file_verbose": {
                "class": "logging.FileHandler",
                "filename": str(log_file_verbose),
                "formatter": "file_verbose",
            },
        },
        "root": {
            "handlers": ["console", "file_terse", "file_verbose"],
            "level": level,
        },
    }
