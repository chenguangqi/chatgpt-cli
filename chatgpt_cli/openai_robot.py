"""一个使用OpenAI API的聊天机器人。
输入完成提示语后，使用Ctrl-Z, Enter发送。

下面是一些特殊提示:
@system <message>   设置system角色的提示
@reset              清空历史对话记录
@show               显示历史对话记录

Usage:
  openai-robot [-t TEMPERATURE | --temperature=TEMPERATURE] [-p TOP_P | --top-p TOP_P] [--max-tokens MAX_TOKENS] [--stream] [--once]
  openai-robot [-h | --help]
  openai-robot [-v | --version]

Options:
  -v --version                              显示版本信息
  -h --help                                 显示该帮助信息
  -t TEMPERATURE --temperature=TEMPERATURE  设置温度 [default: 0]
  -p TOP_P --top-p TOP_P                    设置top-p
  --max-tokens MAX_TOKENS                   补全回复的最大tokens数 [default: 2048]
  --stream                                  开始流式响应
  --once                                    不包含对话历史记录

Environment Variables:
  在运行之前，请指定下面的环境变量参数:
  OPENAI_API_VERSION
  AZURE_OPENAI_API_KEY
  AZURE_OPENAI_ENDPOINT
"""
import sys
import tiktoken
import docopt
import json
import requests

from chatgpt_cli.version import VERSION
from chatgpt_cli.settings import *


logger = get_logger(__name__, 'openai-robot.log')


MODEL = "gpt-35-turbo-16k"


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


def get_location_by_ip(ip: str = None):
    # if ip is None:
    #     response = requests.get('https://api.ipify.org')
    #     ip = response.text

    url = 'http://whois.pconline.com.cn/ipJson.jsp?ip=' + ip + '&json=true'
    response = requests.get(url)
    result = response.json()

    if result['err'] == 'noprovince':
        return json.dumps({"当前地址": result['addr']})
    else:
        return None


get_location_by_ip_func = {
    "name": "get_location_by_ip_address",
    "description": "获取当前的地址",
    "parameters": {
        "type": "object",
        "properties": {
            "ip": {
                "type": "string",
                "description": "当前网络的IP地址"
            }
        },
        "required": [],
    }
}


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

    version = args['--version']
    if version:
        print('openai-robot', VERSION)
        sys.exit(0)

    system_message = {"role": "system", "content": "You are a helpful assistant."}
    max_response_tokens = int(args['--max-tokens'])
    token_limit = 4096
    conversation = [system_message]
    # conversation = []

    temperature = args['--temperature']
    temperature = float(temperature) if temperature else None
    top_p = args['--top-p']
    top_p = float(top_p) if top_p else None

    stream = args['--stream']

    from chatgpt_cli.client import client
    if not client:
        print(docopt.printable_usage(__doc__))

        sys.exit(1)

    while True:
        conv_history_tokens = num_tokens_from_messages(conversation)

        user_input_all = []
        # if system_message:
        #     print(system_message.get('content'), flush=True)
        print(f"\033[33mQ({conv_history_tokens}):\033[0m", end='')
        while True:
            try:
                user_input = input()
                user_input = user_input.strip()
                if user_input and not user_input_all and user_input[0] == '@':
                    subcommand = user_input.split(' ', 1)
                    if subcommand[0] == '@system':
                        if len(subcommand) > 1:
                            conversation.append({"role": "system", "content": subcommand[1].strip()})
                    elif subcommand[0] == '@reset':
                        conversation = []
                    elif subcommand[0] == '@show':
                        print(conversation)
                    elif subcommand[0].startswith('@'):
                        print('不支持的命令。')

                    # 执行命令的处理后，继续等待输入。
                    break

                # print(bytes(user_input, encoding='UTF-8'))
                if user_input:
                    user_input_all.append(user_input)
            except KeyboardInterrupt:
                # 处理键盘中断。
                sys.exit(1)
            except EOFError:
                break

        # print(user_input_all)
        # 删除输入前后的空白字符。
        user_message = '\n'.join(user_input_all)
        if not user_message:
            continue

        logger.info('Q:\n%s', user_message)

        if args['--once']:
            conversation = []
        conversation.append({"role": "user", "content": user_message})
        conv_history_tokens = num_tokens_from_messages(conversation)
        # print('Tokens:', conv_history_tokens)

        # 删除多余的谈话记录，保持tokens数不超过最大限制
        while conv_history_tokens + max_response_tokens >= token_limit:
            # 删除谈话记录中的第1条记录
            del conversation[0]
            # 重新计算当前tokens数
            conv_history_tokens = num_tokens_from_messages(conversation)

        # 请求对话补全
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_response_tokens,
            stream=stream,
            # functions=[get_location_by_ip_func],
            # function_call="auto"
        )

        # response_message = response.choices[0].message
        # # Step 2: 确认 GPT 是否调用外部函数
        # if response_message.get("function_call"):
        #     # Step 3: 调用外部函数，获取结果
        #     available_functions = {
        #         "get_location_by_ip": get_location_by_ip,
        #     }
        #     function_name = response_message["function_call"]["name"]
        #     # 获取匹配到的外部函数
        #     function_to_call = available_functions[function_name]
        #     # 获取外部函数的入参信息
        #     function_args = json.loads(response_message["function_call"]["arguments"])
        #     # 调用外部函数
        #     function_response = function_to_call(
        #         ip=function_args.get("ip")
        #     )
        #
        #     # Step 4: 将原始请求和外部函数响应的结果信息发送到 GPT
        #     conversation.append(response_message)
        #     conversation.append(
        #         {
        #             "role": "function",
        #             "name": function_name,
        #             "content": function_response,
        #         }
        #     )
        #     # 进行二次请求 GPT
        #     second_response = client.chat.completions.create(
        #         model=MODEL,
        #         messages=conversation,
        #     )
        #     print("second_response=" + json.dumps(second_response))
        #     response = second_response
        # else:
        #     print("response=" + json.dumps(response))

        if stream:
            # 流式内容处理。
            content = ''
            print(f"\033[34mA({conv_history_tokens}):\033[0m")
            print(f"\033[36m{content}", flush=True)
            for chunk in response:
                delta = chunk.choices[0].delta
                # if delta.role:
                #     print(f"\033[35m{delta.role}: \033[0m", end='')
                if delta.content:
                    content += delta.content
                    print(delta.content, end='', flush=True)

                # if "context" in delta:
                #     print(f"\033[36mA({conv_history_tokens}):\033[0m\n\033[35m{delta.context}\033[0m\n")

            conversation.append({"role": "assistant", "content": content})
            print(f"\033[0m", flush=True)
            logger.info("\nA:\n%s", content)
        else:
            conversation.append({"role": "assistant", "content": response.choices[0].message.content})
            conv_history_tokens = num_tokens_from_messages(conversation)
            print(f"\033[34mA({conv_history_tokens}):\033[0m\n")
            print(f"\033[36m{response.choices[0].message.content}\033[0m\n", flush=True)
            logger.info("\nA:\n%s", response.choices[0].message.content)


if __name__ == '__main__':
    main()
