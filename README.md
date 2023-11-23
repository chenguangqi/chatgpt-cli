# ChatGPT CLI by OpenAI Python Library

The OpenAI Python library provides convenient access to the OpenAI API
from applications written in the Python language. It includes a
pre-defined set of classes for API resources that initialize
themselves dynamically from API responses which makes it compatible
with a wide range of versions of the OpenAI API.

You can find usage examples for the OpenAI Python library in our [API reference](https://platform.openai.com/docs/api-reference?lang=python) and the [OpenAI Cookbook](https://github.com/openai/openai-cookbook/).

## Installation

To start, ensure you have Python 3.7.1 or newer. If you just
want to use the package, run:

```sh
pip install --upgrade chatgpt-cli
```

### Command-line interface

This library additionally provides an `openai` command-line utility
which makes it easy to interact with the API from your terminal. Run
`openai api -h` for usage.

```sh
# list models
openai api models.list

# create a chat completion (gpt-3.5-turbo, gpt-4, etc.)
openai api chat_completions.create -m gpt-3.5-turbo -g user "Hello world"

# create a completion (text-davinci-003, text-davinci-002, ada, babbage, curie, davinci, etc.)
openai api completions.create -m ada -p "Hello world"

# generate images via DALL·E API
openai api image.create -p "two dogs playing chess, cartoon" -n 1

# using openai through a proxy
openai --proxy=http://proxy.com api models.list
```

#### openai-robot
```sh
openai-robot --help
```

### Microsoft Azure Endpoints

In order to use the library with Microsoft Azure endpoints, you need to set the `api_type`, `api_base` and `api_version` in addition to the `api_key`. The `api_type` must be set to 'azure' and the others correspond to the properties of your endpoint.
In addition, the deployment name must be passed as the `deployment_id` parameter.

```python
import openai
openai.api_type = "azure"
openai.api_key = "..."
openai.api_base = "https://example-endpoint.openai.azure.com"
openai.api_version = "2023-05-15"

# create a chat completion
chat_completion = openai.ChatCompletion.create(deployment_id="deployment-name", model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])

# print the completion
print(chat_completion.choices[0].message.content)
```

Please note that for the moment, the Microsoft Azure endpoints can only be used for completion, embedding, and fine-tuning operations.
For a detailed example of how to use fine-tuning and other operations using Azure endpoints, please check out the following Jupyter notebooks:

- [Using Azure completions](https://github.com/openai/openai-cookbook/tree/main/examples/azure/completions.ipynb)
- [Using Azure chat](https://github.com/openai/openai-cookbook/tree/main/examples/azure/chat.ipynb)
- [Using Azure embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/azure/embeddings.ipynb)

