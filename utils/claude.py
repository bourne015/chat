import anthropic
import tiktoken
from retry import retry

from core.config import settings
from .credit import Credit
from utils import log


log = log.Logger(__name__, clevel=log.logging.DEBUG)

class Claude:
    '''
    wrapper claude api
    '''
    supported_models = [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
            "claude-3-5-sonnet-20240620",
    ]

    def __init__(self) -> None:
        self.model = self.supported_models[0]
        self.client = anthropic.Anthropic(api_key=settings.claude_key)
        self.credit = Credit()
        print("claude init: ", self.model)

    @retry(tries=3, delay=1, backoff=1)
    def ask(self, user_id, prompt, model, stream = False):
        '''
        question without context
        '''
        if model not in self.supported_models:
            model = self.supported_models[0]

        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            stream=stream
        )

        input_tokens = output_tokens = 0
        if getattr(response, 'usage', None):
            input_tokens = getattr(response.usage, 'input_tokens', 0)
            output_tokens = getattr(response.usage, 'output_tokens', 0)
        self.credit.from_tokens(
                user_id, model, input_tokens, output_tokens)
        return response.content[0].text

    @retry(tries=3, delay=1, backoff=1)
    def asks(self, user_id, prompt_list, model, stream = True):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        if model not in self.supported_models:
            model = self.supported_models[1]

        input_tokens = output_tokens = 0
        with self.client.messages.stream(
            model=model,
            messages=prompt_list,
            max_tokens=4096,
        ) as stream:
            for text in stream.text_stream:
                yield text

        message = stream.get_final_message()
        if getattr(message, 'usage', None):
            input_tokens = getattr(message.usage, 'input_tokens', 0)
            output_tokens = getattr(message.usage, 'output_tokens', 0)
        self.credit.from_tokens(user_id, model, input_tokens, output_tokens)

    @retry(tries=3, delay=1, backoff=1)
    def completions(self, user_id, chat_completion):
        '''
        question with context
        prompt_list store a session of prompts and answers
        '''
        model = chat_completion.model
        system_prompt = "you are a helpful assistant"
        if chat_completion.messages[0]['role'] == "system":
            chat_completion.messages[0]['role'] = 'user'
            if chat_completion.messages[0]['content'] is list:
                system_prompt = chat_completion.messages[0]['content'][0]['text']
                chat_completion.messages[0]['content'][0]['text'] = '你好'
            else:
                system_prompt = chat_completion.messages[0]['content']
                chat_completion.messages[0]['content'] = '你好'
            # chat_completion.messages.pop(0)
        messages = chat_completion.messages
        tools = chat_completion.tools
        stream = True
        if model not in self.supported_models:
            model = self.supported_models[1]

        input_tokens = output_tokens = 0
        # with self.client.messages.stream(
        resp = self.client.messages.create(
            model=model,
            messages=messages,
            system=system_prompt,
            tools=tools,
            max_tokens=4096,
            stream=stream,
            )
        for x in resp:
            if getattr(x, 'usage', None):
                input_tokens = getattr(x.usage, 'input_tokens', 0)
                output_tokens = getattr(x.usage, 'output_tokens', 0)
                self.credit.from_tokens(user_id, model, input_tokens, output_tokens)
            yield x.model_dump_json(exclude_unset=True)
        #as stream:
        #    for chunk in stream:
        #        yield chunk.model_dump_json(exclude_unset=True)

        #message = stream.get_final_message()
        #if getattr(message, 'usage', None):
        #    input_tokens = getattr(message.usage, 'input_tokens', 0)
        #    output_tokens = getattr(message.usage, 'output_tokens', 0)
        #self.credit.from_tokens(user_id, model, input_tokens, output_tokens)
 

    def num_tokens_from_messages(self, messages, model="claude-3-haiku-20240307"):
        """
        Return the number of tokens used by a list of messages.
        use gpt tokens num temporarily
        """
        try:
            fakeModel = "gpt-4" # use GPT for this moment
            encoding = tiktoken.encoding_for_model(fakeModel)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
            "claude-3-5-sonnet-20240620",
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
