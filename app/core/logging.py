import logging


def get_logger(module_name: str) -> logging.Logger:
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    exception_logger = logging.getLogger(module_name)
    exception_logger.addHandler(handler)
    return exception_logger
