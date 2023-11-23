import sys
import os
import openai

openai.api_version = os.environ.get("OPENAI_API_VERSION") or '2023-05-15'

client = None
try:
    client = openai.AzureOpenAI(api_version=openai.api_version)
except openai.OpenAIError as ex:
    print(ex, flush=True)


__all__ = ['client']
