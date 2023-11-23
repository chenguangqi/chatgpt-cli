import sys
import os
import openai

api_version = os.environ.get("OPENAI_API_VERSION") or '2023-05-15'

try:
    client = openai.AzureOpenAI(api_version=api_version)
except openai.OpenAIError as ex:
    print(ex)
    sys.exit(-1)


__all__ = ['client']
