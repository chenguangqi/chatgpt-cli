"""OpenAI 命令行工具。

Usage: openai-chat <message>
"""

import sys
import docopt
from chatgpt_cli.role import Role
from chatgpt_cli.settings import client


def chat(messages, model='gpt-35-turbo-16k'):
    completion = None
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
    except Exception as ex:
        print(ex)
    return completion


def show_completion(completion):
    if completion:
        completionMessage = completion.choices[0].message
        print(completionMessage.role, f'({completion.usage.total_tokens}):\n{completionMessage.content}')


def main():
    # 如果有参数错误，自动输出命令的使用方法。
    args = docopt.docopt(__doc__)
    prompt = sys.argv[1]
    if prompt:
        completion = chat([Role.user.message(prompt)])
        show_completion(completion)
    else:
        pass


if __name__ == '__main__':
    main()
