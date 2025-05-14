import gc
from typing import List
import os

from transformers import Qwen2Tokenizer, Qwen2ForCausalLM
import torch

from agents.base_agent import BaseAgent
from utils.logger import logger


class QwenAgent(BaseAgent):

    def __init__(self, model_name:str):
        super().__init__()
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def __call__(self, user_prompt, system_prompt="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(**model_inputs, max_new_tokens=1024)
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]   

    def open(self) -> None:
        logger.info(f"Loading Qwen model {self.model_name}...")
        self.model = Qwen2ForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )
        self.tokenizer = Qwen2Tokenizer.from_pretrained(self.model_name)
        logger.info(f"Qwen model {self.model_name} loaded successfully.")

    def close(self) -> None:
        logger.info(f"Unloading Qwen model {self.model_name}...")
        self.model = self.model.cpu()
        del self.model
        del self.tokenizer
        gc.collect()
        torch.cuda.empty_cache()


class QwenCodebaseQAAgent(BaseAgent):

    def __init__(self, qwen_agent:QwenAgent):
        super().__init__()
        self.qwen_agent = qwen_agent
    
    def __call__(self, question, relevant_code:List[str], system_prompt="You are Qwen. You need to answer the question based on the reterived relevant code in a codebase.") -> str:
        user_prompt = f'Question: {question}'
        if relevant_code:
            user_prompt += "\nRelevant code: "
        for i,code in enumerate(relevant_code):
            user_prompt += f'\nCode {i+1}: \n```\n{code}\n```'

        answer = self.qwen_agent(user_prompt, system_prompt)
        return user_prompt, answer
    
    def open(self) -> None:
        pass

    def close(self) -> None:
        pass
    
class QwenCodebaseSystemDesignAgent(BaseAgent):

    def __init__(self, qwen_agent:QwenAgent):
        super().__init__()
        self.qwen_agent = qwen_agent
    
    def __call__(self, question, tree, relevant_code:List[str], system_prompt="You are Qwen. You need to design the system based on the codebase tree structure, relevant code and question.") -> str:
        user_prompt = f'Codebase tree structure:```\n{tree}\n```\nQuestion: {question}'
        if relevant_code:
            user_prompt += "\nRelevant code: "
        for i,code in enumerate(relevant_code):
            user_prompt += f'\nCode {i+1}: \n```\n{code}\n```'

        answer = self.qwen_agent(user_prompt, system_prompt)
        return user_prompt, answer
    
    def open(self) -> None:
        pass

    def close(self) -> None:
        pass