from openai import AsyncOpenAI
import tiktoken
from retry import retry

from core.config import settings
from .credit import Credit
from utils import log


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class GPT:
    '''
    wrapper openai api
    '''
    supported_models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo-1106",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "dall-e-3"
    ]

    def __init__(self) -> None:
        self.model = self.supported_models[0]
        self.client = AsyncOpenAI(api_key=settings.openai_key)
        self.credit = Credit()
        print("Chat init: ", self.model)

    @retry(tries=3, delay=1, backoff=1)
    async def ask(self, user_id, question, model, stream = False):
        '''
        question without context
        '''
        if model not in self.supported_models:
            model = self.supported_models[0]

        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            stream=stream
        )

        input_tokens = output_tokens = 0
        if getattr(response, 'usage', None):
            input_tokens = getattr(response.usage, 'prompt_tokens', 0)
            output_tokens = getattr(response.usage, 'completion_tokens', 0)
        self.credit.from_tokens(
                user_id, model, input_tokens, output_tokens)
        return response.choices[0].message.content

    @retry(tries=3, delay=1, backoff=1)
    async def completions(self, user_id, chat_completion):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        model = chat_completion.model
        messages = chat_completion.messages
        tools = chat_completion.tools
        stream = True
        # if model not in self.supported_models:
        #     model = self.supported_models[1]

        input_tokens = output_tokens = 0
        params = {
            "model": model,
            "messages": messages,
            # "max_completion_tokens": 4096,
            "stream_options": {"include_usage": True},
            "stream": stream
        }
        if tools and model != "o1-mini":
            params["tools"] = tools
        if (chat_completion.temperature != None and
            0 <= chat_completion.temperature <= 2.0 and
            not model.startswith("o")):
            # greater than 1.2 will generate random characters
            params["temperature"] = min(chat_completion.temperature, 1.15)
            log.debug(f"\033[31mtemperature: {chat_completion.temperature}\033[0m")
        response = await self.client.chat.completions.create(**params)
        async for chunk in response:
            if not chunk.choices and getattr(chunk, 'usage', None):
                input_tokens = chunk.usage.prompt_tokens
                output_tokens = chunk.usage.completion_tokens
            yield chunk.model_dump_json(exclude_unset=True)
        self.credit.from_tokens(user_id, model, input_tokens, output_tokens)


    async def gen_image(self, user_id, prompt, model = 'dall-e-3'):
        """
        generate image
        DALL·E 3  Standard 1024*1024 = $0.040 / image
        """
        response = await self.client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            response_format='b64_json',
            n=1)

        self.credit.from_costs(user_id, 0.04)
        return response

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """
        Return the number of tokens used by a list of messages.
        """
        try:
            mencode = "gpt-4-turbo" if model == "gpt-4o" else model
            encoding = tiktoken.encoding_for_model(mencode)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            "gpt-4-turbo",
            "gpt-4o",
            "dall-e-3",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            # type: 0 text, 1 image, 2 file(file is the same with text)
            if message["type"] == 1:
                if message["role"] == "assistant":
                    # DALL·E 3  Standard 1024×1024 $0.040 / image
                    # fixed to 4000 tokens,then $0.010 / 1k token
                    num_tokens += 4000
                else:
                    # a input image fixed to 765 tokens: https://openai.com/pricing
                    num_tokens += 765
                    # in vision case, content is a list
                    num_tokens += len(encoding.encode(message["content"]))
                continue
            for key, value in message.items():
                if key in ["role", "name", "content"]: # since message have other key for db
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
