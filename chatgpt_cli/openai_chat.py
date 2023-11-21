"""OpenAI 命令行工具。

在运行之前，请指定下面的环境变量参数:
OPENAI_API_VERSION
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT

Usage: openai-chat <message>
"""
import sys
import docopt
from chatgpt_cli.role import Role
from chatgpt_cli.client import client
from chatgpt_cli.settings import get_logger


logger = get_logger(__name__, 'openai-chat.log')


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
        logger.info("\nA:\n%s %s", completionMessage.role, f'({completion.usage.total_tokens}):\n{completionMessage.content}')


def main():
    # 如果有参数错误，自动输出命令的使用方法。
    args = docopt.docopt(__doc__)
    prompt = sys.argv[1]
    if prompt:
        completion = chat([Role.user.message(prompt)])
        logger.info("Q:%s ", prompt)
        show_completion(completion)
    else:
        pass

