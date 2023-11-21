"""一个使用OpenAI API的聊天机器人。
输入完成提示语后，使用Ctrl-Z, Enter发送。

在运行之前，请指定下面的环境变量参数:
OPENAI_API_VERSION
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT

Usage:
  openai-robot [-t TEMPERATURE | --temperature=TEMPERATURE] [-p TOP_P | --top-p TOP_P] [--max-tokens MAX_TOKENS] [--stream]
  openai-robot [-h | --help]
  openai-robot [-v | --version]

Options:
  -v --version                              显示版本信息
  -h --help                                 显示该帮助信息
  -t TEMPERATURE --temperature=TEMPERATURE  设置温度
  -p TOP_P --top-p TOP_P                    设置top-p
  --max-tokens MAX_TOKENS                   补全回复的最大tokens数 [default: 250]
"""
import sys
import tiktoken
import docopt

from chatgpt_cli.version import VERSION
from chatgpt_cli.client import client
from chatgpt_cli.settings import *


logger = get_logger(__name__, 'openai-robot.log')


def num_tokens_from_messages(messages, model="gpt-35-turbo"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning("Warning: model not found. Using cl100k_base encoding.")
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
        logger.warning("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        logger.warning("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
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
    """
    温度越低，得到的结果越精确
    在大多数情况下，将 API 温度设置为 0 或接近 0（如 0.1 或 0.2）往往会得到更好的结果。 在 GPT-3 模型中，
    较高的温度可以提供有用的创意结果和随机结果，Codex 模型则不同，较高温度可能会导致收到十分随机或难以预测的响应。
    如果需要 Codex 提供不同的潜在结果，请从 0 开始，然后向上递增 0.1，直到找到合适的变体。

    :return:
    """
    # 分析输入参数
    args = docopt.docopt(__doc__)
    # print(args)

    version = args['--version']
    if version:
        print('openai-robot', VERSION)
        sys.exit(0)

    system_message = None #{"role": "system", "content": "You are a helpful assistant."}
    max_response_tokens = int(args['--max-tokens'])
    token_limit = 4096
    # conversation = [system_message]
    conversation = []

    temperature = args['--temperature']
    temperature = float(temperature) if temperature else None
    top_p = args['--top-p']
    top_p = float(top_p) if top_p else None

    stream = args['--stream']

    while True:
        conv_history_tokens = num_tokens_from_messages([system_message, *conversation] if system_message else conversation)

        user_input_all = []
        # if system_message:
        #     print(system_message.get('content'), flush=True)
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
        logger.info('Q:\n%s', user_input)
        if not user_input:
            continue

        if user_input.startswith('@system ') and user_input[8:].strip():
            system_message = {"role": "system", "content": user_input[8:].strip()}
            continue

        conversation.append({"role": "user", "content": user_input})
        conv_history_tokens = num_tokens_from_messages([system_message, *conversation] if system_message else conversation)
        # print('Tokens:', conv_history_tokens)

        # 删除多余的谈话记录，保持tokens数不超过最大限制
        while conv_history_tokens + max_response_tokens >= token_limit:
            # 删除谈话记录中的第1条记录
            del conversation[0]
            # 重新计算当前tokens数
            conv_history_tokens = num_tokens_from_messages([system_message, *conversation] if system_message else conversation)

        # 请求对话补全
        response = client.chat.completions.create(
            model="gpt-35-turbo",  # model = "deployment_name".
            messages=[system_message, *conversation] if system_message else conversation,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_response_tokens,
            stream=stream
        )

        if stream:
            # 流式内容处理。
            content = ''
            for chunk in response:
                delta = chunk.choices[0].delta
                # conversation.append({"role": "assistant", "content": response.choices[0].message.content})
                # if delta.role:
                #     print(f"\033[35m{delta.role}: \033[0m", end='')
                if delta.content:
                    content += delta.content
                    # print(f"\033[35m{delta.content}\033[0m", end='')

                # if "context" in delta:
                #     print(f"\033[36mA({conv_history_tokens}):\033[0m\n\033[35m{delta.context}\033[0m\n")

            conversation.append({"role": "assistant", "content": content})
            print(f"\033[34mA({conv_history_tokens}):\033[0m")
            print(f"\033[36m{content}\033[0m", flush=True)
            logger.info("\nA:\n%s", content)
        else:
            conversation.append({"role": "assistant", "content": response.choices[0].message.content})
            conv_history_tokens = num_tokens_from_messages([system_message, *conversation] if system_message else conversation)
            print(f"\033[34mA({conv_history_tokens}):\033[0m\n")
            print(f"\033[36m{response.choices[0].message.content}\033[0m\n", flush=True)
            logger.info("\nA:\n%s", response.choices[0].message.content)


if __name__ == '__main__':
    main()
