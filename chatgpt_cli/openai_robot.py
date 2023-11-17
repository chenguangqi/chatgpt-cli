import sys
import tiktoken

from chatgpt_cli.settings import client


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
    while True:
        conv_history_tokens = num_tokens_from_messages(conversation)

        try:
            user_input = input(f"\033[33mQ({conv_history_tokens}):\033[0m")
        except KeyboardInterrupt:
            # 处理键盘中断。
            sys.exit(1)

        # 删除输入前后的空白字符。
        user_input = user_input.strip()
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
            temperature=0.7,
            max_tokens=max_response_tokens
        )

        conversation.append({"role": "assistant", "content": response.choices[0].message.content})
        print(f"\n\033[35m{response.choices[0].message.content}\033[0m\n")


if __name__ == '__main__':
    main()
