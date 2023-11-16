"""OpenAI 命令行工具。

Usage: openai-chat <message>
"""

import sys
import docopt

from openai import AzureOpenAI

from .settings import settings
from .role import Role

client = AzureOpenAI(
    api_key=settings.get('openai', 'api_key'),
    api_version=settings.get('openai', 'api_version'),
    azure_endpoint=settings.get('openai', 'azure_endpoint', fallback=None)
)


def chat(*message, model='gpt-35-turbo-16k'):
    completion = client.chat.completions.create(
        model=model,
        messages=message
    )
    return completion


def main():
    # 如果有参数错误，自动输出命令的使用方法。
    args = docopt.docopt(__doc__)
    prompt = sys.argv[1]
    if prompt:

        completion = chat(Role.user.message(prompt))
        completionMessage = completion.choices[0].message
        print(completionMessage.role, f'({completion.usage.prompt_tokens},{completion.usage.completion_tokens},{completion.usage.total_tokens}):', completionMessage.content)
    else:
        pass


if __name__ == '__main__':
    main()
