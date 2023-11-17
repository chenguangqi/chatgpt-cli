import sys
import openai

try:
    client = openai.AzureOpenAI()
except openai.OpenAIError as ex:
    print(ex)
    sys.exit(-1)


__all__ = ['client']
