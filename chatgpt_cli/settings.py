import os
import configparser
import openai

settings = configparser.ConfigParser()
configs = [
    os.path.join(os.getcwd(), 'config.ini'),
    os.path.join(os.getenv('USERPROFILE') or os.getenv('HOME'), 'chatgpt', 'config.ini')
]
filenames = settings.read(configs, encoding='UTF-8')


openai.api_key = settings.get('openai', 'api_key', fallback=None)
openai.api_type = settings.get('openai', 'api_type', fallback=None)
openai.api_version = settings.get('openai', 'api_version', fallback=None)
openai.azure_endpoint = settings.get('openai', 'azure_endpoint', fallback=None)

