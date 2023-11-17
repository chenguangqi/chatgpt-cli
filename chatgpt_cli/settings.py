import os
import sys
import configparser
import logging

# settings = configparser.ConfigParser()
# configs = [
#     os.path.join(os.path.dirname(__file__), 'config.ini'),
#     # os.path.join(os.getenv('USERPROFILE') or os.getenv('HOME'), 'chatgpt', 'config.ini')
# ]
# filenames = settings.read(configs, encoding='UTF-8')


def get_logger(name, filename, has_stdout=False):
    logger = logging.Logger(name, logging.INFO)
    file_handler = logging.FileHandler(filename, encoding='UTF-8')
    file_handler.setFormatter(logging.Formatter())
    logger.addHandler(file_handler)
    if has_stdout:
        logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger


__all__ = ['get_logger']