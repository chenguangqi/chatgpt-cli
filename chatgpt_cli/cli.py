# Note: The openai-python library support for Azure OpenAI is in preview.
import time
import logging
import openai

from .settings import *
from .role import Role

logger = logging.Logger(__name__, logging.INFO)

# logger.addHandler(logging.StreamHandler(sys.stdout))
logfile = settings.get('log', 'logfile', fallback='chat.log')
fileHandler = logging.FileHandler(logfile, encoding='UTF-8')
fileHandler.setFormatter(logging.Formatter())

current_handler = fileHandler
current_session = 'default'
current_count = 0
current_file_content = ''
current_messages = []

logger.addHandler(current_handler)


usage = """\
这是OpenAI的ChatGPT控制台程序，提供与用户的交互界面。
用户可以输入提示词与ChatGPT交互。除了支持正常的提示词输入，它还支持以@字符开始的特殊命令。

目前支持的特殊命令列表:
    @help                        显示帮助信息
    @exit                        退出程序
    @new session <session_name>  创建一个新的会话
    @reset session               重置会话
    @file <file_name>            获取指定文件的内容作为提示语"""


# print(openai.api_key)
# {"role": "assistant", "content": ""},


# completion = openai.chat.completions.create(
#   engine="gpt-35-turbo",
#   # engine="gpt-35-turbo-16k",
#   messages=[
#     {"role": "system", "content": ""},
#     {"role": "user", "content": "请结束现在的对话，并重新开启一个新的对话"}
#   ],
#   temperature=0.7,
#   max_tokens=4000,
#   top_p=1.0,
#   frequency_penalty=0,
#   presence_penalty=0,
#   stop=[]
# )
#


def list_modes():
    # openai.organization = "YOUR_ORG_ID"

    result = openai.Model.list()
    for model in result['data']:
        create_at_tm = time.localtime(model['created_at'])
        update_at_tm = None
        if model.get('update_at'):
            update_at_tm = time.localtime(model['updated_at'])
        if update_at_tm:
            create_at = f"{create_at_tm.tm_year}-{create_at_tm.tm_mon}-{create_at_tm.tm_mday}/{update_at_tm.tm_year}-{update_at_tm.tm_mon}-{update_at_tm.tm_mday}"
        else:
            create_at = f"{create_at_tm.tm_year}-{create_at_tm.tm_mon}-{create_at_tm.tm_mday}"

        capabilities = model['capabilities']
        capabilities_str = [capability for capability, value in capabilities.items() if value]

        print(create_at + "\t", model['id'] + "\t\t", capabilities_str)
    # print(result)


def handler_cmd(cmd):
    global current_session
    global current_count
    global current_file_content
    global current_messages

    if cmd.lower() == 'exit':
        return False
    elif cmd.startswith("new session"):
        current_session = cmd[11:].strip()
        current_count = 0
    # elif cmd.startswith('ansicon'):
    #     if ansicon.loaded():
    #         ansicon.unload()
    #         print('Unload ansicon')
    #     else:
    #         ansicon.load()
    #         print('Load ansicon')
    elif cmd.startswith('help'):
        print(usage)
    elif cmd.startswith('file '):
        try:
            with open(cmd[5:].strip(), encoding='UTF-8') as f:
                while True:
                    text = f.read(8192)
                    if text:
                        current_file_content += text
                    else:
                        break
            # print(current_file_content)
        except FileNotFoundError as ex:
            print(ex)
        except Exception as ex:
            print(ex)
    elif cmd.startswith('reset session'):
        current_messages.clear()
        print('Reset Session')
    else:
        print(f'Not supported command: {cmd}')
        print(f'Please use @help command for help.')
    return True


def text_ui_with_context():
    global current_count
    global current_file_content
    global current_messages

    model = "gpt-35-turbo-16k"
    include_history_count = 8

    running = True
    while running:
        if not current_file_content:
            try:
                content = input(f'\033[32;1m[{current_session}]\U0001f47bUser>\033[0m')
            except KeyboardInterrupt:
                break
            logger.info(f'[{current_session}]User>{content}')
            content = content.strip()
            if content.startswith("@"):
                running = handler_cmd(content[1:])
                content = ''

        content = current_file_content or content
        if content:
            current_messages.append(Role.user.message(content))
            completion = client.chat.completions.create(model=model, messages=current_messages[-include_history_count:])
            answer = completion.choices[0].message.content
            current_count += 1
            total_tokens = completion.usage.total_tokens
            print(f'\033[34;1m[{current_session}]\U0001f47dAssistant[{current_count}]({total_tokens})>\n{answer}\033[0m')
            logger.info(f'[{current_session}]Assistant[{current_count}]({total_tokens})> \n{answer}')
            current_messages.append(Role.user.message(answer))

            if len(current_messages) > include_history_count:
                current_messages = current_messages[-include_history_count:]

        current_file_content = ''
