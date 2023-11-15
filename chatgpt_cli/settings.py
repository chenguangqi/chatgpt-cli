import os
import configparser

settings = configparser.ConfigParser()
configs = [
    os.path.join(os.getcwd(), 'config.ini'),
    os.path.join(os.getenv('USERPROFILE') or os.getenv('HOME'), 'chatgpt', 'config.ini')
]
filenames = settings.read(configs, encoding='UTF-8')
