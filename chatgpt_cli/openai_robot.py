"""一个使用OpenAI API的聊天机器人。

Usage:
  openai-robot
  openai-robot [-t temperature | --temperature=temperature]
  openai-robot [-h | --help]
  openai-robot [-v | --version]

Options:
  -v --version                              显示版本信息
  -h --help                                 显示该帮助信息
  -t temperature --temperature=temperature  设置温度

"""

import sys
import tiktoken
import docopt

from chatgpt_cli.settings import client
from chatgpt_cli.version import VERSION


system_message = {"role": "system", "content": "You are a helpful assistant."}
max_response_tokens = 250
token_limit = 4096
conversation = [system_message]


def num_tokens_from_messages(messages, model="gpt-35-turbo"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-35-turbo",
        "gpt-35-turbo-16k",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def main():
    # 分析输入参数
    args = docopt.docopt(__doc__)
    # print(args)

    version = args['--version']
    if version:
        print('openai-robot', VERSION)
        sys.exit(0)

    temperature = args['--temperature']
    temperature = float(temperature) if temperature else None

    while True:
        conv_history_tokens = num_tokens_from_messages(conversation)

        user_input_all = []
        print(f"\033[33mQ({conv_history_tokens}):\033[0m", end='')
        while True:
            try:
                user_input = input()
                # print(bytes(user_input, encoding='UTF-8'))
                user_input_all.append(user_input)
            except KeyboardInterrupt:
                # 处理键盘中断。
                sys.exit(1)
            except EOFError:
                break

        # print(user_input_all)
        # 删除输入前后的空白字符。
        user_input = '\n'.join(user_input_all)
        # print(user_input)
        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})
        conv_history_tokens = num_tokens_from_messages(conversation)
        # print('Tokens:', conv_history_tokens)

        # 删除多余的谈话记录，保持tokens数不超过最大限制
        while conv_history_tokens + max_response_tokens >= token_limit:
            # 删除谈话记录中的第2条记录
            del conversation[1]
            # 重新计算当前tokens数
            conv_history_tokens = num_tokens_from_messages(conversation)

        # 请求对话补全
        response = client.chat.completions.create(
            model="gpt-35-turbo",  # model = "deployment_name".
            messages=conversation,
            temperature=temperature,
            max_tokens=max_response_tokens
        )

        conversation.append({"role": "assistant", "content": response.choices[0].message.content})
        conv_history_tokens = num_tokens_from_messages(conversation)
        print(f"\033[36mA({conv_history_tokens}):\033[0m\n\033[35m{response.choices[0].message.content}\033[0m\n")


if __name__ == '__main__':
    main()
