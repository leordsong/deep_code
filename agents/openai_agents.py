import json
from typing import Optional, List

from openai import OpenAI

from agents.base_agent import BaseAgent
from utils.openai_api import build_single_round_messages, reasoning_streaming_decode
from utils.logger import logger


class ChatOpenAIAgent(BaseAgent):

    def __init__(self, api_key:str, model:str, temperature:float, reasoning:bool, base_url:Optional[str]=None):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.reasoning = reasoning
        self.temperature = temperature
        self.base_url = base_url

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


class JsonResponseOpenAIAgent(BaseAgent):

    def __init__(self, api_key:str, model:str, temperature:float, reasoning:bool, base_url:Optional[str]=None, json_retries:int=1):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.reasoning = reasoning
        self.temperature = temperature
        self.base_url = base_url
        self.json_retries = json_retries

    def forward(self, system_prompt, user_prompt) -> str:
        messages = build_single_round_messages(user_prompt, system_prompt)

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            stream=self.reasoning,
            temperature=self.temperature,
            response_format={
                'type': 'json_object'
            } if not self.reasoning else None,
        )

        if self.reasoning:
            output, _ = reasoning_streaming_decode(chat_completion)
        else:
            output = chat_completion.choices[0].message.content
            return output

    def __call__(self, system_prompt, user_prompt) -> str:
        original_temperature = self.temperature
        temp = 0
        i = 0
        while i < self.json_retries and original_temperature >= temp:
            self.temperature = original_temperature - temp
            try:
                output = self.forward(system_prompt, user_prompt)
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

    def open(self) -> None:
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=self.api_key,
            base_url=self.base_url
        )

    def close(self) -> None:
        self.client.close()

class OpenAICodebaseQAAgent(ChatOpenAIAgent):
    
    def __call__(self, question, relevant_code:List[str], system_prompt="You are Qwen. You need to answer the question based on the reterived relevant code in a codebase.") -> str:
        user_prompt = f'Question: {question}\nRelevant code: '
        for i,code in enumerate(relevant_code):
            user_prompt += f'\nCode {i+1}: ```\n{code}\n```'

        answer = super().__call__(user_prompt, system_prompt)
        return user_prompt, answer