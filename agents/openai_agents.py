import json
from typing import Optional

from openai import OpenAI

from agents.base_agent import BaseAgent
from utils.openai_api import build_single_round_messages, reasoning_streaming_decode, _MODELS, _REASONING_MODELS
from utils.logger import logger


class ChatOpenAIAgent(BaseAgent):

    def __init__(self, api_key:str, model:str, temperature:float, base_url=None):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or _MODELS.get(model, None)
        assert self.base_url is not None, f"Please specify the base_url for model {model}"
        self.temperature = temperature
        self.reasoning = model in _REASONING_MODELS

    def __call__(self, system_prompt, user_prompt) -> str:
        messages = build_single_round_messages(user_prompt, system_prompt)

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            stream=self.reasoning,
            temperature=self.temperature,
        )

        if self.reasoning:
            output, _ = reasoning_streaming_decode(chat_completion)
        else:
            output = chat_completion.choices[0].message.content
            return output

    def open(self) -> None:
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=self.api_key,
            base_url=self.base_url
        )

    def close(self) -> None:
        self.client.close()


class JsonChatOpenAIAgent(ChatOpenAIAgent):

    def __init__(self, api_key:str, model:str, temperature:float, base_url=None, json_retries:int=1):
        super().__init__(api_key, model, temperature, base_url)
        self.json_retries = json_retries

    def __call__(self, system_prompt, user_prompt) -> str:
        original_temperature = self.temperature
        temp = 0
        i = 0
        while i < self.json_retries and original_temperature >= temp:
            self.temperature = original_temperature - temp
            try:
                output = super().__call__(system_prompt, user_prompt)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error, retrying {i+1}/{self.json_retries}...")
                if i == self.json_retries - 1:
                    raise e
                else:
                    i += 1
                    temp += 0.1
            finally:
                self.temperature = original_temperature
        return output

